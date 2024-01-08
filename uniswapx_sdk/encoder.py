from dataclasses import (
    asdict,
    astuple,
    dataclass,
)
from random import randint
import time
from typing import (
    Any,
    Dict,
    Sequence,
    Tuple,
    Union,
)

from eth_abi import encode
from eth_account.messages import (
    encode_typed_data,
    SignableMessage,
)
from web3 import Web3
from web3.types import (
    ChecksumAddress,
    HexStr,
)

from uniswapx_sdk.constants import (
    _execute_function_selector,
    exclusive_dutch_order_abi,
    exclusive_dutch_order_types,
    permit2_domain_data,
)


@dataclass
class ExclusiveDutchOrderInfo:
    reactor: Union[ChecksumAddress, HexStr, str, bytes]
    swapper: Union[ChecksumAddress, HexStr, str, bytes]
    nonce: int
    deadline: int
    validation_callback: Union[HexStr, ChecksumAddress, str] = "0x0000000000000000000000000000000000000000"
    validation_data: bytes = b""

    def __post_init__(self) -> None:
        self.reactor = Web3.to_checksum_address(self.reactor)
        self.swapper = Web3.to_checksum_address(self.swapper)
        self.validation_callback = Web3.to_checksum_address(self.validation_callback)


@dataclass
class ExclusiveDutchOrderInput:
    token: Union[ChecksumAddress, HexStr, str, bytes]
    start_amount: int
    end_amount: int

    def __post_init__(self) -> None:
        self.token = Web3.to_checksum_address(self.token)


@dataclass
class ExclusiveDutchOrderOutput(ExclusiveDutchOrderInput):
    recipient: Union[ChecksumAddress, HexStr, str, bytes]

    def __post_init__(self) -> None:
        super().__post_init__()
        self.recipient = Web3.to_checksum_address(self.recipient)


@dataclass(frozen=True)
class DecayTime:
    decay_start_time: int
    decay_end_time: int


@dataclass
class ExclusiveFiller:
    filler: Union[ChecksumAddress, HexStr, str, bytes] = "0x0000000000000000000000000000000000000000"
    override_bps: int = 0

    def __post_init__(self) -> None:
        self.filler = Web3.to_checksum_address(self.filler)


def get_deadline(duration: int = 10 * 60) -> int:
    """
    get deadline or expiration. Default is 10mn
    :param duration: The number of seconds before reaching the deadline/expiration
    :return: Unix timestamp corresponding to now + duration
    """
    return int(time.time() + duration)


def get_nonce() -> int:
    """
    :return: nonce used to build orders
    """
    return time.time_ns() * 10**58 + randint(10**57, 10**58-1)


class Encoder:
    def __init__(self, chain_id: int, order_abi: Sequence[str]) -> None:
        self.chain_id = chain_id
        self.order_abi = order_abi

    def encode(self, args: Sequence[Any]) -> bytes:
        return encode(self.order_abi, args)

    def create_signable_message(self, message_types: Dict[str, Any], message_data: Dict[str, Any]) -> SignableMessage:
        domain_data = dict(permit2_domain_data)
        domain_data["chainId"] = self.chain_id
        return encode_typed_data(
            domain_data=domain_data,
            message_types=message_types,
            message_data=message_data
        )

    @staticmethod
    def encode_execute(order: bytes, sig: bytes) -> HexStr:
        """
        Encode the input data to include in the transactions sent to the reactors.
        :param order: the encoded order
        :param sig: the signature (so the SignableMessage after being signed)
        :return: The encoded input data
        """
        return HexStr(_execute_function_selector + encode(('(bytes,bytes)', ), ((order, sig), )).hex())


class ExclusiveDutchOrderEncoder(Encoder):
    def __init__(self, chain_id: int) -> None:
        super().__init__(chain_id, exclusive_dutch_order_abi)

    @staticmethod
    def _create_args(
            order_info: ExclusiveDutchOrderInfo,
            decay_time: DecayTime,
            dutch_input: ExclusiveDutchOrderInput,
            dutch_outputs: Tuple[ExclusiveDutchOrderOutput, ...],
            exclusive_filler: ExclusiveFiller) -> Tuple[Any, ...]:
        args = [astuple(order_info)]
        args.extend(astuple(decay_time))
        args.extend(astuple(exclusive_filler))
        args.append(astuple(dutch_input))
        args.append(tuple(map(lambda dutch_output: astuple(dutch_output), dutch_outputs)))
        return tuple(args)

    def encode_order(
            self,
            order_info: ExclusiveDutchOrderInfo,
            decay_time: DecayTime,
            dutch_input: ExclusiveDutchOrderInput,
            dutch_outputs: Tuple[ExclusiveDutchOrderOutput, ...],
            exclusive_filler: ExclusiveFiller = ExclusiveFiller()) -> Tuple[bytes, SignableMessage]:
        """
        Encode the order and create the signable message to be signed.
        :param order_info: a valid instance of ExclusiveDutchOrderInfo
        :param decay_time: a valid instance of DecayTime
        :param dutch_input: a valid instance of ExclusiveDutchOrderInput
        :param dutch_outputs: a valid instance of Tuple[ExclusiveDutchOrderOutput, ...]
        :param exclusive_filler: a valid instance of ExclusiveFiller
        :return: the encoded order as bytes and a SignableMessage ready to be signed
        """
        args = self._create_args(order_info, decay_time, dutch_input, dutch_outputs, exclusive_filler)
        encoded_order = self.encode([args, ])
        message = self._create_signable_message(order_info, decay_time, dutch_input, dutch_outputs, exclusive_filler)
        return encoded_order, message

    @staticmethod
    def _create_message_data(
            order_info: ExclusiveDutchOrderInfo,
            decay_time: DecayTime,
            dutch_input: ExclusiveDutchOrderInput,
            dutch_outputs: Tuple[ExclusiveDutchOrderOutput, ...],
            exclusive_filler: ExclusiveFiller) -> Dict[str, Any]:

        order_info_data = asdict(order_info)
        order_info_data["additionalValidationContract"] = order_info_data.pop("validation_callback")
        order_info_data["additionalValidationData"] = order_info_data.pop("validation_data")

        outputs = []
        for output in dutch_outputs:
            output_data = asdict(output)
            output_data["startAmount"] = output_data.pop("start_amount")
            output_data["endAmount"] = output_data.pop("end_amount")
            outputs.append(output_data)

        return {
            "info": order_info_data,
            "decayStartTime": decay_time.decay_start_time,
            "decayEndTime": decay_time.decay_end_time,
            "exclusiveFiller": exclusive_filler.filler,
            "exclusivityOverrideBps": exclusive_filler.override_bps,
            "inputToken": dutch_input.token,
            "inputStartAmount": dutch_input.start_amount,
            "inputEndAmount": dutch_input.end_amount,
            "outputs": outputs,
        }

    def _create_signable_message(
            self,
            order_info: ExclusiveDutchOrderInfo,
            decay_time: DecayTime,
            dutch_input: ExclusiveDutchOrderInput,
            dutch_outputs: Tuple[ExclusiveDutchOrderOutput, ...],
            exclusive_filler: ExclusiveFiller = ExclusiveFiller()) -> SignableMessage:
        witness_data = self._create_message_data(order_info, decay_time, dutch_input, dutch_outputs, exclusive_filler)
        message_data = {
            "permitted": {
                'token': dutch_input.token,
                'amount': dutch_input.end_amount,
            },
            "spender": order_info.reactor,
            "nonce": order_info.nonce,
            "deadline": order_info.deadline,
            "witness": witness_data
        }
        return self.create_signable_message(exclusive_dutch_order_types, message_data)

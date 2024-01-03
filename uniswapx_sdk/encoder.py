from dataclasses import (
    astuple,
    dataclass,
)
from typing import (
    Any,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from eth_abi import encode
from web3 import Web3
from web3.types import (
    ChecksumAddress,
    HexStr,
)

from uniswapx_sdk.constants import exclusive_dutch_order_abi


@dataclass
class ExclusiveDutchOrderInfo:
    reactor: Union[HexStr, ChecksumAddress]
    swapper: Union[HexStr, ChecksumAddress]
    nonce: int
    deadline: int
    validation_callback: Union[HexStr, ChecksumAddress] = HexStr("0x0000000000000000000000000000000000000000")
    validation_data: bytes = b""

    def __post_init__(self) -> None:
        self.reactor = Web3.to_checksum_address(self.reactor)
        self.swapper = Web3.to_checksum_address(self.swapper)
        self.validation_callback = Web3.to_checksum_address(self.validation_callback)


@dataclass
class ExclusiveDutchOrderInput:
    token: Union[HexStr, ChecksumAddress]
    start_amount: int
    end_amount: int

    def __post_init__(self) -> None:
        self.token = Web3.to_checksum_address(self.token)


@dataclass
class ExclusiveDutchOrderOutput(ExclusiveDutchOrderInput):
    recipient: Union[HexStr, ChecksumAddress]

    def __post_init__(self) -> None:
        super().__post_init__()
        self.recipient = Web3.to_checksum_address(self.recipient)


@dataclass(frozen=True)
class DecayTime:
    decay_start_time: int
    decay_end_time: int


@dataclass
class ExclusiveFiller:
    filler: Union[HexStr, ChecksumAddress]
    override_bps: int

    def __post_init__(self) -> None:
        self.filler = Web3.to_checksum_address(self.filler)


class _Encoder:
    def __init__(self, abi: Sequence[str]) -> None:
        self.abi = abi

    def _encode(self, args: Sequence[Any]) -> bytes:
        return encode(self.abi, args)


class Encoder(_Encoder):
    def __init__(self, abi: Sequence[str]) -> None:
        super().__init__(abi)


class ExclusiveDutchOrderEncoder(Encoder):
    def __init__(self) -> None:
        super().__init__(exclusive_dutch_order_abi)

    @staticmethod
    def _create_args(
            order_info: ExclusiveDutchOrderInfo,
            decay_time: DecayTime,
            dutch_input: ExclusiveDutchOrderInput,
            dutch_outputs: Tuple[ExclusiveDutchOrderOutput, ...],
            exclusive_filler: Optional[ExclusiveFiller] = None) -> Tuple[Any, ...]:
        args = [astuple(order_info)]
        args.extend(astuple(decay_time))
        if exclusive_filler:
            args.extend(astuple(exclusive_filler))
        args.append(astuple(dutch_input))
        args.append(tuple(map(lambda dutch_output: astuple(dutch_output), dutch_outputs)))
        return tuple(args)

    def encode(
            self,
            order_info: ExclusiveDutchOrderInfo,
            decay_time: DecayTime,
            dutch_input: ExclusiveDutchOrderInput,
            dutch_outputs: Tuple[ExclusiveDutchOrderOutput, ...],
            exclusive_filler: Optional[ExclusiveFiller] = None) -> bytes:
        args = self._create_args(order_info, decay_time, dutch_input, dutch_outputs, exclusive_filler)
        return self._encode([args, ])

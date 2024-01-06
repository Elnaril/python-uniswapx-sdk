from typing import (
    Any,
    Optional,
    Tuple,
    Union,
)

from web3 import (
    AsyncHTTPProvider,
    AsyncWeb3,
)
from web3.exceptions import (
    ContractCustomError,
    ContractLogicError,
)
from web3.types import (
    BlockIdentifier,
    ChecksumAddress,
    HexBytes,
    HexStr,
)

from uniswapx_sdk.constants import (
    order_quoter_abi,
    order_quoters,
)
from uniswapx_sdk.exceptions import (
    order_validation_exceptions,
    OrderValidationError,
)


class OrderResolver:
    def __init__(self,  w3: AsyncWeb3, chain_id: int, quoter_address: ChecksumAddress) -> None:
        self._w3 = w3
        self._chain_id = chain_id
        self._quoter = self._w3.eth.contract(address=quoter_address, abi=order_quoter_abi)

    @classmethod
    async def create(
            cls,
            w3: Optional[AsyncWeb3] = None,
            rpc_endpoint: Optional[str] = None) -> "OrderResolver":
        """
        Create an OrderResolver instance which is used to validate and quote UniswapX signed orders.

        :param w3: a valid AsyncWeb3 instance (if no rpc endpoint is given)
        :param rpc_endpoint: an rpc endpoint address (if no w3 instance is given)
        :return: an OrderResolver instance
        """
        _w3 = cls._get_w3(rpc_endpoint, w3)
        chain_id = await _w3.eth.chain_id
        return cls(_w3, chain_id, order_quoters[chain_id])

    @staticmethod
    def _get_w3(rpc_endpoint: Optional[str], w3: Optional[AsyncWeb3]) -> AsyncWeb3:
        if w3:
            return w3
        elif rpc_endpoint:
            return AsyncWeb3(AsyncHTTPProvider(rpc_endpoint))
        else:
            raise ValueError("Invalid parameters. Must provide either an AsyncWeb3 instance or a valid rpc address")

    async def resolve(
            self,
            encoded_order: Union[HexStr, HexBytes],
            signature: Union[HexStr, HexBytes],
            block_identifier: BlockIdentifier = "latest") -> Tuple[Any, ...]:
        """
        Return the resolved order or raise an OrderValidationError
        :param encoded_order: the first parameter of a signed order sent to a reactor's execution function
        :param signature: the second parameter of a signed order sent to a reactor's execution function
        :param block_identifier: Optional block number or string identifier. Default to 'latest'.
        :return: the resolved order
        """
        try:
            resolved_order: Tuple[Any, ...] = (
                await self._quoter.functions.quote(encoded_order, signature).call(block_identifier=block_identifier)
            )
            return resolved_order
        except ContractCustomError as e:
            ExceptionClass = order_validation_exceptions.get(e.message, OrderValidationError)
            raise ExceptionClass(message=e.message, data=e.data)
        except ContractLogicError as e:
            if e.message and "TRANSFER_FROM_FAILED" in e.message:
                ExceptionClass = order_validation_exceptions.get("TRANSFER_FROM_FAILED", OrderValidationError)
                raise ExceptionClass(message=e.message, data=e.data)
            else:
                raise

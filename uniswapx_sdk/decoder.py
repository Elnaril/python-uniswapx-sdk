from typing import (
    Any,
    Sequence,
    Tuple,
    Union,
)

from eth_abi import decode
from eth_utils import to_bytes
from web3.types import (
    HexBytes,
    HexStr,
)

from uniswapx_sdk.constants import exclusive_dutch_order_abi


class _Decoder:
    def __init__(self, abi: Sequence[str]) -> None:
        self.abi = abi

    def decode(self, encoded_order: Union[HexStr, HexBytes]) -> Tuple[Any, ...]:
        order = encoded_order.hex() if isinstance(encoded_order, bytes) else encoded_order
        data = to_bytes(hexstr=order)
        return decode(self.abi, data)


class Decoder(_Decoder):
    def __init__(self, abi: Sequence[str]) -> None:
        super().__init__(abi)


class ExclusiveDutchOrderDecoder(Decoder):
    def __init__(self) -> None:
        super().__init__(exclusive_dutch_order_abi)

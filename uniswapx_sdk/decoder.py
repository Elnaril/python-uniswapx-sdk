from typing import (
    Any,
    Iterable,
    Tuple,
    Union,
)

from eth_abi import decode
from eth_utils import to_bytes
from web3.types import (
    HexBytes,
    HexStr,
)


class _Decoder:
    def __init__(self, abi: Iterable[str]) -> None:
        self.abi = abi

    def decode(self, encoded_order: Union[HexStr, HexBytes]) -> Tuple[Any, ...]:
        order = encoded_order.hex() if isinstance(encoded_order, bytes) else encoded_order
        data = to_bytes(hexstr=order)
        return decode(self.abi, data)


class Decoder(_Decoder):
    def __init__(self, abi: Iterable[str]) -> None:
        super().__init__(abi)


class ExclusiveDutchOrderDecoder(_Decoder):
    def __init__(self) -> None:
        abi = ['((address,address,uint256,uint256,address,bytes),uint256,uint256,address,uint256,(address,uint256,uint256),(address,uint256,uint256,address)[])']  # noqa
        super().__init__(abi)

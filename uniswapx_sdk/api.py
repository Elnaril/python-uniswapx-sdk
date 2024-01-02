from typing import (
    Any,
    cast,
    Dict,
    Optional,
)

from aiohttp import ClientSession

from uniswapx_sdk.constants import uniswapx_orders_endpoint


class UniswapXAPI:
    def __init__(self, chain_id: int) -> None:
        self.chain_id = chain_id

    @staticmethod
    async def _get_orders(session: ClientSession, **params: str) -> Dict[str, Any]:
        async with session.get(url=uniswapx_orders_endpoint, params=params) as response:
            return cast(Dict[str, Any], await response.json())

    async def get_orders(
            self,
            order_status: str = "open",
            limit: int = 10,
            session: Optional[ClientSession] = None,
            **kwargs: str) -> Dict[str, Any]:
        """
        Get orders from UniswapX API (https://api.uniswap.org/v2/orders)
        :param order_status: one of the following str: open, expired, error, cancelled, filled, insufficient-funds
        :param limit: result max count
        :param session: optional. A valid aiohttp.ClientSession instance
        :param kwargs: other possible parameters as describe here: https://api.uniswap.org/v2/uniswapx/docs
        :return: The list of corresponding orders
        """
        params = kwargs.copy()
        params.update({"chainId": str(self.chain_id), "orderStatus": order_status, "limit": str(limit)})
        if session:
            return await self._get_orders(session, **params)
        else:
            async with ClientSession() as client_session:
                return await self._get_orders(client_session, **params)

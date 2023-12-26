import os

from eth_utils import to_bytes
import pytest
from web3.types import HexStr

from uniswapx_sdk.exceptions import order_validation_exceptions
from uniswapx_sdk.resolver import OrderResolver


encoded_order_1 = HexStr("0x0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000658809c90000000000000000000000000000000000000000000000000000000065880a050000000000000000000000002008b6c3d07b061a84f790c035c2f6dc11a0be700000000000000000000000000000000000000000000000000000000000000064000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec7000000000000000000000000000000000000000000000000000000006c5274a2000000000000000000000000000000000000000000000000000000006c5274a200000000000000000000000000000000000000000000000000000000000002000000000000000000000000006000da47483062a0d734ba3dc7576ce6a0b645c4000000000000000000000000033f50fdfce0dfb6aadbca89221d002b003436dd046832f6e4287ab217c8b0c0301573edcef40afca419cc0b9902b6cea83219000000000000000000000000000000000000000000000000000000000065880a11000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc20000000000000000000000000000000000000000000000000af7af81daf163570000000000000000000000000000000000000000000000000ace07c1c27dfa28000000000000000000000000033f50fdfce0dfb6aadbca89221d002b003436dd000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2000000000000000000000000000000000000000000000000000437c55ad5296d000000000000000000000000000000000000000000000000000427c052b845fb00000000000000000000000037a8f295612602f2774d331e562be9e61b83a327")  # noqa
signature_1 = HexStr("0x39c849e3ddfe618036330549c61cbd232dcbfac040fc734ba7903c2019bba5763f4bca563210f4c55b83ccf114a77dd880a5b5de08428e4800633bf1753216751b")  # noqa

encoded_order_2 = HexStr("0x0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000658a8f6600000000000000000000000000000000000000000000000000000000658a8fa200000000000000000000000091afe96ed862cb3a2df3a9f93d118189a06373270000000000000000000000000000000000000000000000000000000000000064000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc200000000000000000000000000000000000000000000000029a2241af62c000000000000000000000000000000000000000000000000000029a2241af62c000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000006000da47483062a0d734ba3dc7576ce6a0b645c40000000000000000000000005b50cbaaaa89c040bd4aa114cda7dfd85f8c2528046832cd60a4376530138a7fbb7169903d3002535ecba46a9f182e695bda6a0000000000000000000000000000000000000000000000000000000000658a8fae000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000000000018ebc726c000000000000000000000000000000000000000000000000000000018c16b6290000000000000000000000005b50cbaaaa89c040bd4aa114cda7dfd85f8c2528000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000000000000000000000000000000000000099583d000000000000000000000000000000000000000000000000000000000098539900000000000000000000000027213e28d7fda5c57fe9e5dd923818dbccf71c47")  # noqa
signature_2 = HexStr("0xa17abf7ccdb9e23aba09e182df23cc07fe1e8fea9fe4db606fc673bfebf6e0cf4f133ca03996730dfa31a272359d267318ba424a7615972be3f62faf46df15141c")  # noqa
resolved_order_2 = (('0x6000da47483062A0D734Ba3dc7576Ce6A0B645C4', '0x5B50CBAaaa89c040bD4Aa114cdA7dfd85f8C2528', 1993354113353958521630686347068058033222319641616315893150254404554163120640, 1703579566, '0x0000000000000000000000000000000000000000', b''), ('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2', 3000000000000000000, 3000000000000000000), [('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 6756578848, '0x5B50CBAaaa89c040bD4Aa114cdA7dfd85f8C2528'), ('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 10150092, '0x27213E28D7fDA5c57Fe9e5dD923818DBCcf71c47')], b'\xa1z\xbf|\xcd\xb9\xe2:\xba\t\xe1\x82\xdf#\xcc\x07\xfe\x1e\x8f\xea\x9f\xe4\xdb`o\xc6s\xbf\xeb\xf6\xe0\xcfO\x13<\xa09\x96s\r\xfa1\xa2r5\x9d&s\x18\xbaBJv\x15\x97+\xe3\xf6/\xafF\xdf\x15\x14\x1c', b'\xaddX\xd6`Q\n;C}`\x90\x92\xc4WHX\x16\xb2mP\xf5\xac\x9c\xad\x04\xfb}1\xca\xe9\xc5')  # noqa

encoded_order_3 = HexStr("0x0000000000000000000000000000000000000000000000000000000000000020000000000000000000000000000000000000000000000000000000000000012000000000000000000000000000000000000000000000000000000000658af6a700000000000000000000000000000000000000000000000000000000658af6e3000000000000000000000000d198fbe60c49d4789525fc54567447518c7d2a110000000000000000000000000000000000000000000000000000000000000064000000000000000000000000514910771af9ca656af840dff83e8264ecf986ca0000000000000000000000000000000000000000000000062030a54ce32400000000000000000000000000000000000000000000000000062030a54ce324000000000000000000000000000000000000000000000000000000000000000002000000000000000000000000006000da47483062a0d734ba3dc7576ce6a0b645c40000000000000000000000000d457fa1f10c51add527b1eff15613789dbb61dd0468328f46ed604513a2bd00587ef15775617978976265018ada7c9dbbb0d20000000000000000000000000000000000000000000000000000000000658af6ef000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001000000000000000000000000dac17f958d2ee523a2206206994597c13d831ec700000000000000000000000000000000000000000000000000000000656a53d80000000000000000000000000000000000000000000000000000000063eac4360000000000000000000000000d457fa1f10c51add527b1eff15613789dbb61dd")  # noqa
signature_3 = HexStr("0x3491fd41f0f3b23b2036e57941b1aef9bfaa8a6d550a4bb14860325db7f21cf6746b1c4fee79e87d46b9b30fa03a6d011250db7543bda9f7c321bcebc838190e1b")  # noqa


@pytest.mark.asyncio(scope="session")
@pytest.mark.parametrize(
    "encoded_order, signature, block_number, expected_resolved_order, expected_exception_cause",
    (
        (encoded_order_1, signature_1, 18868691, None, "0x70f65caa"),
        (encoded_order_2, signature_2, 18868690, resolved_order_2, None),
        (to_bytes(hexstr=encoded_order_2), to_bytes(hexstr=signature_2), 18868690, resolved_order_2, None),
        (encoded_order_2, signature_2, 18868691, resolved_order_2, "0x756688fe"),
        (encoded_order_3, signature_3, 18870876, None, "TRANSFER_FROM_FAILED"),  # swapper does not have enough (approved) LINK  # noqa
    )
)
async def test_resolver(encoded_order, signature, block_number, expected_resolved_order, expected_exception_cause):
    resolver = await OrderResolver.create(rpc_endpoint=os.environ["RPC_ENDPOINT"])
    if expected_exception_cause:
        with pytest.raises(order_validation_exceptions[expected_exception_cause]):
            _ = await resolver.get_quote(encoded_order, signature, block_number)
    else:
        resolved_order = await resolver.get_quote(encoded_order, signature, block_number)
        assert expected_resolved_order == resolved_order

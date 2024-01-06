from eth_utils import keccak
import pytest
from web3 import Account

from uniswapx_sdk.encoder import (
    DecayTime,
    ExclusiveDutchOrderInfo,
    ExclusiveDutchOrderInput,
    ExclusiveDutchOrderOutput,
    ExclusiveFiller,
)


wallet = Account.from_key(keccak(text="moo"))
assert wallet.address == "0xcd7328a5D376D5530f054EAF0B9D235a4Fd36059"


@pytest.fixture
def account():
    return wallet


order_info_4 = ExclusiveDutchOrderInfo(
    reactor="0x6000da47483062a0d734ba3dc7576ce6a0b645c4",
    swapper=wallet.address,
    nonce=17044488556984821651367783140780206339718078492509275355826173425128561760239,
    deadline=1704283964,
)
decay_time_4 = DecayTime(1704283832, 1704283952)
dutch_input_4 = ExclusiveDutchOrderInput('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 11514000000, 11514000000)
dutch_outputs_4 = (
    ExclusiveDutchOrderOutput(
        token='0x0000000000000000000000000000000000000000',
        start_amount=5357273070919632430,
        end_amount=5129553448285053856,
        recipient='0xe7f525dd1bc6d748ae4d7f21d31e54741e05e110',
    ),
    ExclusiveDutchOrderOutput(
        token='0x0000000000000000000000000000000000000000',
        start_amount=8047981578747570,
        end_amount=7705889005936485,
        recipient='0x37a8f295612602f2774d331e562be9e61b83a327',
    ),
)
exclusive_filler_4 = ExclusiveFiller()
order_4 = (
    order_info_4,
    decay_time_4,
    dutch_input_4,
    dutch_outputs_4,
    exclusive_filler_4,
)

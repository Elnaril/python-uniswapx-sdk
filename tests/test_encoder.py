import time

from eth_utils import to_hex
import pytest

from tests.conftest import order_4
from uniswapx_sdk.encoder import (
    DecayTime,
    ExclusiveDutchOrderEncoder,
    ExclusiveDutchOrderInfo,
    ExclusiveDutchOrderInput,
    ExclusiveDutchOrderOutput,
    ExclusiveFiller,
    generate_nonce,
)


# orderHash_1: 0xd1a982a611fc9dcd1230226140f22100994d769b2e01036dd8b3473ded7a3529
order_details_1 = \
    (
        (
            (
                '0x6000da47483062a0d734ba3dc7576ce6a0b645c4',
                '0xe7f525dd1bc6d748ae4d7f21d31e54741e05e110',
                1993350810584104428432150966441163937812467703763408189373898424638421800960,
                1704283964,
                '0x0000000000000000000000000000000000000000',
                b''
            ),
            1704283832,
            1704283952,
            '0x919f9173e2dc833ec708812b4f1cb11b1a17efde',
            100,
            ('0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48', 11514000000, 11514000000),
            (
                (
                    '0x0000000000000000000000000000000000000000',
                    5357273070919632430,
                    5129553448285053856,
                    '0xe7f525dd1bc6d748ae4d7f21d31e54741e05e110'
                ),
                (
                    '0x0000000000000000000000000000000000000000',
                    8047981578747570,
                    7705889005936485,
                    '0x37a8f295612602f2774d331e562be9e61b83a327'
                )
            )
        ),
    )

order_info_1 = ExclusiveDutchOrderInfo(*order_details_1[0][0])
decay_time_1 = DecayTime(order_details_1[0][1], order_details_1[0][2])
dutch_input_1 = ExclusiveDutchOrderInput(*order_details_1[0][5])
dutch_outputs_1 = (ExclusiveDutchOrderOutput(*order_details_1[0][6][0]), ExclusiveDutchOrderOutput(*order_details_1[0][6][1]))  # noqa
exclusive_filler_1 = ExclusiveFiller(to_hex(hexstr=order_details_1[0][3]), order_details_1[0][4])

order_1 = (
    order_info_1,
    decay_time_1,
    dutch_input_1,
    dutch_outputs_1,
    exclusive_filler_1,
)

expected_args_1 = (('0x6000da47483062A0D734Ba3dc7576Ce6A0B645C4', '0xe7f525dd1bc6d748AE4D7F21D31e54741e05e110', 1993350810584104428432150966441163937812467703763408189373898424638421800960, 1704283964, '0x0000000000000000000000000000000000000000', b''), 1704283832, 1704283952, '0x919f9173E2Dc833Ec708812B4f1CB11B1a17eFDe', 100, ('0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', 11514000000, 11514000000), (('0x0000000000000000000000000000000000000000', 5357273070919632430, 5129553448285053856, '0xe7f525dd1bc6d748AE4D7F21D31e54741e05e110'), ('0x0000000000000000000000000000000000000000', 8047981578747570, 7705889005936485, '0x37a8f295612602f2774d331e562be9e61B83a327')))  # noqa
expected_encoded_order_1 = "0x000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000001200000000000000000000000000000000000000000000000000000000065954eb80000000000000000000000000000000000000000000000000000000065954f30000000000000000000000000919f9173e2dc833ec708812b4f1cb11b1a17efde0000000000000000000000000000000000000000000000000000000000000064000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb4800000000000000000000000000000000000000000000000000000002ae49b28000000000000000000000000000000000000000000000000000000002ae49b28000000000000000000000000000000000000000000000000000000000000002000000000000000000000000006000da47483062a0d734ba3dc7576ce6a0b645c4000000000000000000000000e7f525dd1bc6d748ae4d7f21d31e54741e05e11004683252def7714463ae315bbade448e191b5b652150ab5c0bfc7e4ee76b18000000000000000000000000000000000000000000000000000000000065954f3c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000c00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004a58db7954ee462e000000000000000000000000000000000000000000000000472fd5af056923a0000000000000000000000000e7f525dd1bc6d748ae4d7f21d31e54741e05e1100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001c9798bb28feb2000000000000000000000000000000000000000000000000001b607718e09f6500000000000000000000000037a8f295612602f2774d331e562be9e61b83a327"  # noqa


@pytest.mark.parametrize(
    "order, expected_args, expected_encoded_order",
    (
        (order_1, expected_args_1, expected_encoded_order_1),

    )
)
def test_exclusive_dutch_order_encoder(order, expected_args, expected_encoded_order):
    encoder = ExclusiveDutchOrderEncoder(1)
    assert expected_args == encoder._create_args(*order_1)
    assert expected_encoded_order == to_hex(encoder.encode(*order_1))


def test_generate_nonce():
    lower_bound = time.time_ns() * 10**58
    nonce = generate_nonce()
    upper_bound = time.time_ns() * 10**58
    assert lower_bound < nonce < upper_bound


expected_message_data_1 = \
    {
        'info': {
            'reactor': '0x6000da47483062A0D734Ba3dc7576Ce6A0B645C4',
            'swapper': '0xe7f525dd1bc6d748AE4D7F21D31e54741e05e110',
            'nonce': 1993350810584104428432150966441163937812467703763408189373898424638421800960,
            'deadline': 1704283964,
            'additionalValidationContract': '0x0000000000000000000000000000000000000000',
            'additionalValidationData': b''
        },
        'decayStartTime': 1704283832,
        'decayEndTime': 1704283952,
        'exclusiveFiller': '0x919f9173E2Dc833Ec708812B4f1CB11B1a17eFDe',
        'exclusivityOverrideBps': 100,
        'inputToken': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
        'inputStartAmount': 11514000000,
        'inputEndAmount': 11514000000,
        'outputs': [
            {
                'token': '0x0000000000000000000000000000000000000000',
                'recipient': '0xe7f525dd1bc6d748AE4D7F21D31e54741e05e110',
                'startAmount': 5357273070919632430,
                'endAmount': 5129553448285053856
            },
            {
                'token': '0x0000000000000000000000000000000000000000',
                'recipient': '0x37a8f295612602f2774d331e562be9e61B83a327',
                'startAmount': 8047981578747570,
                'endAmount': 7705889005936485
            }
        ]
    }


def test_create_message_data():
    message_data = ExclusiveDutchOrderEncoder._create_message_data(*order_1)
    assert expected_message_data_1 == message_data


expected_signature_4 = "0xf4ff6b7dffc473ab3ad0d8635d1ce8fda152e3ef1786d66683edc84d49b5d0d072336c06dd04e17abd978a8737b78fbd7699694012c2378e8ffacad9b3ddde011c"  # noqa


def test_create_permit2_signable_message(account):
    encoder = ExclusiveDutchOrderEncoder(1)
    signable_message = encoder.create_permit2_signable_message(*order_4)
    signed_message = account.sign_message(signable_message)
    assert expected_signature_4 == signed_message.signature.hex()

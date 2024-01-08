import asyncio
import os
import subprocess
import time

from eth_utils import keccak
from uniswap_universal_router_decoder import (
    FunctionRecipient,
    RouterCodec,
)
from web3 import (
    Account,
    Web3,
)
from web3.types import Wei

from uniswapx_sdk.encoder import (
    DecayTime,
    ExclusiveDutchOrderEncoder,
    ExclusiveDutchOrderInfo,
    ExclusiveDutchOrderInput,
    ExclusiveDutchOrderOutput,
    ExclusiveFiller,
)
from uniswapx_sdk.resolver import OrderResolver


web3_provider = os.environ['WEB3_HTTP_PROVIDER_URL_ETHEREUM_MAINNET']
ganache_endpoint = "http://127.0.0.1:8545"
w3 = Web3(Web3.HTTPProvider(ganache_endpoint))
chain_id = 1
block_number = 18949582
gas_limit = 800_000

alice_account = Account.from_key(keccak(text="moo"))
assert alice_account.address == "0xcd7328a5D376D5530f054EAF0B9D235a4Fd36059"

bob_account = Account.from_key(keccak(text="baa"))
assert bob_account.address == "0xdb45Eb8B663084225ec9bB814b827F5946Ca3665"

init_amount = 100 * 10**18

erc20_abi = '[{"constant":true,"inputs":[],"name":"name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_from","type":"address"},{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transferFrom","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"decimals","outputs":[{"name":"","type":"uint8"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"symbol","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"_owner","type":"address"},{"name":"_spender","type":"address"}],"name":"allowance","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_from","type":"address"},{"indexed":true,"name":"_to","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Transfer","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_owner","type":"address"},{"indexed":true,"name":"_spender","type":"address"},{"indexed":false,"name":"_value","type":"uint256"}],"name":"Approval","type":"event"}]'  # noqa

weth_address = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
usdc_address = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
usdc_contract = w3.eth.contract(address=usdc_address, abi=erc20_abi)

ur_address = Web3.to_checksum_address("0xEf1c6E67703c7BD7107eed8303Fbe6EC2554BF6B")
reactor_address = Web3.to_checksum_address("0x6000da47483062a0d734ba3dc7576ce6a0b645c4")
permit2_address = Web3.to_checksum_address("0x000000000022D473030F116dDEE9F6B43aC78BA3")

start_amount, end_amount = int(0.52 * 10**18), int(0.51 * 10**18)


def launch_ganache():
    ganache_process = subprocess.Popen(
        f"""ganache
        --logging.quiet='true'
        --fork.url='{web3_provider}'
        --chain.chainId='{chain_id}'
        --fork.blockNumber='{block_number}'
        --miner.defaultGasPrice='15000000000'
        --wallet.accounts='{alice_account.key.hex()}','{init_amount}' '{bob_account.key.hex()}','{init_amount}'
        """.replace("\n", " "),
        shell=True,
    )
    time.sleep(3)
    parent_id = ganache_process.pid
    return parent_id


def kill_processes(parent_id):
    processes = [str(parent_id), ]
    pgrep_process = subprocess.run(
        f"pgrep -P {parent_id}", shell=True, text=True, capture_output=True
    ).stdout.strip("\n")
    children_ids = pgrep_process.split("\n") if len(pgrep_process) > 0 else []
    processes.extend(children_ids)
    subprocess.run(f"kill {' '.join(processes)}", shell=True, text=True, capture_output=True)


def check_initialization():
    assert w3.eth.chain_id == chain_id  # 1337
    assert w3.eth.block_number == block_number + 1
    assert w3.eth.get_balance(alice_account.address) == init_amount == w3.eth.get_balance(bob_account.address)
    assert usdc_contract.functions.balanceOf(alice_account.address).call() == 0
    assert usdc_contract.functions.balanceOf(bob_account.address).call() == 0
    print(" => Initialization: OK")


def send_transaction(from_account, to_address, value, encoded_data):
    trx_params = {
        "from": from_account.address,
        "to": to_address,
        "gas": gas_limit,
        "maxPriorityFeePerGas": w3.eth.max_priority_fee,
        "maxFeePerGas": Wei(int(w3.eth.gas_price * 2) + w3.eth.max_priority_fee),
        "type": '0x2',
        "chainId": chain_id,
        "value": value,
        "nonce": w3.eth.get_transaction_count(from_account.address),
        "data": encoded_data,
    }
    raw_transaction = w3.eth.account.sign_transaction(trx_params, from_account.key).rawTransaction
    trx_hash = w3.eth.send_raw_transaction(raw_transaction)
    return trx_hash


def alice_buys_usdc():
    codec = RouterCodec()
    v3_path = [weth_address, 500, usdc_address]
    v3_out_amount = 1000 * 10**6
    v3_amount_in_max = 1 * 10**18
    encoded_input = (
        codec
        .encode
        .chain()
        .wrap_eth(FunctionRecipient.ROUTER, v3_amount_in_max)
        .v3_swap_exact_out(FunctionRecipient.SENDER, v3_out_amount, v3_amount_in_max, v3_path, payer_is_sender=False)
        .unwrap_weth(FunctionRecipient.SENDER, 0)
        .build(codec.get_default_deadline())
    )
    trx_hash = send_transaction(alice_account, ur_address, v3_amount_in_max, encoded_input)

    receipt = w3.eth.wait_for_transaction_receipt(trx_hash)
    assert receipt["status"] == 1  # trx success
    assert usdc_contract.functions.balanceOf(alice_account.address).call() == 1000 * 10**6
    assert w3.eth.get_balance(alice_account.address) == 99550847420440762427
    print(" => BUY USDC: OK")


def alice_approves_permit2_for_usdc():
    contract_function = usdc_contract.functions.approve(permit2_address, 2**256 - 1)
    trx_params = contract_function.build_transaction(
        {
            "from": alice_account.address,
            "gas": gas_limit,
            "maxPriorityFeePerGas": w3.eth.max_priority_fee,
            "maxFeePerGas": Wei(30 * 10**9),
            "type": '0x2',
            "chainId": chain_id,
            "value": 0,
            "nonce": w3.eth.get_transaction_count(alice_account.address),
        }
    )
    raw_transaction = w3.eth.account.sign_transaction(trx_params, alice_account.key).rawTransaction
    trx_hash = w3.eth.send_raw_transaction(raw_transaction)

    receipt = w3.eth.wait_for_transaction_receipt(trx_hash)
    assert receipt["status"] == 1, f'receipt["status"] is actually {receipt["status"]}'  # trx success
    print(" => APPROVE PERMIT2 FOR USDC: OK")


def alice_creates_dutch_order():
    order_info = ExclusiveDutchOrderInfo(
        reactor=reactor_address,
        swapper=alice_account.address,
        nonce=17044488556984821651367783140780206339718078492509275355826173425128561760239,
        deadline=1714561900,
    )
    decay_time = DecayTime(1704561560, 1714561890)
    dutch_input = ExclusiveDutchOrderInput(usdc_address, 1000 * 10**6, 1000 * 10**6)

    dutch_outputs = (
        ExclusiveDutchOrderOutput(
            token='0x0000000000000000000000000000000000000000',
            start_amount=start_amount,
            end_amount=end_amount,
            recipient=alice_account.address,
        ),
    )
    exclusive_filler = ExclusiveFiller()

    encoder = ExclusiveDutchOrderEncoder(1)
    encoded_order, signable_message = encoder.encode_order(
        order_info,
        decay_time,
        dutch_input,
        dutch_outputs,
        exclusive_filler
    )
    signed_message = alice_account.sign_message(signable_message)

    print(" => CREATE DUTCH ORDER: OK")
    return encoded_order, signed_message.signature


def bob_resolves_order(order, sig):
    resolver = asyncio.run(OrderResolver.create(rpc_endpoint=ganache_endpoint))
    resolved_order = asyncio.run(resolver.resolve(order, sig))
    outputs = resolved_order[2]
    assert len(outputs) == 1
    output_token_address = outputs[0][0]
    assert output_token_address == '0x0000000000000000000000000000000000000000'
    output_amount = outputs[0][1]
    assert start_amount > output_amount > end_amount
    output_recipient = outputs[0][2]
    assert output_recipient == alice_account.address

    print(" => RESOLVE ORDER: OK")
    return resolved_order


def bob_executes_order(order, sig, resolved_order):
    encoded_input = ExclusiveDutchOrderEncoder.encode_execute(order, sig)
    trx_hash = send_transaction(bob_account, reactor_address, resolved_order[2][0][1], encoded_input)

    receipt = w3.eth.wait_for_transaction_receipt(trx_hash)
    assert receipt["status"] == 1  # trx success
    assert usdc_contract.functions.balanceOf(alice_account.address).call() == 0
    assert usdc_contract.functions.balanceOf(bob_account.address).call() == 1000 * 10 ** 6
    assert w3.eth.get_balance(alice_account.address) > 100 * 10**18
    print(" => EXECUTE ORDER: OK")


def launch_integration_tests():
    print("------------------------------------------")
    print("| Launching integration tests            |")
    print("------------------------------------------")
    check_initialization()
    alice_buys_usdc()
    alice_approves_permit2_for_usdc()
    order, sig = alice_creates_dutch_order()
    resolved_order = bob_resolves_order(order, sig)
    bob_executes_order(order, sig, resolved_order)


def print_success_message():
    print("------------------------------------------")
    print("| Integration tests are successful !! :) |")
    print("------------------------------------------")


def main():
    ganache_pid = launch_ganache()
    try:
        launch_integration_tests()
        print_success_message()
    finally:
        kill_processes(ganache_pid)


if __name__ == "__main__":
    main()

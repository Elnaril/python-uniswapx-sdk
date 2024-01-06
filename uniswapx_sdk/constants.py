from web3 import AsyncWeb3


# https://github.com/Uniswap/uniswapx-sdk/blob/main/src/constants.ts
order_quoters = {  # ORDER_QUOTER_MAPPING
    1: AsyncWeb3.to_checksum_address("0x54539967a06Fc0E3C3ED0ee320Eb67362D13C5fF"),
    5: AsyncWeb3.to_checksum_address("0x54539967a06Fc0E3C3ED0ee320Eb67362D13C5fF"),
    137: AsyncWeb3.to_checksum_address("0x54539967a06Fc0E3C3ED0ee320Eb67362D13C5fF"),
    12341234: AsyncWeb3.to_checksum_address("0xbea0901A41177811b099F787D753436b2c47690E"),
}

order_quoter_abi = '[{"inputs":[],"name":"OrdersLengthIncorrect","type":"error"},{"inputs":[{"internalType":"bytes","name":"order","type":"bytes"}],"name":"getReactor","outputs":[{"internalType":"contract IReactor","name":"reactor","type":"address"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes","name":"order","type":"bytes"},{"internalType":"bytes","name":"sig","type":"bytes"}],"name":"quote","outputs":[{"components":[{"components":[{"internalType":"contract IReactor","name":"reactor","type":"address"},{"internalType":"address","name":"swapper","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"contract IValidationCallback","name":"additionalValidationContract","type":"address"},{"internalType":"bytes","name":"additionalValidationData","type":"bytes"}],"internalType":"struct OrderInfo","name":"info","type":"tuple"},{"components":[{"internalType":"contract ERC20","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"maxAmount","type":"uint256"}],"internalType":"struct InputToken","name":"input","type":"tuple"},{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"internalType":"struct OutputToken[]","name":"outputs","type":"tuple[]"},{"internalType":"bytes","name":"sig","type":"bytes"},{"internalType":"bytes32","name":"hash","type":"bytes32"}],"internalType":"struct ResolvedOrder","name":"result","type":"tuple"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"components":[{"components":[{"internalType":"contract IReactor","name":"reactor","type":"address"},{"internalType":"address","name":"swapper","type":"address"},{"internalType":"uint256","name":"nonce","type":"uint256"},{"internalType":"uint256","name":"deadline","type":"uint256"},{"internalType":"contract IValidationCallback","name":"additionalValidationContract","type":"address"},{"internalType":"bytes","name":"additionalValidationData","type":"bytes"}],"internalType":"struct OrderInfo","name":"info","type":"tuple"},{"components":[{"internalType":"contract ERC20","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"maxAmount","type":"uint256"}],"internalType":"struct InputToken","name":"input","type":"tuple"},{"components":[{"internalType":"address","name":"token","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"address","name":"recipient","type":"address"}],"internalType":"struct OutputToken[]","name":"outputs","type":"tuple[]"},{"internalType":"bytes","name":"sig","type":"bytes"},{"internalType":"bytes32","name":"hash","type":"bytes32"}],"internalType":"struct ResolvedOrder[]","name":"resolvedOrders","type":"tuple[]"},{"internalType":"bytes","name":"","type":"bytes"}],"name":"reactorCallback","outputs":[],"stateMutability":"pure","type":"function"}]'  # noqa

uniswapx_api_root = "https://api.uniswap.org/v2/"
uniswapx_orders_endpoint = f"{uniswapx_api_root}orders"

permit2_domain_data = {
            "name": "Permit2",
            "chainId": 1,
            "verifyingContract": "0x000000000022D473030F116dDEE9F6B43aC78BA3",
        }
exclusive_dutch_order_abi = ['((address,address,uint256,uint256,address,bytes),uint256,uint256,address,uint256,(address,uint256,uint256),(address,uint256,uint256,address)[])']  # noqa
exclusive_dutch_order_types = {
    "PermitWitnessTransferFrom": [
        {"name": 'permitted', "type": 'TokenPermissions'},
        {"name": 'spender', "type": 'address'},
        {"name": 'nonce', "type": 'uint256'},
        {"name": 'deadline', "type": 'uint256'},
        {"name": 'witness', "type": "ExclusiveDutchOrder"},
    ],

    "TokenPermissions": [
        {'name': 'token', 'type': 'address'},
        {'name': 'amount', 'type': 'uint256'},
    ],

    "ExclusiveDutchOrder": [
        {"name": "info", "type": "OrderInfo"},
        {"name": "decayStartTime", "type": "uint256"},
        {"name": "decayEndTime", "type": "uint256"},
        {"name": "exclusiveFiller", "type": "address"},
        {"name": "exclusivityOverrideBps", "type": "uint256"},
        {"name": "inputToken", "type": "address"},
        {"name": "inputStartAmount", "type": "uint256"},
        {"name": "inputEndAmount", "type": "uint256"},
        {"name": "outputs", "type": "DutchOutput[]"},
    ],
    "OrderInfo": [
        {"name": "reactor", "type": "address"},
        {"name": "swapper", "type": "address"},
        {"name": "nonce", "type": "uint256"},
        {"name": "deadline", "type": "uint256"},
        {"name": "additionalValidationContract", "type": "address"},
        {"name": "additionalValidationData", "type": "bytes"},
    ],
    "DutchOutput": [
        {"name": "token", "type": "address"},
        {"name": "startAmount", "type": "uint256"},
        {"name": "endAmount", "type": "uint256"},
        {"name": "recipient", "type": "address"},
    ],
}

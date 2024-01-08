# Python UniswapX SDK

---

#### Project Information
[![Tests & Lint](https://github.com/Elnaril/python-uniswapx-sdk/actions/workflows/ci.yml/badge.svg)](https://github.com/Elnaril/python-uniswapx-sdk/actions/workflows/ci.yml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/uniswapx-sdk)](https://pypi.org/project/python-uniswapx-sdk/)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/Elnaril/python-uniswapx-sdk)](https://github.com/Elnaril/python-uniswapx-sdk/releases)
[![PyPi Repository](https://img.shields.io/badge/repository-pipy.org-blue)](https://pypi.org/project/python-uniswapx-sdk/)
[![GitHub](https://img.shields.io/github/license/Elnaril/python-uniswapx-sdk)](https://github.com/Elnaril/python-uniswapx-sdk/blob/master/LICENSE)

#### Code Quality
[![CodeQL](https://github.com/elnaril/python-uniswapx-sdk/workflows/CodeQL/badge.svg)](https://github.com/Elnaril/python-uniswapx-sdk/actions/workflows/codeql.yml)
[![Test Coverage](https://img.shields.io/badge/dynamic/json?color=blueviolet&label=coverage&query=%24.totals.percent_covered_display&suffix=%25&url=https%3A%2F%2Fraw.githubusercontent.com%2FElnaril%2Fpython-uniswapx-sdk%2Fmaster%2Fcoverage.json)](https://github.com/Elnaril/python-uniswapx-sdk/blob/master/coverage.json)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![Type Checker: mypy](https://img.shields.io/badge/%20type%20checker-mypy-%231674b1?style=flat&labelColor=ef8336)](https://mypy-lang.org/)
[![Linter: flake8](https://img.shields.io/badge/%20linter-flake8-%231674b1?style=flat&labelColor=ef8336)](https://flake8.pycqa.org/en/latest/)

---

## Release Notes
### V0.2.0
 - Exclusive Dutch Order Encoder
 - Reactor Execute Encoder
 - Get Orders from UniswapX API
 - Integration Tests
 - Documentation
### V0.1.0
 - Exclusive Dutch Order Decoder
 - Order Resolver

---

## Overview and Points of Attention
This library is a Python SDK that can be used to easily interact with UniswapX ecosystem: Reactors, Quoter, API.
It's partially inspired by https://github.com/Uniswap/uniswapx-sdk

⚠ This library has not been audited, so use at your own risk !

⚠ The API currently exposed is very likely to change with the following versions: consider forcing the version.

⚠ This project is a work in progress so not all features have already been implemented.

---

## Installation
A good practice is to use [Python virtual environments](https://python.readthedocs.io/en/latest/library/venv.html), here is a [tutorial](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/).

The library can be pip installed from [pypi.org](https://pypi.org/project/uniswapx-sdk/) as usual:

```bash
# update pip to latest version if needed
pip install -U pip

# install the decoder from pypi.org
pip install uniswapx-sdk
```

---

## Usage

### How to encode an Exclusive Ducth Order
First, you need to import the classes that will help you to structure the encoding, along with a function that will compute the order nonce: 
```python
from uniswapx_sdk.encoder import (
    DecayTime,    
    ExclusiveDutchOrderInfo,
    ExclusiveDutchOrderInput,
    ExclusiveDutchOrderOutput,
    ExclusiveFiller,
    get_nonce,
)
```

Then you instantiate them:
```python
order_info = ExclusiveDutchOrderInfo(
    reactor="0x6000da47483062a0d734ba3dc7576ce6a0b645c4",
    swapper="0x...",  # your account address
    nonce=get_nonce(),
    deadline=deadline,  # Unix timestamp after which the order won't be valid any more.
)

decay_time = DecayTime(start_timestamp, end_timestamp)

dutch_input = ExclusiveDutchOrderInput(in_token_address, start_amount_in_wei, end_amount_in_wei)

dutch_outputs = (
    ExclusiveDutchOrderOutput(
        token=out_token_address,  # or '0x0000000000000000000000000000000000000000' for native coin
        start_amount=start_amount_in_wei,
        end_amount=end_amount_in_wei,
        recipient=recipient_address,  # who is going to receive the output
    ),
)

exclusive_filler = ExclusiveFiller(filler_address, bps)  # the exclusive filler if any with the override bps
#  or exclusive_filler = ExclusiveFiller() if no exclusive filler
```

And now you're ready to encode the order and sign it:
```python
import ExclusiveDutchOrderEncoder

encoder = ExclusiveDutchOrderEncoder(chain_id)
encoded_order, signable_message = encoder.encode_order(
    order_info,
    decay_time,
    dutch_input,
    dutch_outputs,
    exclusive_filler
)
signed_message = your_account.sign_message(signable_message)
```

### How to resolve/validate/quote an order
Let's say you have en encoded `order` along with its signature `sig`. Resolving it is as simple as:

```python
from uniswapx_sdk.resolver import OrderResolver

resolver = await OrderResolver.create(rpc_endpoint="https://...")
resolved_order = asyncio.run(resolver.resolve(order, sig))
```

### How to decode an order
Let's say you have en encoded order. Decoding it is as simple as:
```python
from uniswapx_sdk.decoder import ExclusiveDutchOrderDecoder

decoder = ExclusiveDutchOrderDecoder()
decoded_order = decoder.decode(encoded_order)
```

### How to get orders from UniswapX API
```python
from uniswapx_sdk.api import UniswapXAPI

api = UniswapXAPI(chain_id)
orders = await api.get_orders(order_status)  # with order_status in open, expired, error, cancelled, filled, insufficient-funds
```

### How to fill an order
Let's say you want to fill (execute) a dutch order. First you encode it as follows:
```python
from uniswapx_sdk.encoder import ExclusiveDutchOrderEncoder

encoded_input = ExclusiveDutchOrderEncoder.encode_execute(order, sig)  # where sig is the signature corresponding to the order
```
Then you include the `encoded_input` in the transaction you sign and send to the Exclusive Dutch Order Reactor.

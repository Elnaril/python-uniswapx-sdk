from typing import (
    Any,
    Dict,
    Optional,
    Union,
)


class UniswapXException(Exception):
    """
    Base class for all UniswapX SDK exceptions
    """


class OrderValidationError(UniswapXException):
    """
    Base class for all order validation errors
    """
    def __init__(self, info: str, message: Optional[str], data: Optional[Union[str, Dict[str, str]]]) -> None:
        self.info = info
        self.message = message
        self.data = data


class InvalidSignatureError(OrderValidationError):
    def __init__(self, message: Optional[str], data: Optional[Any]):
        super().__init__(info="Invalid Signature", message=message, data=data)


class NonceUsedError(OrderValidationError):
    def __init__(self, message: Optional[str], data: Optional[Any]):
        super().__init__(info="Invalid Nonce", message=message, data=data)


class InvalidOrderFieldsError(OrderValidationError):
    def __init__(self, message: Optional[str], data: Optional[Any]):
        super().__init__(info="Invalid Order Fields", message=message, data=data)


class ExpiredOrderError(OrderValidationError):
    def __init__(self, message: Optional[str], data: Optional[Any]):
        super().__init__(info="Expired Order", message=message, data=data)


class ValidationFailedError(OrderValidationError):
    def __init__(self, message: Optional[str], data: Optional[Any]):
        super().__init__(info="Validation Failed", message=message, data=data)


class ExclusivityPeriodError(OrderValidationError):
    def __init__(self, message: Optional[str], data: Optional[Any]):
        super().__init__(info="Exclusivity Period", message=message, data=data)


class InsufficientFundsError(OrderValidationError):
    def __init__(self, message: Optional[str], data: Optional[Any]):
        super().__init__(info="Insufficient Funds", message=message, data=data)


order_validation_exceptions = {
    "0x8baa579f": InvalidSignatureError,
    "0x815e1d64": InvalidSignatureError,
    "0x756688fe": NonceUsedError,
    "0x302e5b7c": InvalidOrderFieldsError,
    "0x773a6187": InvalidOrderFieldsError,
    "0x4ddf4a64": InvalidOrderFieldsError,
    "0xd303758b": InvalidOrderFieldsError,
    "0x7c1f8113": InvalidOrderFieldsError,
    "0x43133453": InvalidOrderFieldsError,
    "0x48fee69c": InvalidOrderFieldsError,
    "0x70f65caa": ExpiredOrderError,
    "0xee3b3d4b": NonceUsedError,
    "0x0a0b0d79": ValidationFailedError,
    "0xb9ec1e96": ExclusivityPeriodError,
    "0x062dec56": ExclusivityPeriodError,
    "0x75c1bb14": ExclusivityPeriodError,
    "TRANSFER_FROM_FAILED": InsufficientFundsError,
    None: OrderValidationError,
}

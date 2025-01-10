from __future__ import annotations

from typing import TYPE_CHECKING, Any, Concatenate

import cerberus
import functools
import json
import time

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from server.handlers import BaseHandler

class RateLimitPool:
    __slots__ = ("limit", "timeframe", "_handlers")

    def __init__(self, limit: float, timeframe: float):
        self.limit: float = limit
        self.timeframe: float = timeframe
        self._handlers: dict[Any, RateLimit] = {}

    def handle(self, key):
        if key not in self._handlers:
            self._handlers[key] = RateLimit(self.limit, self.timeframe)
        return self._handlers[key].trigger()


class RateLimit:
    __slots__ = ("limit", "timeframe", "_used", "_last")

    def __init__(self, limit: float, timeframe: float):
        self.limit: float = limit
        self.timeframe: float = timeframe
        self._last: float = time.monotonic()
        self._used: int = 0

    def trigger(self) -> bool:
        current = time.monotonic()

        if not self._last or current > self._last + self.limit:
            self._last = current
            self._used = 1
            return True
        elif self._used == self.limit:
            return False
        else:
            self._used += 1
            return True


def validate[T: BaseHandler, **P](
    schema,
    *,
    require_all: bool = True,
    require_authentication: bool = False,
    ratelimit: RateLimitPool | None = None
) -> Callable[[Callable[Concatenate[T, P], Awaitable[Any]]], Callable[Concatenate[T, P], Awaitable[Any]]]:
    def predicate(func: Callable[Concatenate[T, P], Awaitable[Any]]) -> Callable[Concatenate[T, P], Awaitable[Any]]:
        @functools.wraps(func)
        async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> Any:
            validator: Any = cerberus.Validator(schema, require_all=require_all) # type: ignore

            if require_authentication and not self.current_user:
                return self.send_error(401, message="User must be authenticated.")
            if ratelimit and self.current_user and not ratelimit.handle(self.current_user["id"]):
                return self.send_error(429, message="Too many attempts. Try again later.")

            try:
                data = json.loads(self.request.body)
            except json.JSONDecodeError:
                return self.send_error(400, message="Expected a JSON body.")
            if not validator.validate(data):
                return self.send_error(400, message="JSON body validation failed.")

            self.body = data
            await func(self, *args, **kwargs)

        return wrapper
    return predicate

import cerberus
import functools
import json
import time

class RateLimitPool:
    __slots__ = ("limit", "timeframe", "_handlers")

    def __init__(self, limit, timeframe):
        self.limit = limit
        self.timeframe = timeframe
        self._handlers = {}

    def handle(key):
        if key not in self._handlers:
            self._handlers[key] = RateLimit(self.limit, self.timeframe)

        return self._handlers[key].trigger()

class RateLimit:
    __slots__ = ("limit", "timeframe", "_used", "_last")

    def __init__(self, limit, timeframe):
        self.limit = limit
        self.timeframe = timeframe
        self._used = 0
        self._last = time.monotonic()

    def trigger(self):
        current = time.monotonic()

        if not last or current > self._last + self.limit:
            self._last = current
            self._used = 1
            return True
        elif self._used == limit:
            return False
        else:
            self._used += 1
            return True

def validate(schema, *, require_all=True, require_authentication=False, ratelimit=None):
    def inner(func):
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            validator = cerberus.Validator(schema, require_all=require_all)

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
    return inner

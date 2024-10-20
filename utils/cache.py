import time

class ExpiringDictionary(dict):
    def __init__(self, *, max_age):
        self._max_age = max_age
        super().__init__()

    def _update(self):
        for key, value in list(super().items()):
            if value.expires_at < time.monotonic():
                self.pop(key)

    def __setitem__(self, key, value):
        super().__setitem__(key, _ExpiringDictionaryItem(value, time.monotonic() + self._max_age))

    def __getitem__(self, key):
        self._update()
        item = super().__getitem__(key)
        return item.value

    def __delitem__(self, key):
        self._update()
        super().__delitem__()

    def __contains__(self, key):
        self._update()
        return super().__contains__(key)

    def get(self, key, default=None):
        self._update()
        item = super().get(key)
        return item.value if item else default

class _ExpiringDictionaryItem:
    def __init__(self, value, expires_at):
        self.value = value
        self.expires_at = expires_at

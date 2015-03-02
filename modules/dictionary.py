

class Dictionary:

    def __init__(self, usernames, passwords, pairs):
        self._pairs = pairs
        self._usernames = usernames
        self._passwords = passwords

    def pairs(self):
        for username, password in self._pairs:
            yield (username, password)

        for username in self._usernames:
            for password in self._passwords:
                yield (username, password)
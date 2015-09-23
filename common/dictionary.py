
from common.keyspace import KeySpace

class Dictionary:

    def __init__(self, dictionaries):
        self.dictionaries = dictionaries

    def make_iterator(self, elements):
        field_name = {0:'username', 1:'password',
                      3:'username', 4:'password'}
        for element in elements:
            _type = element['type']
            if _type in [0, 1]:
                yield element[field_name[_type]]
            elif _type in [3, 4]:
                charsets = {}
                if 'charsets' in element:
                    charsets = element['charsets']
                for keyword in KeySpace(element[field_name[_type]], charsets):
                    yield keyword
        

    def join(self):

        pairs = []
        username_pairs = {}
        for dictionary in self.dictionaries:
            if not 'pairs' in dictionary:
                continue

            for pair in dictionary['pairs']:
                if pair['type'] == 2:
                    if not pair['username'] in username_pairs:
                        username_pairs[pair['username']] = []
                    username_pairs[pair['username']].append(pair)

                elif pair['type'] == 5:
                    pairs.append(pair)

        for dictionary in self.dictionaries:
            usernames_iter = self.make_iterator(dictionary['usernames'])

            for username in usernames_iter:
                passwords_iter = self.make_iterator(dictionary['passwords'])

                if username in username_pairs:
                    for pair in username_pairs[username]:
                        yield (username, pair['password'])
                    del(username_pairs[username])

                for password in passwords_iter:
                    yield (username, password)

        pairs.extend([pair for pairs_list in username_pairs.values() for pair in pairs_list])
        for pair in pairs:
            if pair['type'] == 2:
                yield (pair['username'], pair['password'])
            elif pair['type'] == 5:
                charsets = {}
                if 'charsets' in pair:
                    charsets = pair['charsets']
                for username in KeySpace(pair['username'], charsets):
                    for password in KeySpace(pair['password'], charsets):
                        yield (username, password)



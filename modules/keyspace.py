
import re
from functools import reduce

class KeySpace:

    def __init__(self, mask, charsets={}):
        self.done = False
        self.mask = mask
        self.charsets = {
            '?l':'abcdefghijklmnopqrstuvwxyz',
            '?u':'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
            '?d':'0123456789',
            '?s':' !"#$%&\'()*+,-./:;<=>?@[]^_`{|}~',
            '??':'?'
        }

        to_resolve = {'?a':'?l?u?d?s'}
        to_resolve.update(charsets)
        for key, tokens in to_resolve.items():
            result = tokens
            for token, charset in self.charsets.items():
                result = result.replace(token, charset)
            self.charsets[key] = result

        self.lockers = []

        tokens = re.findall('(\?\w|\?\?|[^\?])', mask)
        for token in tokens:
            if token in self.charsets:
                self.lockers.append(list(set(self.charsets[token])))
            else:
                self.lockers.extend([[c] for c in token])

        self.indexes = [0] * len(self.lockers)


    def __iter__(self):
        return self


    def __next__(self):

        if self.done:
            raise StopIteration

        result = ''.join([self.lockers[i][self.indexes[i]] for i in range(0, len(self.indexes))])
        self.indexes[0] += 1

        for i in range(0, len(self.indexes)):
            if self.indexes[i] >= len(self.lockers[i]):
                self.indexes[i] = 0
                if i+1 < len(self.indexes):
                    self.indexes[i+1] += 1
                else:
                    self.done = True
            else:
                break

        return result

    def __len__(self):
        return reduce(lambda x, y: x*y, [len(locker) for locker in self.lockers])

if __name__ == "__main__":

    g = KeySpace('pedro?d?d?d?s', {'?1':'89'})

    #print(len(g))
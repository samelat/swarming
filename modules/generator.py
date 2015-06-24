
import re
import string

class Generator:

    def __init__(self, mask, charsets={}):
        self.done = False
        self.mask = mask
        self.charsets = {
            '?d':string.digits,
            '?1':'abcdef',
            '?2':'ABC',
            '??':'?'
        }

        self.lockers = []

        tokens = re.findall('(\?\w|\?\?|[^\?])', mask)
        for token in tokens:
            if token in self.charsets:
                self.lockers.append(list(set(self.charsets[token])))
            else:
                self.lockers.append(list(set(token)))

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

if __name__ == "__main__":

    g = Generator('?2?2?2')

    for i in g:
        print(i)
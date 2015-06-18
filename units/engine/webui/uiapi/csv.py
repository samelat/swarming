
import re
import csv
import codecs


class CSV:

    def __init__(self, orm):
        self.orm = orm

    def digest(self, file, params):
        reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        print('[csv] reader: {0}'.format(reader))

        count = 0

        while True:

            chunk = []
            for line in reader:
                entry = {}
                for column in reader.fieldnames:
                    if column == 'url':
                        match = re.match('^(?P<protocol>[^:]+)://(?P<hostname>[^:/]+)(?::(?P<port>\d+))?(?P<path>[^\?]*)', line[column])
                        if not match:
                            continue
                        for field, value in match.groupdict().items():
                            if value and field in self.orm.entities[params['entity']].attributes):
                                entry[field] = value

                    else:
                        entry[column] = line[column]

                for field, value in entry.items():
                    if (_field in self.orm.entities[params['entity']].attributes) and value:
                        entry[_field] = value

            if not chunk:
                break

            count += 1
            chunk.append(entry)
            if len(chunk) > 400:
                print('[upload] #{0}'.format(count))
                self.orm.session_lock.acquire()
                self.orm.add(params['entity'], chunk)
                self.orm.session_lock.release()
                chunk = []

        print('[upload] #{0}'.format(count))

        return {'status':0}

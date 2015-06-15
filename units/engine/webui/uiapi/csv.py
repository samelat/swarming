
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
        for row in reader:
            result = {}
            for field in reader.fieldnames:
                if field == 'url':
                    match = re.match('^(?P<protocol>[^:]+)://(?P<hostname>[^:/]+)(?::(?P<port>\d+))?(?P<path>[^\?]*)', row[field])
                    if not match:
                        continue

                    for key, value in match.groupdict().items():
                        if value:
                            result[key] = value

                elif field in self.orm.entities[params['entity']].attributes:
                    if not row[field]:
                        result[field] = None
                    else:
                        result[field] = row[field]

            if not (count % 2000):
                print('[upload] #{0} data: {1}'.format(count, result))
            count += 1

            # I don't know if I could improve performance here
            self.orm.session_lock.acquire()
            result = self.orm.set(params['entity'], result)
            self.orm.session_lock.release()
        print('[upload] #{0} data: {1}'.format(count, result))
        self.orm.session.commit()

        return {'status':0}

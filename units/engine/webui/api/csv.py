
import re
import csv
import codecs


class CSV:

    def __init__(self, orm):
        self.orm = orm
    

    def digest(self, file, params):
        reader = csv.DictReader(codecs.iterdecode(file.file, 'utf-8'))
        #print('[csv] reader: {0}'.format(reader))

        count = 0

        while True:

            chunk = []
            for line in reader:
                entry = {}
                for column in reader.fieldnames:
                    if column == 'url':
                        match = re.match('^(?P<protocol>[^:]+)://(?P<hostname>[^:/]+)(?::(?P<port>\d+))?(?P<path>[^\?]*)', line[column])
                        if match:
                            entry.update(match.groupdict())

                    else:
                        entry[column] = line[column]

                #print('[values] {0}'.format(entry))
                new_entry = self.orm.entities[params['entity']].suit(entry)

                if new_entry:
                    chunk.append(new_entry)

                if len(chunk) > 400:
                    break

            if not chunk:
                break

            count += 1
            
            #print('[upload] #{0}'.format(count))
            self.orm.session_lock.acquire()
            self.orm.add(params['entity'], chunk)
            self.orm.session_lock.release()

        #print('[upload] #{0}'.format(count))

        return {'status':0}

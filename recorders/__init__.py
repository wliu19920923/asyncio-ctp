import os
import pandas


class Recorder(object):
    def __init__(self, dtype, filepath=None):
        self.dtype = dtype
        self.filepath = filepath
        self.records = self._load()

    def _load(self):
        try:
            if self.filepath and os.path.exists(self.filepath):
                return pandas.read_csv(self.filepath, index_col=0, dtype=self.dtype)
        except Exception as exp:
            print(exp)
        return pandas.DataFrame(columns=self.dtype.keys())

    def _save(self):
        if self.filepath:
            self.records.to_csv(self.filepath)

    def insert(self, record):
        self.records = self.records.append([record], ignore_index=True)
        self._save()
        return record

    def delete(self, **kwargs):
        records = self.records
        for key, value in kwargs.items():
            if not len(records):
                break
            records = records.loc[records[key] == value]
        self.records = self.records.drop(records.index)
        self._save()
        return records.to_dict(orient='records')

    def update(self, record: dict, **kwargs):
        records = self.records
        for key, value in kwargs.items():
            if not len(records):
                break
            records = records.loc[records[key] == value]
        self.records[records.index, list(record.keys())] = list(record.values())
        self._save()
        return record

    def update_or_insert(self, record: dict, **kwargs):
        records = self.records
        for key, value in kwargs.items():
            if not len(records):
                break
            records = records.loc[records[key] == value]
        if len(records.index) > 0:
            self.records.loc[records.index, list(record.keys())] = list(record.values())
        else:
            self.records = self.records.append([record], ignore_index=True)
        self._save()
        return record

    def query(self, **kwargs):
        records = self.records
        for key, value in kwargs.items():
            if not len(records):
                break
            records = records.loc[records[key] == value]
        return records.to_dict(orient='records')

    def clear(self):
        records = self.records
        self.records = self.records.drop(records.index)
        self._save()
        return records.to_dict(orient='records')

    def drop(self, filters):
        records = self.records[filters]
        self.records = self.records.drop(records.index)
        self._save()
        return records.to_dict(orient='records')


if __name__ == '__main__':
    r = Recorder({'a': int})
    r.update_or_insert({'a': 1})
    print(r.query())
    r.update_or_insert({'a': 2}, a=2)
    print(r.query())

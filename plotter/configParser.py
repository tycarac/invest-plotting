from __future__ import annotations
import datetime
from dataclasses import dataclass
from dateutil import parser
import jsonschema as js
import logging.handlers
from os import PathLike
from pathlib import Path
import yaml

_logger = logging.getLogger(__name__)


# _____________________________________________________________________________
@dataclass
class ConfigCsvFile:
    __slots__ = ['idx', 'filename', 'code', 'fields']

    idx: int
    filename: str
    code: str
    fields: dict[str, str]

    # _____________________________________________________________________________
    def __init__(self, filename, code, fields, idx):
        self.idx = idx
        self.filename = filename
        self.code = code
        self.fields = fields


# _____________________________________________________________________________
@dataclass
class ConfigPlotView:
    __slots__ = ['idx', 'start_date', 'title']

    idx: int
    start_date: datetime.datetime
    title: str

    # _____________________________________________________________________________
    def __init__(self, item, idx):
        self.idx = idx
        self.start_date = parser.parse(item['startDate']) if 'startDate' in item else None
        self.title = item.get('title', '')
        if not self.title and self.start_date:
            self.title = f'Start date: {self.start_date:%d-%b-%y}'


# _____________________________________________________________________________
@dataclass
class ConfigPlot:
    __slots__ = ['idx', 'tag', 'filename', 'csv_files', 'views']

    idx: int
    tag: str
    filename: str
    csv_files: list[ConfigCsvFile]
    views: list[ConfigPlotView]

    # _____________________________________________________________________________
    def __init__(self, item, idx):
        self.idx = idx
        self.tag = item.get('tag', '')
        self.csv_files = self.__parse_csv_files(item.get('csvFiles')) if 'csvFiles' in item else []
        self.filename = item['output']['filename']
        self.views = [ConfigPlotView(x, i) for i, x in enumerate(item['views'])]

    # _____________________________________________________________________________
    def __parse_csv_files(self, item):
        csv_files = []

        for i, x in enumerate(item):
            if 'byFile' in x:
                data = x['byFile']
                filename = data['filename']
                code = data.get('code', '')
                fields = data.get('fields', None)
                csv_files.append(ConfigCsvFile(filename, code, fields, i))
            elif 'byCodes' in x:
                data = x['byCodes']
                fields = data.get('fields', None)
                for code in data.get('yahooCodes', []):
                    filename = f'{code}.csv'
                    csv_files.append(ConfigCsvFile(filename, code, fields, i))

        return csv_files


# _____________________________________________________________________________
class ConfigParser:
    # _____________________________________________________________________________
    @staticmethod
    def parse(path: PathLike) -> list[ConfigPlot]:
        filename = Path(path).resolve()
        schema_filename = filename.with_suffix('.schema.yaml').resolve()
        _logger.debug(f'config filename: {filename}')
        _logger.debug(f'schema filename: {schema_filename}')

        try:
            data = yaml.safe_load(filename.read_text())
            data_schema = yaml.safe_load(schema_filename.read_text())
            js.validate(instance=data, schema=data_schema)
            entries = [ConfigPlot(x, i) for i, x in enumerate(data['plots'])]
        except yaml.YAMLError as ex:
            _logger.exception(f'Parse rrror in: "{filename.name}"')
            raise
        except js.SchemaError as ex:
            _logger.exception(f'Schema error in: "{filename.name}" {ex.message}')
            raise
        except js.ValidationError as ex:
            _logger.exception(f'Validation error in: "{filename.name}" {ex.message}')
            raise
        return entries

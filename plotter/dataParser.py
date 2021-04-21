from abc import ABC, abstractmethod
from dataclasses import dataclass
from os import PathLike
import logging.handlers
import pandas as pd
from pathlib import Path
from typing import Union

_logger = logging.getLogger(__name__)


# _____________________________________________________________________________
@dataclass
class DataSource:
    __slots__ = ['code', 'filepath', 'fields']

    code: str
    filepath: PathLike
    fields: dict[str: str]


# _____________________________________________________________________________
class DataParser(ABC):
    # _____________________________________________________________________________
    def __init__(self, parser_name):
        self._parser_name = parser_name

    # _____________________________________________________________________________
    @abstractmethod
    def parses(self, data_sources: list[DataSource], /, **kwargs) -> pd.DataFrame:
        raise NotImplementedError(f'Parser name "{self._parser_name}" parse')

    # _____________________________________________________________________________
    def parse(self, data_source: Union[DataSource, list[DataSource]], **kwargs) -> pd.DataFrame:
        if type(data_source) is str:
            return self.parses([data_source], **kwargs)
        else:
            return self.parses(data_source, **kwargs)

    # _____________________________________________________________________________
    @property
    def parser_name(self):
        return self._parser_name


# _____________________________________________________________________________
class CsvParser(DataParser):
    # _____________________________________________________________________________
    def __init__(self):
        super().__init__('CsvParser')

    # _____________________________________________________________________________
    def parses(self, data_sources: list[DataSource], /, **kwargs) -> pd.DataFrame:
        _logger.debug(f'Parser {self.parser_name}: {len(data_sources)} files')

        df = pd.DataFrame()
        for ds in data_sources:
            filepath = Path(ds.filepath)
            fields = ds.fields
            _logger.debug(f'Parsing {ds.code}: "{filepath.name}"')

            # Load csv file
            date_col = fields.get('Date', 'Date')
            _logger.debug(f'Parsing {ds.code}: index column "{date_col}"')
            dff = pd.read_csv(str(filepath), index_col=date_col, parse_dates=True)

            # Copy columns
            for key in fields.keys():
                if key == 'Date':
                    continue
                df_column_name = ds.code if key == 'Exit' else f'{ds.code}|{key}'
                _logger.debug(f'Parsing {ds.code}: column "{df_column_name}" <-- "{fields[key]}"')
                df[df_column_name] = dff[fields[key]]

            # Rename index label (if needed)
            if value := fields.get('Date', ''):
                _logger.debug(f'Parsing {ds.code}: index "Date" <-- "{value}"')
                df.index.rename('Date', inplace=True)

        df.sort_index(inplace=True)
        return df


# _____________________________________________________________________________
class CsvYahooParser(DataParser):
    # _____________________________________________________________________________
    def __init__(self):
        super().__init__('CsvYahooParser')

    # _____________________________________________________________________________
    def parses(self, data_sources: list[DataSource], /, **kwargs) -> pd.DataFrame:
        _logger.debug(f'Parser {self.parser_name}: {len(data_sources)} files')

        df = pd.DataFrame()
        for data_source in data_sources:
            filepath = Path(data_source.filepath)
            _logger.debug(f'Parser {self.parser_name}: "{filepath.name}"')
            dff = pd.read_csv(str(filepath), index_col='Date', parse_dates=True)
            df[data_source.code] = dff['Adj Close']
        df.sort_index(inplace=True)
        return df

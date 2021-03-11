from dateutil import parser
import json
import jsonschema as js
import logging.handlers
from os import PathLike
from pathlib import Path

_logger = logging.getLogger(__name__)


# _____________________________________________________________________________
class ConfigPlotView:
    """Holder for configuration view
    """

    # _____________________________________________________________________________
    def __init__(self, item, idx: int):
        self._idx = idx
        self._start_date = parser.parse(item['startDate']) if 'startDate' in item else None
        self._title = item.get('title', '')
        if not self._title and self._start_date:
            self._title = f'Start date: {self._start_date:%d-%b-%y}'

    # _____________________________________________________________________________
    @property
    def start_date(self):
        return self._start_date

    # _____________________________________________________________________________
    @property
    def title(self):
        return self._title


# _____________________________________________________________________________
class ConfigPlot:
    """Holder for configuration data
    """

    # _____________________________________________________________________________
    def __init__(self, item, idx: int):
        """
        Takes one JSON unpacked config item and extracts the values.  Certain values assumed
        to exist being validated by JSON schema.
        """
        self._idx = idx
        self._csv_yahoo_codes = item['data'].get('csvYahooCodes', [])
        self._output_filename = item['output']['filename']
        self._views = [ConfigPlotView(x, i) for i, x in enumerate(item['views'])]

    # _____________________________________________________________________________
    @property
    def input_csv_yahoo_codes(self):
        return self._csv_yahoo_codes

    # _____________________________________________________________________________
    @property
    def views(self):
        return self._views

    # _____________________________________________________________________________
    @property
    def output_filename(self):
        return self._output_filename


# _____________________________________________________________________________
class ConfigParser:

    # _____________________________________________________________________________
    @staticmethod
    def parse(path: PathLike) -> list[ConfigPlot]:
        filename = Path(path).resolve()
        entries = list()
        try:
            json_data = json.loads(filename.read_text())
            json_schema = json.loads(filename.with_suffix('.schema.json').read_text())
            js.validate(instance=json_data, schema=json_schema)
            entries = [ConfigPlot(x, i) for i, x in enumerate(json_data['plots'])]
        except json.JSONDecodeError as ex:
            _logger.exception(f'Error in: "{filename.name}" at {ex.lineno}:{ex.colno}')
            raise
        except js.ValidationError as ex:
            _logger.exception(f'Error in: "{filename.name}" {ex.message}')
            raise
        return entries

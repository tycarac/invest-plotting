import json
import logging.handlers
import time
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

import jsonschema as js

_logger = logging.getLogger(__name__)
lh_file = logging.FileHandler(Path(__file__).with_suffix('.log'), mode='wt')
lh_file.setLevel(logging.DEBUG)
lh_console = logging.StreamHandler()
lh_console.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG, handlers=[lh_file, lh_console])
logging.captureWarnings(True)

FIXED_PLACES = Decimal('.0001')


# _____________________________________________________________________________
def process():
    _logger.debug('process')

    config_path = Path(r'..\plotter\plots.config.json').resolve()
    schema_path = Path(r'..\plotter\plots.config.schema.json').resolve()
    _logger.info(f'Config file: "{config_path}"')
    _logger.info(f'Schema file: "{schema_path}"')

    try:
        json_config = json.loads(config_path.read_text())
    except json.JSONDecodeError as ex:
        _logger.exception(f'JSON error in: "{config_path.name}" at {ex.lineno}:{ex.colno}')
        raise
    try:
        json_schema = json.loads(schema_path.read_text())
    except json.JSONDecodeError as ex:
        _logger.exception(f'JSON error in: "{schema_path.name}" at {ex.lineno}:{ex.colno}')
        raise

    try:
        _logger.info(f'Validating ...')
        js.validate(instance=json_config, schema=json_schema, format_checker=js.draft7_format_checker)
        _logger.info(f'Validation passed')
    except js.ValidationError as ex:
        _logger.exception(f'Validation error: "{ex}')
    except js.SchemaError as ex:
        _logger.exception(f'Schema error: "{ex}')


# _____________________________________________________________________________
def main():
    start_time = time.time()
    start_datetime = datetime.fromtimestamp(start_time)
    _logger.info(f'Now: {start_datetime.strftime("%a  %d-%b-%y  %I:%M:%S %p")}')

    try:
        process()
    except Exception as ex:
        _logger.exception('Catch all exception')


# _____________________________________________________________________________
if __name__ == '__main__':
    main()

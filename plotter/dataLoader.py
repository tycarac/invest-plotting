from abc import ABC, abstractmethod
from os import PathLike
import logging.handlers
import pandas as pd
from pathlib import Path
from typing import Union

from appConfig import AppConfig
from configParser import ConfigPlot
from dataParser import CsvYahooParser, CsvParser, DataSource

_logger = logging.getLogger(__name__)
_data_parsers = {
    'csv': CsvParser,
    'yahoo': CsvYahooParser,
    '': CsvParser
}


# _____________________________________________________________________________
def load_plot_data(config_plot: ConfigPlot, app_config: AppConfig) -> pd.DataFrame:
    _logger.debug('process_codes')

    parser = CsvYahooParser()
    # filenames = [Path(app_config.data_path, f'{code}.csv') for code in config_plot.input_csv_yahoo_codes]
    data_sources = [DataSource(code, Path(app_config.data_path, f'{code}.csv'))
                    for code in config_plot.input_csv_yahoo_codes]
    df = parser.parses(data_sources)
    df.round(decimals=2)

    return df

from abc import ABC, abstractmethod
from os import PathLike
import logging.handlers
import pandas as pd
from pathlib import Path
from typing import Union

from appConfig import AppConfig
from configParser import ConfigPlot
from dataParser import CsvParser, DataSource

_logger = logging.getLogger(__name__)


# _____________________________________________________________________________
def load_plot_data(config_plot: ConfigPlot, app_config: AppConfig) -> pd.DataFrame:
    _logger.debug('load_plot_data')

    data_sources, df = [], None
    for cf in config_plot.csv_files:
        filepath = Path(app_config.data_path, cf.filename)
        data_sources.append(DataSource(cf.code, filepath, cf.fields))

    if data_sources:
        parser = CsvParser()
        df = parser.parses(data_sources)
        df.round(decimals=2)
    return df

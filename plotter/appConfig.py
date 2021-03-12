from datetime import date
import logging.handlers
from pathlib import Path

from configParser import ConfigParser, ConfigPlot

# Common variables
_logger = logging.getLogger(__name__)
_PLOTS_CONFIG_FILENAME = 'plots.config.json'


# _____________________________________________________________________________
class AppConfig:

    # _____________________________________________________________________________
    def __init__(self, app_path: Path, base_path: Path):
        """Initialises the configuration class
        """
        _logger.debug(f'__init__ app_path "{app_path}"')

        # Initialize
        self._name = app_path.stem
        self._base_path = base_path

        # Folders
        self._data_path = Path(self._base_path, 'data').resolve()
        self._output_path = Path(self._base_path, 'output').resolve()
        self._base_data_frame_path = Path(self._output_path, 'dataframes').resolve()
        self._data_frame_path = Path(self._base_data_frame_path, date.today().strftime("%y-%m-%d")).resolve()
        self._plot_base_path = Path(self._output_path, 'plots').resolve()
        self._plot_path = Path(self._plot_base_path, date.today().strftime("%y-%m-%d")).resolve()

        # Ensure directories pre-exist
        self._data_path.mkdir(parents=True, exist_ok=True)
        self._data_frame_path.mkdir(parents=True, exist_ok=True)
        self._plot_path.mkdir(parents=True, exist_ok=True)
        _logger.debug(f'data path:       "{self._data_path}"'
                      f'data frame path: "{self._data_path}"'
                      f'plot path:       "{self._plot_path}"')

        self._config_plots = ConfigParser.parse(Path(_PLOTS_CONFIG_FILENAME))

    # _____________________________________________________________________________
    @property
    def name(self):
        return self._name

    # _____________________________________________________________________________
    @property
    def data_path(self):
        return self._data_path

    # _____________________________________________________________________________
    @property
    def data_frame_path(self):
        return self._data_frame_path

    # _____________________________________________________________________________
    @property
    def plot_path(self):
        return self._plot_path

    # _____________________________________________________________________________
    @property
    def plot_configs(self) -> list[ConfigPlot]:
        return self._config_plots

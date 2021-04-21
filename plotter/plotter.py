import logging.handlers
import time
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path

import pandas as pd
import plotly as py
import plotly.graph_objs as go
import plotly.subplots as ps

from appConfig import AppConfig
from configParser import ConfigPlot, ConfigPlotView
from dataLoader import load_plot_data

_logger = logging.getLogger(__name__)
lh_file = logging.FileHandler(Path(__file__).with_suffix('.log'), mode='wt')
lh_file.setLevel(logging.DEBUG)
lh_console = logging.StreamHandler()
lh_console.setLevel(logging.INFO)
logging.basicConfig(level=logging.DEBUG, handlers=[lh_file, lh_console])
logging.captureWarnings(True)

FIXED_PLACES = Decimal('.0001')


# _____________________________________________________________________________
def plot_chart(df: pd.DataFrame, tag: str, config_views: list[ConfigPlotView], output_filepath: Path):
    _logger.debug('plot_chart')

    colors = py.colors.qualitative.Plotly
    subplot_titles = [cv.title for cv in config_views]
    fig = ps.make_subplots(rows=len(config_views), cols=1, subplot_titles=subplot_titles)

    # Plot
    for i, cv in enumerate(config_views, start=1):
        _logger.debug(f'{tag}:{i} - title "{cv.title}"')
        dff = df.loc[cv.start_date:] if cv.start_date else df
        for j, col in enumerate(df.columns):
            _logger.debug(f'{tag}:{i} - column "{col}"')
            color = colors[j % len(colors)]
            fig.add_trace(go.Scatter(name=col, x=dff.index, y=dff[col],
                                     mode='lines', line={'color': color}),
                          row=i, col=1)

    # Save to file
    _logger.debug(f'Write chart: "{output_filepath}"')
    py.io.write_html(fig, str(output_filepath),
                     include_plotlyjs='directory', full_html=True, config={'displaylogo': False})


# _____________________________________________________________________________
def process(app_config: AppConfig):
    _logger.debug('process')

    for i, plot_config in enumerate(app_config.plot_configs):
        output_filepath = Path(app_config.plot_path, plot_config.filename)
        data_frame_filepath = Path(app_config.data_frame_path, plot_config.filename).with_suffix('.csv')

        df = load_plot_data(plot_config, app_config)
        df.to_csv(data_frame_filepath)
        plot_chart(df, plot_config.tag, plot_config.views, output_filepath)


# _____________________________________________________________________________
def main():
    start_time = time.time()
    app_path = Path(__file__)
    try:
        # Configure logging
        start_datetime = datetime.fromtimestamp(start_time)
        _logger.info(f'Now: {start_datetime.strftime("%a  %d-%b-%y  %I:%M:%S %p")}')

        # Run application
        process(AppConfig(app_path, app_path.parents[1]))
    except Exception as ex:
        _logger.exception('Catch all exception')
    finally:
        mins, secs = divmod(timedelta(seconds=time.time() - start_time).total_seconds(), 60)
        _logger.info(f'Run time: {int(mins)}:{secs:0.1f}s')


# _____________________________________________________________________________
if __name__ == '__main__':
    main()

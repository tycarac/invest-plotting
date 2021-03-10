"""Transform and filter unit prices from Investing.com
 - Date formant used by investing.com (eg FEB 16, 2021) is not recognised by excel
Input 7 columns: Date, Price, Open, High, Low, Vol., Change %
Output 2 columns: Date, Exit
"""
import logging
import csv
from pathlib import Path
from dateutil import parser

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.FileHandler('output.log', mode='w'), logging.StreamHandler()])
logging.captureWarnings(True)


# _____________________________________________________________________________
def strip_line(iterator):
    for ln in iterator:
        # Skip lines with no content and not starting with a digit
        if (ln := ln.strip()) and len(ln):
            yield ln


# _____________________________________________________________________________
# Setup
base_path = Path(__file__).parent
data_path = Path(base_path, 'data').resolve()
out_path = Path(base_path, 'output').resolve()
out_path.mkdir(parents=True, exist_ok=True)

# Initialize
rows = list()

# Process
for inp_path in Path(data_path).glob('*.investing.csv'):
    _logger.info(f'Reading "{inp_path.name}"')
    with inp_path.open(mode='r', newline='') as fp:
        csv_reader = csv.reader(strip_line(fp), quoting=csv.QUOTE_MINIMAL)
        next(csv_reader) # Skip header
        for row in csv_reader:
            date = parser.parse(row[0])
            rows.append([date, row[1]])
    rows.sort(key=lambda x: x[0], reverse=True)

    # Write output
    out_filename = Path(out_path, inp_path.name).with_suffix('.csv')
    _logger.info(f'Writing "{out_filename.name}"')
    with out_filename.open(mode='wt', newline='') as out:
        csv_writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['Date', 'Exit'])
        for row in rows:
            csv_writer.writerow([f'{row[0]:%d-%m-%Y}', row[1]])

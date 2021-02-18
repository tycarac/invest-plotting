"""Transform and filter unit prices for Eley Giffiths funds

Prices are provided in PDF files.  To extract unit prices:
1. Load PDF and use "File > Save as text ..." to create text file
2. Run python script over text file to create csv file.
"""
import csv
import logging
from pathlib import Path
import re
from dateutil import parser

re_date = re.compile(r'(\d{1,2})/(\d{1,2})/(20\d{2})')
re_price = re.compile(r'(\d+(?:\.\d+))')

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.FileHandler('output.log', mode='w'), logging.StreamHandler()])
logging.captureWarnings(True)


# _____________________________________________________________________________
def strip_line(iterator):
    for ln in iterator:
        # Skip lines with no content and not starting with a digit
        if (ln := ln.strip()) and ln[0].isdigit():
            yield ln


# _____________________________________________________________________________
# Setup
base_path = Path(__file__).parent
data_path = Path(base_path, 'data').resolve()
out_path = Path(base_path, 'output').resolve()
out_path.mkdir(parents=True, exist_ok=True)

# Ready input
inp_path = Path(data_path, 'wcm-ISCG.txt').resolve()
if not inp_path.exists():
    _logger.error(f'File not found "{inp_path.name}"')
    exit(1)

# Initialize
row, rows = list(), list()

# Process
_logger.info(f'Reading "{inp_path.name}"')
with inp_path.open(mode='r', newline='') as fp:
    for line in strip_line(fp):
        if match_date := re_date.match(line):
            date = parser.parse(row[0], dayfirst=True)
            if len(row) > 1:
                rows.append(row)
            row = list()
            row.append(date)
        elif match_price := re_price.match(line):
            row.append(line)
    if len(row) > 1:
        rows.append(row)
rows.sort(key=lambda x: x[0], reverse=True)

# Write output
out_filename = Path(out_path, inp_path.name).with_suffix('.csv')
_logger.info(f'Writing {out_filename.name}')
with out_filename.open(mode='wt', newline='') as out:
    csv_writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['Date', 'Exit'])
    for row in rows:
        csv_writer.writerow([f'{row[0]:%d-%m-%Y}', row[3]])

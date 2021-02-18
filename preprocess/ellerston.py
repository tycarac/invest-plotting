"""Transform and filter unit prices for Ellerston funds
Input 4 columns: date, application, NAV, redemption
Output 3 columns: date, redemption, and redemption adjusted
"""
from datetime import date, datetime
import logging
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from dateutil import parser

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.FileHandler('output.log', mode='w'), logging.StreamHandler()])
logging.captureWarnings(True)

# Patch known bad data in Ellerston downloaded data
patch_data = {
    '16/04/0220': '16/04/2020,"Australian Micro Cap Fund",1.2698,1.2666,1.2634,Daily',
    '26/03/0202': '26/03/2020,"Australian Micro Cap Fund",1.0532,1.0506,1.0480,Daily',
    '23/01/2008': '23/01/2018,"Australian Micro Cap Fund",1.3903,1.3868,1.3833,Daily',
    '25/09/2007': '25/09/2017,"Australian Micro Cap Fund",1.1971,1.1941,1.1911,Daily',
    '28/08/2017': '28/08/2017,"Australian Micro Cap Fund",1.1853,1.1823,1.1793,Daily'
}


# _____________________________________________________________________________
def strip_line(iterator):
    for ln in iterator:
        # Skip lines with no content and not starting with a digit
        if (ln := ln.strip()) and ln[0].isdigit():
            key = ln.split(',')[0]
            if key in patch_data:
                ln = patch_data[key]
            yield ln


# _____________________________________________________________________________
# Setup
base_path = Path(__file__).parent
data_path = Path(base_path, 'data').resolve()
out_path = Path(base_path, 'output').resolve()
out_path.mkdir(parents=True, exist_ok=True)

# Ready input
inp_path = Path(data_path, 'ellerston-AMC.csv').resolve()
if not inp_path.exists():
    _logger.error(f'File not found "{inp_path.name}"')
    exit(1)

# Initialize
has_redemption = False
redemption, adj_redemption = Decimal(0.0), Decimal(0.0)
distribution, dist_redemption = Decimal(0.0), Decimal(0.0)
rows = list()

# Process
_logger.info(f'Reading "{inp_path.name}"')
with inp_path.open(mode='r', newline='') as fp:
    csv_reader = csv.reader(strip_line(fp), quoting=csv.QUOTE_MINIMAL)
    for row in csv_reader:
        if len(row) != 6:
            raise ValueError('Expecting 6 CSV values')

        date = parser.parse(row[0], dayfirst=True)
        if has_redemption := row[4].find('dist)') >= 0:
            redemption = Decimal(row[4].split(' ')[0])
            rows.append([date, redemption - adj_redemption, redemption])

            row = next(csv_reader)
            dist_redemption = Decimal(row[4].split(' ')[0])
            adj_redemption += dist_redemption - redemption
        else:
            redemption = Decimal(row[4])
            rows.append([date, redemption - adj_redemption, redemption])
rows.sort(key=lambda x: x[0], reverse=True)

# Write output
out_filename = Path(out_path, inp_path.name).with_suffix('.csv')
_logger.info(f'Writing "{out_filename.name}"')
with out_filename.open(mode='wt', newline='') as out:
    csv_writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['Date', 'Adj Exit', 'Exit'])
    for row in rows:
        csv_writer.writerow([f'{row[0]:%d-%m-%Y}', row[1], row[2]])

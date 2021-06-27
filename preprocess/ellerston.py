"""Transform and filter unit prices for Ellerston funds
Input 4 columns: date, application, NAV, redemption
Output 3 columns: date, redemption, and redemption adjusted
"""
import string
from datetime import date, datetime
import logging
import csv
from decimal import Decimal
from pathlib import Path
from dateutil import parser
import re

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.FileHandler('output.log', mode='w'), logging.StreamHandler()])
logging.captureWarnings(True)

# Patch known bad data in Ellerston downloaded data
patch_data_amc = {
    '16/04/0220': '16/04/2020,"Australian Micro Cap Fund",1.2698,1.2666,1.2634,Daily',
    '26/03/0202': '26/03/2020,"Australian Micro Cap Fund",1.0532,1.0506,1.0480,Daily',
    '23/01/2008': '23/01/2018,"Australian Micro Cap Fund",1.3903,1.3868,1.3833,Daily',
    '25/09/2007': '25/09/2017,"Australian Micro Cap Fund",1.1971,1.1941,1.1911,Daily',
    '28/08/2017': '28/08/2017,"Australian Micro Cap Fund",1.1853,1.1823,1.1793,Daily'
}
patch_data_gmsc = {
}
re_line = re.compile(r'(\d+(?:\.\d*)?)\s*(?:\(\s*([^)]+)\s*\))?')
re_split = re.compile(r'[\s()]+')
re_is_cum_dist = re.compile(r'\s\(\s*cum[\s-]', re.IGNORECASE)
re_is_ex_dist = re.compile(r'\s\(\s*ex[\s-]', re.IGNORECASE)


# _____________________________________________________________________________
def strip_line(iterator, patch_data):
    for ln in iterator:
        # Skip lines with no content and not starting with a digit
        if (ln := ln.strip()) and ln[0].isdigit():
            key = ln.split(',', 1)[0].strip()
            if key in patch_data:
                ln = patch_data[key]
            yield ln


# _____________________________________________________________________________
def parse_item(item: str):
    try:
        g = re_line.match(item).groups()
        redemption = Decimal(g[0])
        if s := g[1]:
            s = s.lower()
            return redemption, s.find('ex') >= 0, s.find('cum') >= 0
        else:
            return redemption, False, False
    except Exception as ex:
        raise ValueError(f' line "{item}" could not be parsed', ex)


# _____________________________________________________________________________
def process_file(inp_path: Path, patch_data: dict):
    # Initialize
    redemption, adj_redemption = Decimal(0.0), Decimal(0.0)
    distribution, dist_redemption = Decimal(0.0), Decimal(0.0)
    rows = list()

    # Process
    _logger.info(f'Reading "{inp_path.name}"')
    with inp_path.open(mode='r', newline='') as fp:
        csv_reader = csv.reader(strip_line(fp, patch_data), quoting=csv.QUOTE_MINIMAL)
        for row in csv_reader:
            if len(row) != 6:
                raise ValueError('Expecting 6 CSV values')

            date = parser.parse(row[0], dayfirst=True)
            redemption, is_dist, is_cumm = parse_item(row[4])
            if is_dist:
                rows.append([date, redemption - adj_redemption, redemption])

                row = next(csv_reader)
                price, is_dist, is_cumm = parse_item(row[4])
                if is_cumm:
                    adj_redemption += price - redemption
                elif parser.parse(row[0], dayfirst=True) == date:
                    adj_redemption += price - redemption
                else:
                    adj_redemption += price - redemption
                    rows.append([date, redemption - adj_redemption, redemption])

            else:
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


# _____________________________________________________________________________
# Setup
base_path = Path(__file__).parent
data_path = Path(base_path, 'data').resolve()
out_path = Path(base_path, 'output').resolve()
out_path.mkdir(parents=True, exist_ok=True)

# Ready input
inp_path = Path(data_path, 'ellerston-AMC.csv').resolve()
if inp_path.exists():
    process_file(inp_path, patch_data_amc)
else:
    _logger.error(f'File not found "{inp_path.name}"')

inp_path = Path(data_path, 'ellerston-GMSC.csv').resolve()
if inp_path.exists():
    process_file(inp_path, patch_data_gmsc)
else:
    _logger.error(f'File not found "{inp_path.name}"')

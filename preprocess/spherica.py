"""Transform and filter unit prices for Spherica funds

Prices are provided in PDF files.  To extract unit prices:
1. Load PDF and use "File > Save as text ..." to create text file
2. Run python script over text file to create csv file.
"""
import csv
from dateutil import parser
import logging
from pathlib import Path
import re

from pdfminer.high_level import extract_text_to_fp, extract_pages
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter, XMLConverter, TextConverter
from pdfminer.layout import LAParams
from io import StringIO


re_date = re.compile(r'([\d]{1,2}-[a-zA-Z]{3}-[\d]{2})')
re_price = re.compile(r'\$?\s*(\d+(?:\.\d+))')

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.FileHandler('output.log', mode='w'), logging.StreamHandler()])
logging.captureWarnings(True)
logging.getLogger("pdfminer").setLevel(logging.ERROR)


# _____________________________________________________________________________
def strip_line(iterator):
    for ln in iterator:
        # Skip lines with no content and not starting with a digit
        if ln := ln.strip():
            yield ln


# _____________________________________________________________________________
# Setup
base_path = Path(__file__).parent
data_path = Path(base_path, 'data').resolve()
out_path = Path(base_path, 'output').resolve()
out_path.mkdir(parents=True, exist_ok=True)

# Ready input
inp_path = Path(data_path, 'Spheria_Global_Microcap_UnitPrices-187.txt').resolve()
if not inp_path.exists():
    _logger.error(f'File not found "{inp_path.name}"')
    exit(1)

# Initialize
row, rows = list(), list()

# Process
_logger.info(f'Reading "{inp_path.name}"')
with inp_path.open(mode='r', newline='') as fp:
    for line in strip_line(fp):
        if match_price := re_price.match(line):
            row.append(match_price[1])
        elif match_date := re_date.match(line):
            if len(row) > 1:
                rows.append(row)
            row = list()
            row.append(parser.parse(match_date[1], dayfirst=True))
    if len(row) > 1:
        rows.append(row)
rows.sort(key=lambda x: x[0], reverse=True)

# Write output
out_filename = Path(out_path, inp_path.name).with_suffix('.csv')
_logger.info(f'Writing {out_filename.name}')
with out_filename.open(mode='wt', newline='') as out:
    csv_writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['Date', 'Exit'])
    try:
        for row in rows:
            csv_writer.writerow([f'{row[0]:%d-%m-%Y}', row[3]])
    except Exception as ex:
        _logger.exception(f'row {row}')

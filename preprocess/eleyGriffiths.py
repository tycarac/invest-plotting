"""Transform and filter unit prices for Eley Giffiths funds

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


re_date = re.compile(r'(20[\d]{6})')
re_price = re.compile(r'(\d+(?:\.\d+))')

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    handlers=[logging.FileHandler('output.log', mode='w'), logging.StreamHandler()])
logging.captureWarnings(True)
logging.getLogger("pdfminer").setLevel(logging.ERROR)


# _____________________________________________________________________________
def lines_iter(iter):
    with StringIO(iter) as buf:
        idx = 0
        while (ln := buf.readline().strip(' \t')) and not ln[0].isdigit():
            _logger.debug(f'skip ln "{ln.encode("unicode_escape")}"  {idx}')

        while ln:
            _logger.debug(f'ln "{ln.encode("unicode_escape")}"  {idx}')
            if ln:
                if ln[0] == '\n':
                    idx += 1
                elif ln[0] == '\f':
                    idx = 0
                elif ln[0].isdigit():
                    yield idx, ln.strip()
            ln = buf.readline().strip(' \t')


# _____________________________________________________________________________
# Setup
base_path = Path(__file__).parent
data_path = Path(base_path, 'data').resolve()
out_path = Path(base_path, 'output').resolve()
out_path.mkdir(parents=True, exist_ok=True)

# Ready input
inp_path = Path(data_path, 'Historical-Unit-Prices-ECF.pdf').resolve()
if not inp_path.exists():
    _logger.error(f'File not found "{inp_path}"')
    exit(1)

# Initialize
entries = [list() for _ in range(5)]

# Process
_logger.info(f'Reading "{inp_path.name}"')
with StringIO() as buf:
    with open(str(inp_path), 'rb') as fp:
        extract_text_to_fp(fp, buf, laparams=LAParams(), output_type='text', codec=None)
        content = buf.getvalue()

# Transform text
_logger.info(f'Transforming text')
for idx, line in lines_iter(content):
    entries[idx].append(line)
# convert string to dates
entries[0] = [parser.parse(d, dayfirst=False) for d in entries[0]]
rows = zip(entries[0], entries[1])

for r in rows:
    _logger.debug(f'> {r[0]}  {r[1]}')

# Write output
out_filename = Path(out_path, inp_path.name).with_suffix('.csv')
_logger.info(f'Writing {out_filename.name}')
with out_filename.open(mode='wt', newline='') as out:
    csv_writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
    csv_writer.writerow(['Date', 'Exit'])
    for row in rows:
        csv_writer.writerow([f'{row[0]:%d-%m-%Y}', row[2]])

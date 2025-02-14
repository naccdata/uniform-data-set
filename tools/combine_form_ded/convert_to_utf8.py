"""
Some of the CSVs are encoded in cp1252 which causes issues downstream,
this script converts them to utf-8.
"""

import logging
from pathlib import Path

log = logging.getLogger(__name__)

def convert_to_utf8(file: Path, outfile: Path) -> None:
    """Convert a file to UTF-8 if a different format.
    Really only have to worry about CP-1252 so just try-catch.

    Args:
        file: The file to check if is in UTF-8 format
        outfile: The target file to write to
    """
    contents = None

    try:
        with file.open('r', encoding='utf-8') as fh:
            contents = fh.read()

        # also check if ufeff is there and remove as needed
        if contents.startswith(u'\ufeff'):
            log.warning(f"{file} has \\ufeff character, removing")
            contents = contents.replace(u'\ufeff', '')

    except UnicodeDecodeError as e:
        log.warning(f"{file} is not UTF-8 - converting")
        with file.open('r', encoding='cp1252') as fh:
            contents = fh.read()

    # write with UTF-8 encoding
    with outfile.open('w', encoding='utf-8') as fh:
        fh.write(contents)


FORMS_DIR = Path('../../forms')

# ADD/ITERATE OVER WHICHEVER FILES YOU NEED TO CONVERT
file = FORMS_DIR / 'lbd/long/e2l/form_e2l_fvp_questions_and_vars.csv'
convert_to_utf8(file, file)  # in this case overwriting same file

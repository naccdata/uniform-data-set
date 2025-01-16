import logging
from pathlib import Path

log = logging.getLogger(__name__)

def convert_to_utf8(file: Path) -> None:
    """Convert a file to UTF-8 if a different format.
    Really only have to worry about CP-1252 so just try-catch.

    NOTE: THIS WILL OVERWRITE THE SOURCE FILE IN-PLACE IF NOT UTF-8
    """
    try:
        with file.open('r', encoding='utf-8') as fh:
            fh.read()
    except UnicodeDecodeError as e:
        log.warning(f"{file} is not UTF-8 - converting")
        contents = None
        with file.open('r', encoding='cp1252') as fh:
            contents = fh.read()

        with file.open('w', encoding='utf-8') as fh:
            fh.write(contents)

FORMS_DIR = Path('../../forms')

convert_to_utf8(FORMS_DIR / 'lbd/long/e2l/form_e2l_fvp_questions_and_vars.csv')
convert_to_utf8(FORMS_DIR / 'lbd/long/e3l/form_e3l_fvp_questions_and_vars.csv')

"""
Preps the error checks for import into REDCap.

Works almost identically to combine_form_ded.py but
works on the error checks instead.

EXTRA STEPS:

1) For LBD, you need to copy the `header` directory to
   the long and short directories as well (just don't
   check it in).
2) Filenames and error codes/packets will need to be updated since this
   script only copies files around, namely:
   - For FVP, make sure filenames say "FVP" instead of "IVP"
   - For FVP, make sure packets are the correct FVP packet 
   - For LBD 3.1, make sure error codes are `lbd3.1ivp` or `lbd3.1fvp`
      for IVP and FVP, respectively
3) Manually sync the results to S3 and import into REDCap
"""
import logging
from pathlib import Path

from convert_to_utf8 import convert_to_utf8
from form_organizer import (
    STATIC_LBD_FORMS,
    FileClassification,
    FormOrganizer,
    ModuleType,
    VisitType
)

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

MODULE_MAPPING = {
    ModuleType.ENROLLMENT: 'ENROLL'
}

FORM_VER_MAPPING = {
    ModuleType.UDS: '4.0',
    ModuleType.FTLD: '3.0',
    ModuleType.LBD_LONG: '3.0',
    ModuleType.LBD_SHORT: '3.1',
    ModuleType.ENROLLMENT: '1.0'
}

PACKET_MAPPING = {
    ModuleType.UDS: {
        VisitType.IVP: 'I',
        VisitType.FVP: 'F',
        VisitType.I4: 'I4'
    },
    ModuleType.FTLD: {
        VisitType.IVP: 'IF',
        VisitType.FVP: 'FF'
    },
    ModuleType.LBD_LONG: {
        VisitType.IVP: 'IL',
        VisitType.FVP: 'FL'
    },
    ModuleType.LBD_SHORT: {
        VisitType.IVP: 'IL',
        VisitType.FVP: 'FL'
    }
}


class ErrorCheckPreparer(FormOrganizer):
    """Class to handle preparing error checks for import"""

    def __init__(self, target_dir: str, **kwargs):
        super().__init__(**kwargs)

        # set up the target directory. follows same structure as rule defs, e.g.
        # MODULE / FORM_VER / PACKET
        self.target_dir = Path(target_dir) / MODULE_MAPPING.get(self.module, self.module.upper()) / FORM_VER_MAPPING[self.module]

        # enrollment does not have a packet
        if self.module != ModuleType.ENROLLMENT:
            self.target_dir = self.target_dir / PACKET_MAPPING[self.module][self.visit]

        self.target_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, subdir: str, file: str, file_found: bool, override_visit: str = None) -> bool:
        """If a valid error check CSV is found for the visit, copy it to the correct location.

        Args:
            subdir: The subdirectory containing this error check file
            file: The error check file to move
            file_found: Whether or not we've found an error check file for this form yet
            override_visit: The override visit

        Returns:
            True if the file was found, False otherwise
        """
        visit = override_visit if override_visit else self.visit
        if not self.is_correct_file(file, visit):
            return file_found  # return previous state

        # for LBD_SHORT we do not necessarily copy all files over, as it will just
        # use the long versions, so check if it's something we need to copy over
        if self.module == ModuleType.LBD_SHORT:
            form = subdir.split('/')[-1].strip()
            if form in STATIC_LBD_FORMS:
                return True

        # copy to target directory, updating to utf-8 as needed
        filepath = Path(subdir) / file
        log.info(f"Copying {filepath} to {self.target_dir}")
        convert_to_utf8(filepath, self.target_dir / file)
        return True


if __name__ == "__main__":

    root_dir = '../../forms'
    target_dir = './error_check_prep'

    for module in ModuleType.all():
        for visit in VisitType.all():
            if visit == VisitType.I4 and module != ModuleType.UDS:
                continue

            for error_check_type in FileClassification.error_checks():
                prep = ErrorCheckPreparer(target_dir=target_dir,
                                          root_dir=root_dir,
                                          module=module,
                                          visit=visit,
                                          classification=error_check_type)
                prep.run()

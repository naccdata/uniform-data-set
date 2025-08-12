"""
Preps the error checks for import into REDCap.

Works almost identically to combine_form_ded.py but
works on the error checks instead.

EXTRA STEPS:
1) For LBD, you need to copy the `header` directory to
   ONLY the long directory as well (just don't
   check it in).
"""
import argparse
import logging
from pathlib import Path

from convert_to_utf8 import convert_to_utf8
from form_organizer import FormOrganizer
from module_configurations import *

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)


class ErrorCheckPreparer(FormOrganizer):
    """Class to handle preparing error checks for import"""

    def __init__(self, target_dir: str, **kwargs):
        super().__init__(**kwargs)

        # set up the target directory. follows same structure as rule defs, e.g.
        # MODULE / FORM_VER / PACKET*
        self.target_dir = Path(target_dir) / MODULE_MAPPING.get(self.module, self.module.value.upper()) / FORM_VER_MAPPING[self.module]

        # not all modules have packets - only those with initial/followups
        if self.module.has_packet():
            self.target_dir = self.target_dir / PACKET_MAPPING[self.module][self.visit]

        self.target_dir.mkdir(parents=True, exist_ok=True)

    def execute(self, subdir: str, file: str, file_found: bool, override_visit: VisitType = None) -> bool:
        """If a valid error check CSV is found for the visit, copy it to the correct location.

        Args:
            subdir: The subdirectory containing this error check file
            file: The error check file to move
            file_found: Whether or not we've found an error check file for this form yet
            override_visit: The override visit

        Returns:
            True if the file was found, False otherwise
        """
        # for UDS I4, do NOT override
        visit = self.visit.value if self.visit is not None else None
        if override_visit and not (self.module == ModuleType.UDS and self.visit == VisitType.I4):
            visit = override_visit.value

        if not self.is_correct_file(file, visit):
            return file_found  # return previous state

        # UDS FVP not ready yet, only copy headers over
        if self.module == ModuleType.UDS and self.visit == VisitType.FVP:
            if not file.startswith('form_header'):
                return True

        # for LBD_SHORT we do not necessarily copy all files over, as it will just
        # use the long versions, so check if it's something we need to copy over
        if self.module == ModuleType.LBD_SHORT:
            form = subdir.split('/')[-1].strip()
            if form in STATIC_LBD_FORMS:
                return True

        # copy to target directory, updating to utf-8 as needed
        filepath = Path(subdir) / file

        # may need to replace _ivp_ with _fvp_ in filename for target filepath
        if self.visit == VisitType.FVP:
            file = file.replace(VisitType.IVP.value, VisitType.FVP.value)
        target_filepath = self.target_dir / file

        # calling convert_to_utf8 will also fix encoding issues
        # copy to self as well so we don't have non utf-8 files lingering
        log.info(f"Copying {filepath} to {target_filepath}")
        convert_to_utf8(filepath, filepath)
        convert_to_utf8(filepath, target_filepath)

        # nothing more needs to be done here if there are no packets
        if not self.module.has_packet():
            return True

        # otherwise we need to actually look at the file contents and possibly rename things
        contents = None
        with target_filepath.open('r') as fh:
            contents = fh.read()

        # make sure IVP packet names are translated to FVP packets, e.g. IF -> FF
        if self.visit == VisitType.FVP:
            ivp_packet = PACKET_MAPPING[self.module][VisitType.IVP]
            fvp_packet = PACKET_MAPPING[self.module][VisitType.FVP]

            # use commas so we don't accidentally replace a variable name or something
            contents = contents.replace(f',{ivp_packet},', f',{fvp_packet},')

        # for FVP, need to update error codes
        if self.visit == VisitType.FVP:
            ivp_code = ERROR_CODE_MAPPING[self.module][VisitType.IVP]
            fvp_code = ERROR_CODE_MAPPING[self.module][VisitType.FVP]
            contents = contents.replace(ivp_code, fvp_code)

        # for LBD SHORT (e.g. 3.1), error codes also need the 3.1 in them 
        if self.module == ModuleType.LBD_SHORT:
            target_code = ERROR_CODE_MAPPING[self.module][self.visit]

            # use the - to ensure we only change error codes
            contents = contents.replace('-lbdivp-', target_code)
            contents = contents.replace('-lbdfvp-', target_code)

        with target_filepath.open('w', encoding='utf-8') as fh:
            fh.write(contents)

        return True

    def handle_lbd_short_fvp(self, form: str, subdir: str, long_subdir: str, file_found: bool) -> bool:
        """Handles FVP LBD_SHORT specifically for error check importing generation. This
        very much depends on the form so just hardcode the cases.

        Args:
            form: The form name
            subdir: The short subdirectory
            long_subdir: The long subdirectory
            file_found: Whether or not the file was found

        Returns:
            Whether or not the file was found
        """
        # these "static" forms don't change from 3.0, so their error checks don't need to be copied over
        if form in STATIC_LBD_FORMS:
            return True

        if self.classification == FileClassification.ERROR_CHECK_MC:
            # m/c same as 3.1 IVP - b1l has its own unique M/C so not included here
            if form in ['b2l', 'b6l', 'c1l', 'b4l', 'b9l', 'e2l', 'e3l']:
                file = f'form_{form}_ivp_error_checks_mc.csv'
                file_found = self.execute(subdir, file, file_found,
                                          override_visit=VisitType.IVP)
                if not file_found:
                    raise FileNotFoundError(f"3.1 FVP LBD form {form} must grab M/C from 3.1 IVP")

        elif self.classification == FileClassification.ERROR_CHECK_P:
            # p same as 3.1 IVP
            if form in ['b4l', 'b9l', 'e2l', 'e3l']:
                file = f'form_{form}_ivp_error_checks_p.csv'
                file_found = self.execute(subdir, file, file_found,
                                          override_visit=VisitType.IVP)
                if not file_found:
                    raise FileNotFoundError(f"3.1 FVP LBD form {form} must grab P from 3.1 IVP")

            # p same as 3.0 FVP
            if form in ['b1l', 'b2l', 'b6l']:
                file = f'form_{form}_fvp_error_checks_p.csv'
                file_found = self.execute(long_subdir, file, file_found)
                if not file_found:
                    raise FileNotFoundError(f"3.1 FVP LBD form {form} must grab P from 3.0 FVP")

            # c1l specifically is same as 3.0 IVP
            if form in ['c1l']:
                file = f'form_{form}_ivp_error_checks_p.csv'
                file_found = self.execute(long_subdir, file, file_found,
                                          override_visit=VisitType.IVP)
                if not file_found:
                    raise FileNotFoundError(f"3.1 FVP LBD form {form} must grab P from 3.0 IVP")
        else:
            raise ValueError(f"Invalid classification: {self.classification}")


        # always return True because we assume it is explicitly handled (error thrown otherwise)
        return True

def main():
    parser = argparse.ArgumentParser(prog='Organizes the error check CSVs for upload to S3 and import into REDCap')
    parser.add_argument('-m', '--modules', dest='modules', type=str, required=True,
                        help="Comma-deliminated list of modules to organize CSVs for.")
    parser.add_argument('-o', '--output-dir', dest='output_dir', type=str, required=True,
                        help="Target output directory to write results to")

    args = parser.parse_args()
    log.info(f"modules:\t{args.modules}")

    for raw_module in args.modules.split(','):
        module = ModuleType(raw_module.strip())

        for visit in VisitType.all():
            if visit == VisitType.I4 and module != ModuleType.UDS:
                continue

            for error_check_type in FileClassification.error_checks():
                prep = ErrorCheckPreparer(target_dir=args.output_dir,
                                          module=module,
                                          visit=visit,
                                          classification=error_check_type)
                prep.run()


if __name__ == "__main__":
    main()

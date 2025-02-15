"""
Base class for handling the forms. The main logic handled here
is correctly iterating over the forms and grabbing the correct
alternative if a form is missing for a given context.

Will be inhereited by the DED generator and
import preparer.
"""
import os

from abc import ABC, abstractmethod
from typing import List


class VisitType:
    """Defines the visit type (initial vs followup)"""
    IVP = 'ivp'
    FVP = 'fvp'
    I4 = 'i4'  # only for UDS

    @classmethod
    def all(cls) -> List[str]:
        return [cls.IVP, cls.FVP, cls.I4]


class FileClassification:
    """File classification. Either question and var vs error check."""
    QNV = '_questions_and_vars.csv'
    ERROR_CHECK_MC = '_error_checks_mc.csv'
    ERROR_CHECK_P = '_error_checks_p.csv'

    @classmethod
    def error_checks(cls) -> List[str]:
        return [
            cls.ERROR_CHECK_MC,
            cls.ERROR_CHECK_P
        ]


class ModuleType:
    """Currently handled module types."""
    UDS = 'uds'
    FTLD = 'ftld'
    LBD_LONG = 'lbd/long'
    LBD_SHORT = 'lbd/short'
    ENROLLMENT = 'enrollment'

    @classmethod
    def all(cls) -> List[str]:
        return [
            cls.UDS,
            cls.FTLD,
            cls.LBD_LONG,
            cls.LBD_SHORT,
            cls.ENROLLMENT
        ]


STATIC_LBD_FORMS = ['b3l', 'b5l', 'b7l', 'd1l', 'e1l', 'header']


class FormOrganizer(ABC):
    """Abstract class for handling organization of forms."""

    def __init__(self,
                 root_dir: str,
                 module: ModuleType,
                 visit: VisitType,
                 classification: FileClassification):
        """Initializer

        Args:
            root_dir: Root directory of forms
            module: Module to evaluate 
            visit: Visit type to evaluate
            classification: File type to evaluate
        """
        self.root_dir = f'{root_dir}/{module}'
        self.module = module
        self.visit = visit
        self.classification = classification

    @abstractmethod
    def execute(self,
                subdir: str,
                file: str,
                file_found: bool,
                override_visit: str = None) -> bool:
        """Abstract method for subclasses to define. Performs
        the main executional function of the subclass.

        Args:
            subdir: The subdirectory containing this file
            file: The file to act on
            file_found: Whether or not we've found the given file for this form yet
            override_visit: The override visit

        Returns:
            True if the file was found, False otherwise
        """

    def is_correct_file(self, file: str, visit: str) -> bool:
        """Returns whether or not this is the correct file to process by looking
        at the filename and comparing against module/visit/classification attributes.

        Args:
            file: The file to check the filename of.
            visit: The corresponding visit

        Returns:
            Whether or not this is the correct file to process
        """
        # for enrollment, should just be a single file
        if self.module == ModuleType.ENROLLMENT:
            if not file.endswith(self.classification):
                return False

        # Check if the filename matches the pattern
        elif (not file.endswith(self.classification)  # needs to end with correct postfix
              or not file.startswith('form_')         # not a form CSV
              or f"_{visit}_" not in file):           # not a visit we care about
            return False

        return True

    @abstractmethod
    def handle_lbd_short_fvp(self, form: str, subdir: str, long_subdir: str, file_found: bool) -> bool:
        """FVP LBD_SHORT is a special case and changes depending on what exactly
        we're trying to do, so subclasses should define the behavior.

        Args:
            form: The form name
            subdir: The short subdirectory
            long_subdir: The long subdirectory
            file_found: Whether or not the file was found
        Returns:
            Whether or not the file was found
        """

    def handle_lbd(self, subdir: str, file_found: bool) -> bool:
        """Handle LBD, which needs to handle both the long and short case.

        Args:
            subdir: The subdirectory to search in
            file_found: Whether or not we've found a file for this form yet
        Returns:
            Whether or not the file was found
        """
        long_subdir = subdir.replace('short', 'long')
        form = subdir.split('/')[-1].strip()

        # LBD short does not have B8l, skip it by returning true so it doesn't
        # trigger other searches
        if self.module == ModuleType.LBD_SHORT and form == 'b8l':
            return True

        # 3. For LBD Short (3.1) FVP, grab from either LBD Short IVP OR LBD Long FVP
        if self.visit == VisitType.FVP:
            # LBD Short FVP special case
            if self.module == ModuleType.LBD_SHORT:
                file_found = self.handle_lbd_short_fvp(form, subdir, long_subdir, file_found)

            # 1. In general, for any FVP, grab from the IVP directory (this case is for LBD Long FVP)
            if not file_found:
                for file in os.listdir(subdir):
                    file_found = self.execute(subdir, file, file_found,
                                              override_visit=VisitType.IVP)

        # 2. For LBD Short (3.0) IVP, grab from LBD Long IVP
        elif self.module == ModuleType.LBD_SHORT:
            for file in os.listdir(long_subdir):
                file_found = self.execute(long_subdir, file, file_found)

        # LBD Long IVP should have had its own file, so we're done here
        return file_found

    def run(self) -> None:
        """Loop through the forms."""

        # Walk through the directory
        for subdir, dirs, files in os.walk(self.root_dir):
            dirs.sort()  # ensures order
            file_found = False

            # see if the visit file is defined for this module to begin with
            for file in files:
                file_found = self.execute(subdir, file, file_found)

            if file_found:
                continue

            # If not, we have to grab from a corresponding visit, e.g.
            #   1. In general, for any FVP, grab from the IVP directory
            #   2. For LBD Short (3.0) IVP, grab from LBD Long IVP
            #   3. For LBD Short (3.1) FVP, grab from either LBD Short IVP OR for special cases:
            #       - Look for LBD Long FVP
            #       - If not found, look at LBD Long IVP

            # Handle the LBD cases
            if self.module in [ModuleType.LBD_LONG, ModuleType.LBD_SHORT]:
                file_found = self.handle_lbd(subdir, file_found)

            # everything else should be an FVP grabbing from the IVP directory; this is
            # the last case so we don't care about the result
            if not file_found:
                for file in os.listdir(subdir):
                    self.execute(subdir, file, file_found, override_visit=VisitType.IVP)

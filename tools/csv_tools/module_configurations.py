"""
Module configurations - basically all known module properties.
"""
import os
from enum import Enum
from typing import List


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))


class VisitType(Enum):
    """Defines the visit type (initial vs followup)"""
    IVP = 'ivp'
    FVP = 'fvp'
    I4 = 'i4'  # only for UDS

    @classmethod
    def all(cls) -> List[str]:
        return [cls.IVP, cls.FVP, cls.I4]

    def __eq__(self, other):
        if isinstance(other, VisitType):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other

        return False

    __hash__ = Enum.__hash__


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


class ModuleType(Enum):
    """Currently handled module types."""
    UDS = 'uds'
    FTLD = 'ftld'
    LBD_LONG = 'lbd/long'
    LBD_SHORT = 'lbd/short'
    ENROLLMENT = 'enrollment'
    PREPROCESS = 'preprocessing'
    BDS = 'bds'
    CLS = 'cls'
    DS = 'ds'
    MILESTONES = 'milestones'
    NP = 'np'

    @classmethod
    def all(cls) -> List[str]:
        return [
            cls.UDS,
            cls.FTLD,
            cls.LBD_LONG,
            cls.LBD_SHORT,
            cls.ENROLLMENT,
            cls.PREPROCESS,
            cls.BDS,
            cls.CLS,
            cls.DS,
            cls.MILESTONES,
            cls.NP
        ]

    def has_packet(self) -> bool:
        """Checks if this module has a packet."""
        return self.value in [
            ModuleType.UDS.value,
            ModuleType.FTLD.value,
            ModuleType.LBD_LONG.value,
            ModuleType.LBD_SHORT.value,
            ModuleType.DS.value
        ]

    def __eq__(self, other):
        if isinstance(other, ModuleType):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other

        return False

    __hash__ = Enum.__hash__


STATIC_LBD_FORMS = ['b3l', 'b5l', 'b7l', 'd1l', 'e1l', 'header']

# for those whose modlue name/location does not match
# the form directory name
MODULE_MAPPING = {
    ModuleType.LBD_LONG: 'LBD',
    ModuleType.LBD_SHORT: 'LBD',
    ModuleType.ENROLLMENT: 'ENROLL',
    ModuleType.PREPROCESS: 'PREPROCESS'
}

FORM_VER_MAPPING = {
    ModuleType.UDS: '4.0',
    ModuleType.FTLD: '3.0',
    ModuleType.LBD_LONG: '3.0',
    ModuleType.LBD_SHORT: '3.1',
    ModuleType.ENROLLMENT: '1.0',
    ModuleType.PREPROCESS: '1.0',
    ModuleType.BDS: '1.0',
    ModuleType.CLS: '3.0',
    ModuleType.DS: '1.0',
    ModuleType.MILESTONES: '3.0',
    ModuleType.NP: '11.0'
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
    },
    ModuleType.DS: {
        VisitType.IVP: 'IDS',
        VisitType.FVP: 'FDS'
    }
}

ERROR_CODE_MAPPING = {
    ModuleType.UDS: {
        VisitType.IVP: '-ivp-',
        VisitType.FVP: '-fvp-',
        VisitType.I4: '-i4vp-'
    },
    ModuleType.FTLD: {
        VisitType.IVP: '-ftldivp-',
        VisitType.FVP: '-ftldfvp-'
    },
    ModuleType.LBD_LONG: {
        VisitType.IVP: '-lbdivp-',
        VisitType.FVP: '-lbdfvp-'
    },
    ModuleType.LBD_SHORT: {
        VisitType.IVP: '-lbd3.1ivp-',
        VisitType.FVP: '-lbd3.1fvp-'
    },
    ModuleType.DS: {
        VisitType.IVP: '-ivp-',
        VisitType.FVP: '-fvp-'
    },
}

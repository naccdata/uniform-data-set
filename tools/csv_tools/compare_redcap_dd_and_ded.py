"""
Compares the exported REDCap Data Dictionary with RT-generated DED.

REDCap project might have extra local variables (usually identifiable
by prefixes like instr_, desc_, loc_, etc.) and are ignored. All
others should match. 
"""
from pathlib import Path

from combine_form_ded import main as combine_form_ded_main
from module_configurations import ModuleType, VisitType


def main(redcap_dd: str, ded: str):
    redcap_dd = Path(redcap_dd)
    ded = Path(ded)
    for file in [redcap_dd, ded]:
        if not file.is_file():
            raise FileNotFoundError(f"Cannot find file: {file}")


if __name__ == "__main__":

    redcap_dd = "PATH TO REDCAP DD"
    ded = "PATH TO DED, if set to None, can generate using below"

    # SET THESE IF YOU NEED THE DED GENERATED
    if not ded:
        module = ModuleType.UDS
        visit = VisitType.IVP
        target_dir = './work/combined_ded'
        ded = combine_form_ded_main(module, visit, target_dir)

    main(redcap_dd, ded)

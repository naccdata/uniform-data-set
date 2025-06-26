"""
Compares the exported REDCap Data Dictionary with RT-generated DED.

REDCap project might have extra local variables (usually identifiable
by having a _ in the variable name)
and are ignored. All others should match. 
"""
import csv
import json
from typing import Dict, List
from pathlib import Path

from combine_form_ded import main as combine_form_ded_main
from module_configurations import ModuleType, VisitType


# REDCap DD column names to DED column names
REDCAP_KEY = "Variable / Field Name"
DED_KEY = "var_name"

REDCAP_TO_DED_MAPPING = {
    REDCAP_KEY: DED_KEY,
    "Field Label" : "question",  # form headers do not need leading question number
    "Choices, Calculations, OR Slider Labels": "response_labels",
}

# prefixes to ignore
IGNORE_PREFIXES = [
]


def load_data_file(file: Path, key_field: str, fields: List[str]) -> Dict[str, str]:
    """Load data files; only keep fields we're checking."""
    if not file.is_file():
        raise FileNotFoundError(f"Cannot find file: {file}")

    result = {}

    with file.open('r', encoding='utf-8-sig') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            data = {k: v.strip() for k,v in row.items() if k in fields}

            # also denote in REDCap if it's form header
            if key_field == REDCAP_KEY:
                data['form_header'] = row['Form Name'].strip() == 'form_header'

            result[row[key_field]] = data

    return result


def main(redcap_dd: str, ded: str):
    """Run the comparison process."""
    redcap_data = load_data_file(Path(redcap_dd), REDCAP_KEY, list(REDCAP_TO_DED_MAPPING.keys()))
    ded_data = load_data_file(Path(ded), DED_KEY, list(REDCAP_TO_DED_MAPPING.values()))

    results = {
        'in_redcap_not_in_ded': [],
        'in_ded_not_in_redcap': [],
        'mismatch': []
    }

    # redcap data will always be larger, so iterate on that
    for redcap_var, redcap_row in redcap_data.items():
        if '_' in redcap_var or any(redcap_var.startswith(x) for x in IGNORE_PREFIXES):
            continue

        if redcap_var not in ded_data:
            results['in_redcap_not_in_ded'].append(redcap_var)
            continue

        # pop so we check DED data is empty at end (all match)
        ded_row = ded_data.pop(redcap_var)

        # compare
        form_header = redcap_row.pop('form_header')
        for k, v in redcap_row.items():
            ded_k = REDCAP_TO_DED_MAPPING[k]
            ded_v = ded_row[ded_k].replace(" | ", "|")

            # if no response label, ignore
            if k == 'Field Label' and not ded_v:
                continue

            if not v.replace(" ", "") == ded_v.replace(" ", ""):
                # if form header and field is field label, may not have leading numbers
                if form_header and ded_v.startswith('0') and ded_v.endswith(v):
                    continue

                results['mismatch'].append({
                    redcap_var: {
                        "redcap_mismatch_field": k,
                        "redcap_value": v,
                        "ded_mismatch_field": ded_k,
                        "ded_value": ded_v
                    }
                })

    # means not in REDCap DD
    if ded_data:
        results['in_ded_not_in_redcap'].extend(list(ded_data.keys()))

    print(json.dumps(results, indent=4))

if __name__ == "__main__":

    redcap_dd = "./work/redcap_comparison/Milestones_DataDictionary_2025-06-26.csv"
    ded = None # PATH TO DED, if set to None, can generate using below

    # SET THESE IF YOU NEED THE DED GENERATED
    if not ded:
        module = ModuleType.MILESTONES
        visit = None
        target_dir = './work/combined_ded'
        ded = combine_form_ded_main(module, visit, target_dir)

    main(redcap_dd, ded)

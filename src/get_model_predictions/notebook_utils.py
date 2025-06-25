import pandas as pd
import numpy as np

STANCE_NUM_MAP = {"supports": 5,
                    "insufficient-supports": 4,
                    "insufficient-neutral": 3,
                    "insufficient-contradictory": 3,
                    "insufficient-refutes": 2,
                    "refutes": 1,
                    "not_applicable": 100}

VERDICT_NUM_MAP = {"True": 5,
                    "Half True": 4,
                    "False": 1}

PREDS_MAP = {True: "True",
                False: "False",
                "Pants on Fire": "False",
                "Pants on Fire!": "False",
                "Yes": "True",
                "No": "False",
                "Not sure": "None",
                "True": "True",
                "False": "False",
                "None": "None",
                "Support": "True",
                "Refute": "False",
                "Supports": "True",
                "Refutes": "False",
                "Disputed": "None",
                "Not enough information": "None"
                }

PREDS_STANCE_MAP = {"True": "supports",
                        "False": "refutes",
                        "None": "insufficient-neutral",
                        }

def load_data(full_data_filepath, data_paths, data_preds_paths = {}):
    if full_data_filepath.endswith(".tsv"):
        data = pd.read_csv(full_data_filepath, sep="\t").set_index("id")
    else:
        data = pd.read_csv(full_data_filepath).set_index("id")
        
    # this column should be obsolete and will be loaded from properties at a later stage
    if "is_factcheck_article" in data.columns:
        data = data.drop(columns=["is_factcheck_article"])
    
    def add_data_cols(data, data_path, suffix=""):
        print(f"Loading data from {data_path}:")
        sep = "\t" if data_path.endswith(".tsv") else ","
        tmp_data = pd.read_csv(data_path, sep=sep, keep_default_na=False, na_values=[" ", ""]).set_index("id")
        new_cols = [col for col in tmp_data.columns if (col not in data.columns and "Unnamed" not in col)]
        print(f"Adding column values for {new_cols}")
        data = data.merge(tmp_data[new_cols], how="left", left_index=True, right_index=True)
        data = data.rename(columns={col: col+suffix for col in new_cols})
        
        return data
        
    for data_path in data_paths: 
        data = add_data_cols(data, data_path)
    
    for prompt, data_path in data_preds_paths.items():
        data = add_data_cols(data, data_path, "_"+prompt)
        
    data = data.replace({np.nan: None}) # handle annoying nan approach by pandas
    return data


def preprocess_data(data):
   # add claim source metadata    
    claim_sources = ["borderlines", "checkyourfact", "factcheckni", "factly", "politifact", "sciencefeedback", "healthfeedback", "climatefeedback", "srilankafactcrescendo"]
    def get_claim_source(claim_id):
        for claim_source in claim_sources:
            if claim_source in claim_id:
                return claim_source
    data["claim_source"] = data.claim_id.apply(get_claim_source)
    
    # map verdict and stance values to continuous space
    data["evidence_stance_num"] = data.evidence_stance.map(STANCE_NUM_MAP)
    data["factcheck_verdict_num"] = data.factcheck_verdict.map(VERDICT_NUM_MAP)
    
    data = data.replace({np.nan: None}) # handle annoying nan approach by pandas
    return data

def unfold_wo_evidence_preds(data, prediction_wo_evidence_col):
    # unfold wo_evidence predictions across all claims
    for claim_id in data.claim_id.unique():
        claim_ix = data[data.claim_id==claim_id].index
        non_na_values = data.loc[claim_ix][prediction_wo_evidence_col].dropna()
        if len(non_na_values) > 0:
            assert len(non_na_values) == 1, f"There should only be one prediction corresponding to one claim, got multiple for {claim_id} ({non_na_values})."
            prediction_wo_evidence = non_na_values.iloc[0]
            data.loc[claim_ix, prediction_wo_evidence_col] = prediction_wo_evidence
        
    return data

def preprocess_preds(data, prediction_col):
    data[prediction_col + "_orig"] = data[prediction_col].copy()
    # map prediction values to same space as factcheck_verdict
    data[prediction_col] = data[prediction_col].map(PREDS_MAP)
    # map prediction values to same space as stance (string value)
    data[prediction_col + "_stance"] = data[prediction_col].map(PREDS_STANCE_MAP)
    # map pred values to continuous space
    data[prediction_col + "_stance_num"] = data[prediction_col + "_stance"].map(STANCE_NUM_MAP)
    
    data = data.replace({np.nan: None}) # handle annoying nan approach by pandas
    return data
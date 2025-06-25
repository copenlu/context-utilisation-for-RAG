from pathlib import Path
import pandas as pd

def get_claim(row):
    claim = row.base_prompt + row.target_new + "."
    return claim

def get_refuting_evidence(row):
    evidence = row.evidence.replace(row.target_new, row.target_true)
    return evidence

if __name__ == "__main__":    
    import argparse
    parser = argparse.ArgumentParser(description="Recast CounterFact dataset by Ortu et al. to our claim-evidence format.")
    parser.add_argument("--data_path", type=str, help="Path to file with CounterFact data.")
    parser.add_argument("--save_file", type=str, help="File to save the results to.")
    
    args = parser.parse_args()
    
    data = pd.read_json(args.data_path)
    print(f"{len(data)} samples loaded.")
    print()

    # get supporting evidence representing knowledge conflicts
    data["claim"] = data.apply(get_claim, axis=1)
    data["evidence"] = data.claim.copy() # the evidence is the claim, we skip the "Redefine" command here.
    data["evidence_stance"] = "supports"
    data["relevant"] = True
    data["factcheck_verdict"] = False
    data["claim_id"] = [f"counterfact_{i}" for i in range(len(data))]
    data["id"] = data.claim_id.apply(lambda val: val + "_sup")
    
    # get refuting evidence representing model memory
    ext_data = data.copy()
    ext_data["evidence"] = ext_data.apply(get_refuting_evidence, axis=1)
    ext_data["evidence_stance"] = "refutes"
    ext_data["id"] = ext_data.claim_id.apply(lambda val: val + "_ref")
    
    data = pd.concat((data, ext_data))
    data = data.set_index("id")
    data.sort_index().to_csv(args.save_file, sep="\t")
    print(f"Done! Saved recast data to '{args.save_file}'.")
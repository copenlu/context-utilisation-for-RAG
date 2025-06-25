from pathlib import Path
import pandas as pd

def get_verdict(row):
    for ok_answer in row.ground_truth:
        if ok_answer in row.memory_answer:
            return True
    return False

if __name__ == "__main__":    
    import argparse
    parser = argparse.ArgumentParser(description="Recast conflictQA dataset by Xie et al. to our claim-evidence format.")
    parser.add_argument("--data_path", type=str, help="Path to file with conflictQA data.")
    parser.add_argument("--save_file", type=str, help="File to save the results to.")
    
    args = parser.parse_args()
    
    data = pd.read_json(args.data_path, lines=True)
    print(f"{len(data)} samples loaded.")
    print()

    # get supporting evidence representing knowledge conflicts
    data_list = []
    missing_entries = []
    for ix, row in data.iterrows():
        if row.memory_answer.strip() is not None and len(row.memory_answer.strip()) > 0:
            data_entry_memory = {"claim": row.memory_answer.strip(),
                                 "factcheck_verdict": get_verdict(row),
                                 "evidence": row.parametric_memory_aligned_evidence.strip(),
                                 "evidence_stance": "supports",
                                 "evidence_source": "ChatGPT/Wikipedia/human",
                                 "relevant": True,
                                 "claim_id": f"conflictqa_llama_{ix}",
                                 "id": f"conflictqa_llama_{ix}_sup"}
            data_list.append(data_entry_memory)
            
            data_entry_conflicting = {"claim": row.memory_answer.strip(),
                                      "factcheck_verdict": get_verdict(row),
                                      "evidence": row.counter_memory_aligned_evidence.strip(),
                                      "evidence_stance": "refutes",
                                      "evidence_source": "ChatGPT/Wikipedia/human",
                                      "relevant": True,
                                      "claim_id": f"conflictqa_llama_{ix}",
                                      "id": f"conflictqa_llama_{ix}_ref"}
            data_list.append(data_entry_conflicting)
        else:
            missing_entries.append(ix)
            
    print(f"Found {len(missing_entries)} samples with missing entries ({missing_entries}). Skipping these.")
    
    data = pd.DataFrame(data_list)
    data = data.set_index("id")
    data.sort_index().to_csv(args.save_file, sep="\t")
    print(f"Done! Saved recast data to '{args.save_file}'.")
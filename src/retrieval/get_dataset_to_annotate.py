import os
import math
import pandas as pd

def get_potato_text_field(data_entry):
    text_cols = ["claimant", "claim_date", "claim", "evidence_date", "evidence"]
    text = ""
    for col in text_cols:
        text += f"<b> {col.capitalize().replace('_', ' ')}: </b> {data_entry[col]} <br> "
    text = text[:-len(" <br> ")]
    # make multiple evidence pieces easier to read for annotators
    text = text.replace("[...]", "<br> <br>")
    return text

def get_dataset_to_annotate(auto_evidence_path, source_claims_path, save_folder, n_claims, n_claims_per_batch):
    print()
    
    auto_evidence_data = pd.read_csv(auto_evidence_path).set_index("id")
    claim_ids_with_auto_evidence = auto_evidence_data.claim_id.unique()
    print(f"Loaded {len(claim_ids_with_auto_evidence)} auto retrieved evidence samples corresponding to {len(claim_ids_with_auto_evidence)} claims.")
    avg_n_auto_evidence_per_claim = auto_evidence_data.groupby(["claim_id"]).evidence.count().mean()
    print(f"For which each claim corresponds to {avg_n_auto_evidence_per_claim:.2f} evidence pieces on average.")
    print()
    
    gold_data = pd.read_csv(source_claims_path).set_index("id")
    print(f"Loaded {len(gold_data)} source claims from '{source_claims_path}'.")
    print(f"Dropping {len(gold_data)-len(claim_ids_with_auto_evidence)} claims for which sufficient auto evidence was not found.")
    gold_data = gold_data.loc[claim_ids_with_auto_evidence]
    print()

    if n_claims is not None:
        if len(gold_data) < n_claims:
            print(f"Warning: There are not enough claim samples ({len(gold_data)}) to meet the desired number of claims ({n_claims}). Will instead collect all available claims.")
            n_claims = len(gold_data) 
    else:
        n_claims = len(gold_data)

    print(f"Collecting {n_claims} claims for the annotation dataset:")
    # there are generally few claims that are 'true' or 'half-true'. Prioritise the collection of these.
    if not (False in gold_data.factcheck_verdict or "False" in gold_data.factcheck_verdict):
        # bordelines does not correspond to verdicts, just sample these
        claims_to_include = gold_data.sample(n=n_claims, replace=False, random_state=42).index.tolist()
    else:
        claims_to_include = gold_data[gold_data.factcheck_verdict.isin(["True", "Half True", True])].index.tolist()
        remaining_claims_to_include = n_claims-len(claims_to_include)
        claims_to_include += gold_data[(gold_data.factcheck_verdict=="False") | (gold_data.factcheck_verdict==False)]\
            .sample(n=remaining_claims_to_include, replace=False, random_state=42).index.tolist()
    gold_data = gold_data.loc[claims_to_include]
    auto_evidence_data = auto_evidence_data[auto_evidence_data.claim_id.isin(claims_to_include)]
    print("Fact-check verdict distribution: of claims included in the annotation dataset:")
    print(gold_data.factcheck_verdict.value_counts())
    print()
    
    print("Merging the auto retrieved evidence with the gold evidence:")
    cols_to_include_in_annotation_data = ["claim_id", 
                                          "claim", 
                                          "claimant", 
                                          "claim_date", 
                                          "evidence_source", 
                                          "evidence", 
                                          "evidence_date", 
                                          "factcheck_verdict",
                                          "is_factcheck_article",
                                          "evidence_published_after_claim",
                                          "is_gold"]
    
    # add necessary columns to gold data
    gold_data = gold_data.drop(columns=["evidence_source"])
    gold_data = gold_data.rename(columns={"factcheck_url": "evidence_source",
                                          "date": "claim_date"})
    gold_data["claim_id"] = gold_data.index.copy()
    gold_data["evidence_date"] = gold_data.claim_date.copy()
    gold_data["is_factcheck_article"] = True
    gold_data["evidence_published_after_claim"] = True
    gold_data["is_gold"] = True
    gold_data = gold_data[cols_to_include_in_annotation_data]
    
    # add necessary columns to auto evidence data
    auto_evidence_data = auto_evidence_data.rename(columns={"link": "evidence_source",
                                                            "is_fact_check_article": "is_factcheck_article"})
    auto_evidence_data["factcheck_verdict"] = auto_evidence_data.claim_id.apply(lambda val: gold_data.loc[val].factcheck_verdict)
    auto_evidence_data["is_gold"] = False
    auto_evidence_data = auto_evidence_data[cols_to_include_in_annotation_data]
    
    annotation_data = pd.concat([gold_data, auto_evidence_data])
    print(f"Compiled a total of {len(annotation_data)} samples to be annotated corresponding to {len(annotation_data.claim_id.unique())} claims.")
    print()
    
    print("Adding metadata necessary for the potato annotation server ('text'):")
    annotation_data["text"] = annotation_data.apply(get_potato_text_field, axis=1)
    print()
    
    if n_claims_per_batch is not None:
        n_batches = math.ceil(n_claims/n_claims_per_batch)
    else:
        # skip batching if no batches provided
        n_batches = 1
        n_claims_per_batch = len(claims_to_include)
        
    print(f"Storing data in {n_batches} batches.")
    for batch_ix in range(n_batches):
        save_file = os.path.join(save_folder, f"dataset_to_annotate_{batch_ix+1}.tsv")
        lower_claim_bound = batch_ix*n_claims_per_batch
        upper_claim_bound = min(len(claims_to_include), (batch_ix+1)*n_claims_per_batch)
        claims_in_batch = claims_to_include[lower_claim_bound:upper_claim_bound]
        annotation_data[annotation_data.claim_id.isin(claims_in_batch)].sort_values(by=["claim_id","id"]).to_csv(save_file, sep="\t")
    print(f"Done! A total of {len(annotation_data)} samples have been saved to '{save_folder}'.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get dataset to annotate")
    parser.add_argument("--auto_evidence_path", type=str, required=True, help="Path to the automatically retrieved CSV file")
    parser.add_argument("--source_claims_path", type=str, required=True, help="Path to source claims CSV file")
    parser.add_argument("--save_folder", type=str, required=True, help="Folder to save the data to")
    parser.add_argument("--n_claims", type=int, default=None, help="Number of claims to include in the annotation dataset")
    parser.add_argument("--n_claims_per_batch", type=int, default=None, help="The data will be batched, if necessary, based on the number of claims to include per batch")
    
    args = parser.parse_args()
    
    results_file = os.path.join(args.save_folder, "dataset_to_annotate_1.tsv")
    if os.path.isfile(results_file):
        print(f"A results file already exists for this script. ('{results_file}')")
        print("Remove it if you want to rerun the script.")
    else:
        os.makedirs(args.save_folder, exist_ok=True)
        get_dataset_to_annotate(args.auto_evidence_path, 
                                args.source_claims_path,
                                args.save_folder,
                                args.n_claims,
                                args.n_claims_per_batch)
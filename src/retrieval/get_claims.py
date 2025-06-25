import os
import re
import pandas as pd

# ["checkyourfact.com", "climatefeedback.org", "factcheckni.org", \
#                   "factly.in", "healthfeedback.org", "srilanka.factcrescendo.com"]
# target_site = "srilanka.factcrescendo.com"
# filename = "../../../data/claims/%s_2.csv" %(target_site)

DATE_SHARES = {('1900', '2023'): 0.5, ('2023', '2025'): 0.5} # [.,.)
# DATE_SHARES = {('1900', '2025'): 1.0}
VERDICT_SHARES = {"True": 0.4, "Half True": 0.2, "False": 0.4}

PROBLEMATIC_LINK_TAGS = ["-dnc", "-rnc"]
PROBLEMATIC_CLAIM_WORDS = ["photo", "image", "video"]

def get_id(row):
    site_name = ("").join(row.factcheck_site.split(".")[:-1])
    ix = f"{site_name}_{row.name}"
    return ix

def get_claims(claim_data_path, save_folder, n_claims_to_include, sample_all):
    # the claim data files contain duplicated indeces, let the order decide the index instead
    data = pd.read_csv(claim_data_path).reset_index(drop=True)
    data = data.drop_duplicates(["claim"])
    
    # reformat dates
    data["date"] = pd.to_datetime(data.date).dt.strftime('%Y-%m-%d')
    data = data.sort_values(by="date")
    data["date_year"] = pd.to_datetime(data.date).dt.strftime('%Y')
    
    # remove potentially problematic claims (in which the fact check article refers to another article)
    problematic_samples_url_mask = data.factcheck_url.apply(
        lambda val: any([tag in val for tag in PROBLEMATIC_LINK_TAGS]))
    data = data[~problematic_samples_url_mask]
    problematic_samples_claim_mask = data.claim.apply(
        lambda val: any([w in val.lower() for w in PROBLEMATIC_CLAIM_WORDS]))
    data = data[~problematic_samples_claim_mask]

    print(f"Processing {len(data)} claims after removal of duplicates and problematic samples.")
    print(f"Input data date and veractiy distribution:")
    print(data.value_counts(["date_year", "factcheck_verdict"]))
    print()
    
    print(f"Warning: less samples than specified ('{n_claims_to_include}') can be found, trying to sample from those available.")
    print()

    if sample_all:
        print("Simply sampling all available data points.")
    else:
        print("Sampling data points according to the desired distribution:")
        choose_ix = []
        for t_interval, t_share in DATE_SHARES.items():
            extra_false_samples = 0
            for verdict, v_share in VERDICT_SHARES.items():
                num_samples = int(n_claims_to_include * t_share * v_share)
                if verdict == 'False':
                    num_samples += extra_false_samples
                share_mask = (data.date >= t_interval[0]) & (data.date < t_interval[1]) & (
                            data.factcheck_verdict == verdict)
                n_matching_samples = len(data[share_mask])

                if n_matching_samples < num_samples:

                    try:
                        assert verdict != 'False', "Cannot fulfil distribution requirements - too few samples with verdict 'False'"
                    except:
                        if verdict == "True":
                            pass

                    lacking_num_samples = num_samples - n_matching_samples
                    print(
                        f"Warning: Too few samples between dates {t_interval} with the verdict '{verdict}'.")
                    print(
                        f"Sampling max available ({n_matching_samples}) and rest ({lacking_num_samples}) from verdict='False' ().")
                    extra_false_samples += lacking_num_samples
                    num_samples = n_matching_samples
                choose_ix.extend(data[share_mask].index[:num_samples])
        data = data.loc[choose_ix]
    print()
        
    # set IDs
    data["id"] = data.apply(get_id, axis=1)
    data = data.set_index("id")

    print("Distribution of fact-check verdicts")
    print(data.value_counts(["factcheck_verdict"]))
    print()

    print("Distribution of claim dates:")
    print(data.date_year.value_counts(sort=False))
    print()

    data["evidence"] = data.evidence.apply(lambda val: re.sub(' +', ' ', val.replace("\n"," ").replace(u'\xa0', u' ').replace("•","")).strip())
    data = data.sort_index()
    print("Number of Sampled claims:", len(data))
    data.to_csv(os.path.join(save_folder, "gold_samples.csv"))
    print(f"Done! Data saved in '{save_folder}.'")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Get a dataset with gold sample claims and evidence according to our desired distribution")
    parser.add_argument("--claim_data_path", type=str, required=True, help="Path to the crawl results CSV file")
    parser.add_argument("--save_folder", type=str, required=True, help="Folder to save the data to")
    parser.add_argument("--n_claims_to_include", type=int, default=300, help="Number of claims to include in the dataset")
    parser.add_argument("--sample_all", action="store_true", default=False, help="Whether to just take all samples available, instead of following the desired distribution.")

    args = parser.parse_args()
    
    results_file = os.path.join(args.save_folder, "gold_samples.csv")
    if os.path.isfile(results_file):
        print(f"A results file already exists for this script. ('{results_file}')")
        print("Remove it if you want to rerun the script.")
    else:
        os.makedirs(args.save_folder, exist_ok=True)
        get_claims(args.claim_data_path, args.save_folder, args.n_claims_to_include, args.sample_all)
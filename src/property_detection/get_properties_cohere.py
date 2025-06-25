# move stuff from notebook to here
from pathlib import Path
import os
import time
from tqdm import tqdm
import pandas as pd
import cohere

with open("API-keys/cohere-api-key.txt") as f:
    cohere_api_key = f.readline().strip()
    
co = cohere.ClientV2(cohere_api_key)

PROMPTS = {"refers_external_source": 'Does the following text refer to an external source or not? Admissible external sources are for example "a study", "[1]", "the BBC", a news channel etc. Answer with a "Yes" or "No".\n\nText: <text>',
        #    "difficult_to_understand": 'Is the following text difficult to understand? Answer with a "Yes" or "No".\n\nText: <text>', # model always predicted 'No'
        #    "difficult_to_understand": 'Is the following text potentially difficult to understand due to complicated words, long sentences, strange phrasings etc.? Answer with a "Yes" or "No".\n\nText: <text>',
           "unreliable": 'Does the following text seem unreliable? It could for example be due to the presentation of information that contradicts your prior knowledge or commonsense. Answer with a "Yes" or "No".\n\nText: <text>',
           "uncertain": 'Does the following text appear uncertain? It could for example be due to the inclusion of hedging terms such as "might", "maybe" etc. Answer with a "Yes" or "No".\n\nText: <text>',
           "implicit": 'Consider the claim and corresponding evidence below. Is the evidence only relevant to the claim if one has to assume that the evidence is implicitly referring to the same topics or entities as the claim under consideration? Implicit evidence can include, among others, the use of pronouns instead of specific names or more specific statements instead of a general statement made in a claim. Answer with a "Yes" or "No".\n\nClaim: "<claim>"\nEvidence: "<evidence>"'
           }

def get_properties_cohere(data, prop, save_file):
    # initialize save file
    with open(save_file, "w") as f:
        f.write(f"id\t{prop}_cohere\n")
    
    error_ix = []        
    for ix, row in tqdm(data.iterrows(), total=len(data)):
        if prop != "implicit":
            query = PROMPTS[prop].replace("<text>", row.evidence)
        else:
            query = PROMPTS[prop].replace("<claim>", row.claim).replace("<evidence>", row.evidence)
        try:
            response = co.chat(
            model="command-r-plus",
            messages=[
                    {
                    "role": "user",
                    "content": query
                    }
                ]
            )
            pred = response.message.dict()['content'][0]['text'].strip(".")
            with open(save_file, "a") as f:
                f.write(f"{ix}\t{pred}\n")
        except Exception as e:
            print(f"Error: Could not fetch prediction for {ix}.")
            print(e)
            print()
            print("reponse:")
            print(response.dict())
            print()
            error_ix.append(ix)
            
        # rate limit for cohere chat is 500/min
        time.sleep(0.12)
        
    print(f"Cohere processing of '{prop}' done!")
    print()
    print("Failed to fetch results for the following indeces:")
    print(error_ix)
    return

if __name__ == "__main__":    
    import argparse
    parser = argparse.ArgumentParser(description="Auto detect properties for DRUUID using Cohere chat.")
    parser.add_argument("--data_path", type=str, help="Path to .tsv file with data to detect properties for. Should contain the columns 'claim' and 'evidence'.")
    parser.add_argument("--save_folder", type=str, help="Folder to save the results to.")
    parser.add_argument("--properties", type=str, help="String with properties to detect, separated by spaces. Choose either 'all' or any combination of 'refers_external_source', 'unreliable', 'uncertain' or 'implicit'.")
    parser.add_argument("--start_index", type=int, default=0, help="Index to start from. Useful if a previous run has crashed and you wish to resume, just make sure to save the previous results to another file as they otherwise will be overwritten.")
    
    args = parser.parse_args()
    
    Path(args.save_folder).mkdir(exist_ok=True, parents=True)
    
    data = pd.read_csv(args.data_path, sep="\t").set_index("id").iloc[args.start_index:]
    print(f"{len(data)} samples loaded.")
    print()

    if args.properties == "all":
        properties = PROMPTS.keys()
    else:
        properties = args.properties.split()
        
    for prop in properties:
        print(f"Processing property {prop}...")
        save_file = os.path.join(args.save_folder, f"{prop}_cohere.tsv")
        get_properties_cohere(data, prop, save_file)
    
    print(f"Done! Saved properties to '{args.save_folder}'.")
    
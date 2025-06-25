## from https://huggingface.co/docs/transformers/perplexity
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
from tqdm import tqdm
import sys
import os

if __name__ == '__main__':

    MODEL_NAME = sys.argv[1]
    DATASET_NAME = sys.argv[2]
    include_eos = False #bool(sys.argv[2])
    
    # create the save folder if it does not exist
    SAVEFOLDER = "data/property_detection/ppl"
    os.makedirs(SAVEFOLDER, exist_ok=True)

    stride = 512

    assert MODEL_NAME in ['openai-community/gpt2','EleutherAI/pythia-6.9b','meta-llama/Llama-3.1-8B-Instruct']

    MODEL_SHORT = MODEL_NAME.split('/')[1].split('-')[0]
    print(MODEL_SHORT)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    model = model.to(device)

    if 'gpt' in MODEL_NAME: #### UNSURE FOR PYTHIA
        max_length = model.config.n_positions ## for GPT models
    else:
        max_length = model.config.max_position_embeddings ## for LLAMA

    ppls = []

    ## LOAD DATASET
    ds = pd.read_csv(DATASET_NAME,sep="\t")

    for index, row in tqdm(ds.iterrows()):
        encodings = tokenizer(row['evidence'], return_tensors="pt")

        seq_len = encodings.input_ids.size(1) #- 1
        if not include_eos:
            seq_len -= 1

        nlls = []
        prev_end_loc = 0
        for begin_loc in tqdm(range(0, seq_len, stride)):
            end_loc = min(begin_loc + max_length, seq_len)
            trg_len = end_loc - prev_end_loc  # may be different from stride on last loop
            input_ids = encodings.input_ids[:, begin_loc:end_loc].to(device)
            target_ids = input_ids.clone()
            target_ids[:, :-trg_len] = -100

            with torch.no_grad():
                outputs = model(input_ids, labels=target_ids)

                # loss is calculated using CrossEntropyLoss which averages over valid labels
                # N.B. the model only calculates loss over trg_len - 1 labels, because it internally shifts the labels
                # to the left by 1.
                neg_log_likelihood = outputs.loss

            nlls.append(neg_log_likelihood)

            prev_end_loc = end_loc
            if end_loc == seq_len:
                break

        ppl = torch.exp(torch.stack(nlls).mean()).cpu().item()
        ppls.append(ppl)
        
    ds['ppl'] = ppls

    ds.to_csv(os.path.join(SAVEFOLDER, f'ppl_{MODEL_SHORT}_{DATASET_NAME}_{include_eos}.csv'))
import os
import torch
import argparse
import random
import numpy as np
import transformers
import pandas as pd
from tqdm import tqdm

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, GenerationConfig
from datasets import Dataset
from transformers.pipelines.pt_utils import KeyDataset
from torch.nn.functional import softmax

from src.get_model_predictions.utils import TextWithLogitsGenerationPipeline
from src.get_model_predictions.prompts import PROMPT_DICT

torch.backends.cuda.enable_mem_efficient_sdp(False)
torch.backends.cuda.enable_flash_sdp(False)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def enforce_reproducibility(seed=1000):

    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    random.seed(seed)
    np.random.seed(seed)

def get_prompt(row, prompt_template, use_evidence):
    prompt = prompt_template.replace("<claim>", row['claim'])
    if "<claimant>" in prompt:
        prompt = prompt.replace("<claimant>", row['claimant'])
        
    if use_evidence:
        prompt = prompt.replace("<evidence>", row['evidence'])
    return prompt

def predict_veracity(file_path:str, save_folder:str, use_evidence:str, model_code:str, prompt_name:str, cache_folder:str)-> None:
    '''
    Function to predict the stance for claim, evidence pairs read from a file
    Args:
    file_path: Path to the file containing the claims and evidence
    '''
    tokenizer = AutoTokenizer.from_pretrained(model_code, cache_dir=cache_folder)
    model = AutoModelForCausalLM.from_pretrained(model_code,
            # quantization_config=bnb_config,
            # torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True,
            cache_dir=cache_folder)
    tokenizer.pad_token = tokenizer.eos_token
    
    if file_path.endswith(".tsv"):
        data = pd.read_csv(file_path, sep="\t").set_index("id")
    elif file_path.endswith(".csv"):
        data = pd.read_csv(file_path).set_index("id")
    else:
        raise ValueError(f"Can only handle .tsv or .csv files, got '{file_path}'.")
    prompt_template = PROMPT_DICT[prompt_name]
    
    if use_evidence == 'yes':
        assert "<evidence>" in prompt_template
        print("Using evidence")
        use_evidence = True
    else:
        assert "<evidence>" not in prompt_template
        print("Not using evidence")
        use_evidence = False
        # if we are not considering evidence, we just need to run the model on the unique claims
        data = data.drop_duplicates(subset=["claim_id"])
        
    data["prompt"] = data.apply(lambda row: get_prompt(row, prompt_template, use_evidence), axis=1)
    dataset = Dataset.from_pandas(data[["claim_id", "prompt"]])
    
    # pipe = transformers.pipeline(model=model, tokenizer=tokenizer, task='text-generation')
    pipe = TextWithLogitsGenerationPipeline(model=model, tokenizer=tokenizer)
    eos_token_ids = [tokenizer.eos_token_id, 
                     tokenizer.encode("\n", add_special_tokens=False)[0], 
                     tokenizer.encode(" \n", add_special_tokens=False)[0], 
                     tokenizer.encode("\n ", add_special_tokens=False)[0], 
                     tokenizer.encode(" \n ", add_special_tokens=False)[0],
                     tokenizer.encode("\n\n", add_special_tokens=False)[0], 
                     tokenizer.encode(" \n\n", add_special_tokens=False)[0], 
                     tokenizer.encode("\n\n\n", add_special_tokens=False)[0], 
                     tokenizer.encode(" \n\n\n", add_special_tokens=False)[0], 
                     ]
    print(f"Using the following EOS token IDs for the generation: {eos_token_ids}")
    config = GenerationConfig(
        eos_token_id=eos_token_ids,
        max_new_tokens=10,
        output_logits=True,
        return_dict_in_generate=True,
    )
    
    # get logits for the following tokens
    logit_tokens = ["True", "False", "None", "Support", "Refute"]
    logit_ixs = {}
    for tok in logit_tokens:
        tok_ix = tokenizer.encode(tok, add_special_tokens=False)
        if len(tok_ix) > 1:
            print(f"Warning: token {tok} corresponds to multiple token IDs ({tok_ix}), will record logits for the first ID.")
        logit_ixs[tok] = tok_ix[0]
        
        # some tokens may be encoded differently with a preceeding space
        tok_w_space = " " + tok
        tok_w_space_ix = tokenizer.encode(tok_w_space, add_special_tokens=False)
        # record logits for tokens for which the space does not add an extra token ID
        if len(tok_w_space_ix) == len(tok_ix):
            logit_ixs[tok_w_space] = tok_w_space_ix[0]
    print("Will record logits for the following tokens with token ids:")
    print(logit_ixs)
    print()
        
    pred_list = []
    probs_list = {key: [] for key in logit_ixs.keys()}
    for out in tqdm(pipe(KeyDataset(dataset, "prompt"), 
                         pad_token_id=tokenizer.pad_token_id, 
                         return_full_text=False,
                         generation_config=config,),
                    total=len(data)):
        pred_list.append(out[0]["generated_text"].strip())
        
        # get normalized logits of interest for first predicted token - TODO: check that this is not the BOS token
        probs = softmax(out[0]["logits"][0][0], dim=0)
        for tok, tok_id in logit_ixs.items():
            probs_list[tok].append(probs[tok_id].detach().item())
    
    if use_evidence:
        suffix = "w_evidence"
    else:
        suffix = "wo_evidence"
    data[f"prediction_{suffix}"] = pred_list
    for tok in logit_ixs.keys():
        data[f"p_{tok.replace(' ', '_')}"] = probs_list[tok]
    
    data = data.drop(columns=["prompt"])
    MODEL_NICKNAME = model_code.split('/')[1].split('-')[0]
    filename = f'{MODEL_NICKNAME}_preds_use_evidence_{use_evidence}_prompt_{prompt_name}.tsv'
    data.to_csv(os.path.join(save_folder, filename), sep='\t')

if __name__ == '__main__':
    enforce_reproducibility()
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_file", type=str, help="Path to the data file")
    parser.add_argument("--save_folder", type=str, help="Path to folder to save results to")
    parser.add_argument("--use_evidence", type=str, default="no", choices=['yes','no'], help="Whether to use evidence or not")
    parser.add_argument("--model_name", type=str, default="no", help="Path to Huggingface model")
    parser.add_argument("--prompt_name", type=str, required=True, help="What prompt to use for the evaluation.")
    parser.add_argument("--cache_folder", type=str, default=None, help="Path to cache folder")
    
    args = parser.parse_args()
    os.makedirs(args.save_folder, exist_ok=True)
    print(args)
    print()
    
    predict_veracity(file_path=args.data_file, 
                     save_folder=args.save_folder, 
                     use_evidence=args.use_evidence, 
                     model_code=args.model_name, 
                     prompt_name=args.prompt_name,
                     cache_folder=args.cache_folder)
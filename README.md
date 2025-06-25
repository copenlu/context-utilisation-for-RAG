# context-utilisation-for-RAG

This is the repository for the paper [A Reality Check on Context Utilisation for Retrieval-Augmented Generation](https://arxiv.org/abs/2412.17031) accepted to ACL 2025 Main.
In the paper, we ground studies of context utilisation to real-world RAG scenarios.

<p align="center">
  <img src="figures/comparison_overview.png" alt="DRUID and other datasets" style="width:55%; height:auto;">
</p>


## DRUID
We introduce DRUID (_Dataset of Retrieved Unreliable, Insufficient and Difficult-to-understand context_) with real-world (query, context) pairs to facilitate studies of context usage and failures in real-world scenarios.

The developed DRUID datasets can be found [here](https://huggingface.co/datasets/copenlu/druid). More information about the datasets can be found under the same link.

The dataset collection is performed in three main steps (claim collection, automated evidence retrieval and stance annotation), as described below.

### Set up environment

For the dataset collection, set up a virtual environment with packages as listed in `requirements_data.txt`. We used Python 3.9.20.

```bash
python -m venv venv-data
source venv-data/bin/activate
pip install -r requirements_data.txt
```

### 1. Claim Collection
Claims are collected using the [Google Fact Check Tools API](https://developers.google.com/fact-check/tools/api). We sample as many claims as possible from each of the following sites:
  - checkyourfact
  - factcheckni
  - factly
  - politifact
  - sciencefeedback/healthfeedback/climatefeedback
  - srilanka_factcrescendo

For each site, save the claims to a unique <claim_data_path> and run the following code to get a subsample of claims with a desired distribution. This needs to be run for each source site.

```
python -m src.retrieval.get_claims --claim_data_path <claim_data_path> \
  --save_folder <save-folder> \
  --n_claims_to_include 300
```

This will save a subset of claims to `<save-folder>/gold_samples.csv`. The claims are sampled to ensure, to the extent possible, (1) an even distribution across the 7 fact-checking sources, (2) an even distribution across True, False and Half-True claims, and (3) an even distribution of claims posted before and after 2023. For the sampling, we first prioritise (1), followed by (2) etc. Due to a shortage of some claims, we cannot achieve completely even distributions.

#### Borderlines

We also collect special claims related to border conflicts, for which multiple conflicting evidence can be expected to be found. These are denoted as "borderlines claims" and are not retrieved from fact-check sites, differently from the other claims. The collection of these claims is based on the [Borderlines dataset](https://huggingface.co/datasets/manestay/borderlines) by [Li et al. (2024)](https://aclanthology.org/2024.naacl-long.213/). We collect samples representative of each country's standpoint for the different disputed territories in the Borderlines dataset.

### 2. Automated Evidence Retrieval

First, set up the necessary API keys for the search engines (Google and Bing) and the Cohere reranker. This is done as follows:
- Set up a Google API key for the search engine, more info on this can be found [here](https://developers.google.com/maps/documentation/javascript/get-api-key). This key should be saved to `API-keys/google-api-key.txt`.
- You also need to customise a Google search engine (will have access to fact check pages) at the [Programmable Search Engine control panel](https://programmablesearchengine.google.com/controlpanel/all). Do this and save its ID to `API-keys/google-cx.txt`. My settings for the Programmable Search Engine:
  - Image search: off
  - SafeSearch: off
  - Search the entire web: on
  - Sites to search: none
  - Language: English
- Set up a Bing API key for the search engine and save it to `API-keys/bing-api-key.txt`.
- Set up a Cohere API key. You can either create a trial key (for free, but with limited request rates) or set up a production key with billing enabled. More details can be found [here](https://docs.cohere.com/docs/rate-limits). Copy your key to `API-keys/cohere-api-key.txt`.

Then, to run the full retrieval pipeline for a given set of claims (stored in `<save-folder>/gold_samples.csv`), use the following code: 

```
src/retrieval/run_all_retrieval_steps.sh <save-folder>
```

This code will:
  1. Collect search results from Bing and Google for the claims.
  2. Scrape the webpages corresponding to the search results.
  3. Extract paragraphs from the scraped webpages.
  4. Collect Cohere reranker scores for the paragraphs.
  5. Aggregate evidence snippets based on the reranker scores for each claim and webpage.
  6. Format the samples for annotation.

All ensuing results and cached data will be saved to `<save-folder>`. The samples formatted for annotation will be saved in batches to `<save-folder>/dataset_to_annotate_<batch_num>.tsv`. Each `<save-folder>` typically corresponds to one site from which claims have been sampled.

To get the additional samples corresponding to DRUID+, also run the following code:

```bash
DATA_FOLDER=<save-folder>
SAVE_FOLDER=<full-save-folder>
python -m src.retrieval.get_evidence_from_reranked_paragraphs \
        --reranked_paragraphs_path "${DATA_FOLDER}/reranked_paragraph_results.csv" \
        --save_folder "${SAVE_FOLDER}" \
        --source_claims_path "${DATA_FOLDER}/gold_samples.csv" \
        --max_paragraphs_in_evidence 3 \
        --max_paragraph_neighbour_dist 1

python -m src.retrieval.get_dataset_to_annotate \
        --auto_evidence_path "${SAVE_FOLDER}/evidence_results.csv" \
        --source_claims_path "${DATA_FOLDER}/gold_samples.csv" \
        --save_folder "${SAVE_FOLDER}" 
```

### 3. Stance Annotations

The formatted \<claim, evidence\> samples are annotated for relevance and stance using Potato and Prolific. Potato is set up following the guides linked below:
- [Potato general guide](https://github.com/davidjurgens/potato?tab=readme-ov-file#Example-projects-project-hub)
- [Potato prolific guide](https://potato-annotation.readthedocs.io/en/latest/crowdsourcing/)
- [Further potato prolific guides](https://potato-annotation-tutorial.readthedocs.io/en/latest/crowdsourcing.html)
- [Potato login guide](https://potato-annotation.readthedocs.io/en/latest/user_and_collaboration/)

#### Annotation Server

Amazon EC2 instances were used to host the annotation server. Specifically, we used Ubuntu 1 GB RAM instances with 30GB memory which worked well for our purposes.

Using Python 3.12:
```bash
sudo apt update
sudo apt install python3-pip
sudo apt install python3.12-venv
python3 -m venv venv3.12
source venv3.12/bin/activate
pip install potato-annotation
sudo apt-get install tmux
```

We use tmux (a guide to the package can be found [here](https://deliciousbrains.com/tmux-for-local-development/)) to enable detached server sessions. The Potato annotation instance is launched using the following code:

```bash
source ../venv3.12/bin/activate
cd <folder-with-potato-annotation-config-files>
mkdir logs
tmux new -s potato
sudo env PATH="$PATH" potato start configs/<potato-yaml-file> -p 80 > logs/potato.log
```

We need to run with `sudo` to be able to access port 80. Also, we need to preserve our original path (`$PATH`) to be able to run Potato.

The interface should then be available at e.g. http://ec2-13-60-170-165.eu-north-1.compute.amazonaws.com.
(Note that we are not using "https" here.)

[src/annotation_server/round_X](src/annotation_server/round_X) illustrates what the `<folder-with-potato-annotation-config-files>` might look like.

#### Processing of Annotations

All samples are double annotated. Samples with quality issues or too great annotator disagreements are dropped. Samples with minor annotator disagreements (e.g. annotator 1: 'insufficient-neutral' and annotator 2: 'insufficient-refutes') are resolved using competence estimates from [MACE](https://github.com/dirkhovy/MACE). The remaining samples form the DRUID dataset, consisting of \<claim, evidence, labels\>.

## Synthesised Datasets

We compare against CounterFact and ConflictQA. These are recast to a claim verification task using the scripts in src/recast. For example, to recast and save CounterFact used by [Ortu et al.](https://arxiv.org/pdf/2402.11655v1):
1. Download the CounterFact data to `<data-path>`. We use the Pythia 6.9B split found [here](https://github.com/francescortu/comp-mech/blob/refactor/data/full_data_sampled_pythia-6.9b.json).
2. Recast the dataset to a format matching ours, with evidence and claims using:
  ```
  python -m src.recast.recast_counterfact --data_path <data-path> --save_file <save-file>
  ```

A similar procedure is followed for the ConflictQA dataset used by [Xi et al.](https://arxiv.org/pdf/2305.13300). We use the Llama 2 7B split found [here](https://github.com/OSU-NLP-Group/LLM-Knowledge-Conflict/blob/main/conflictQA/conflictQA-popQA-llama2-7b.json) (it should be saved as a .jsonl file). Then use `src/recast/recast_conflictQA.py` to recast it.

## Get Model Predictions

We collect the predictions of the Pythia and Llama models on CounterFact, ConflictQA, and DRUID. CounterFact and ConflictQA have been recast to a claim-evidence format before this. The method for collecting the model predictions is described below. We also provide the collected model predictions in [our data checkpoint](https://huggingface.co/datasets/copenlu/reality-check-on-context-utilisation).

### Set up environment

For the collection of model predictions, set up a virtual environment with packages as listed in `requirements_predictions.txt`. We used Python 3.9.20.

```bash
python -m venv venv-predictions
source venv-predictions/bin/activate
pip install -r requirements_predictions.txt
```

### Collect model predictions

Model predictions with and without context provided are collected for the context usage analysis using the code below. 

```bash
python -m src.get_model_predictions.get_model_predictions \
        --data_file <data-path> \
        --save_folder <save-folder> \
        --use_evidence <yes-or-no> \
        --model_name <model-name> \
        --prompt_name "pythia_claim_prompt_2_shot"
```

- `--data_file` can for example describe the path to the DRUID dataset. The dataset should contain the columns 'id', 'claim', 'claim_id' and 'evidence'. 
- `--use_evidence` details whether the model should be prompted with evidence (context) or without.
- `--model_name` should work with `AutoModelForCausalLM.from_pretrained(<model-name>)`. It can for example be 'EleutherAI/pythia-6.9b'.
- `--prompt_name` should detail a prompt from the dictionary keys in `src/get_model_predictions/prompts.py`. The prompt type (claim or evidence) should match whether evidence is used or not. Claim prompts should be used when no evidence is used and evidence prompts should be used when the evidence is used. A prior prompt tuning stage was performed on a subset of the DRUID dataset, for which optimal prompts were identified, as described below.

```python
OPTIMAL_PROMPTS = {"Pythia 6.9B": 
                      "without_evidence": "pythia_claim_prompt_3_shot_alt_1",
                      "with_evidence": "pythia_evidence_prompt_3_shot_alt_7",
                   "Llama 8B": 
                      "without_evidence": "pythia_claim_prompt_3_shot",
                      "with_evidence": "pythia_evidence_prompt_3_shot_alt_4",
                  }
```

## Context Characteristics Detection

Context characteristics are detected in 4 steps, after which they are saved to a dataset, ready for plotting. The virtual environment used for collecting model predictions can be used here as well. We detect context characteristics for CounterFact, ConflictQA and DRUID.

We have also uploaded the corresponding data checkpoint to Hugging Face, such that one can skip the detection steps described here and immediately load the dataset for plotting in [Create plots](#create-plots).

### 1. Automated property detection

For the detection of most context/evidence properties, use the following command:
```
python -m src.property_detection.get_properties --data_path <data-path> \
  --save_folder <save-folder> \
  --properties all \
```

The data you wish to detect properties for should be found under `<data-path>`. The data and corresponding properties will be saved under `<save-folder>`.

### 2. Cohere property detection

We also use an approach based on prompting an LLM to detect context characteristics. Make sure to have a valid Cohere API key stored under "API-keys/cohere-api-key.txt" and run the following code:
```
python -m src.property_detection.get_properties_cohere --data_path <data-path> \
  --save_folder <save-folder> \
  --properties all \
```

The data and corresponding properties will be saved under `<save-folder>` with the filenames `<property>_cohere.tsv`.

### 3. Add perplexity values 

Use the following code:

```
python src/property_detection/get_perplexity.py <model-name> <tsv-data-path>
```

Replace `<model-name>` with the model for which you would like to collect perplexity values (see the code for what models are admissible). Replace `<tsv-data-path>` with the data path to the tsv file with samples you would like to collect perplexity values for. The perplexity values will be collected for the 'evidence' column in the dataset, so make sure that exists. The perplexity values will be saved to the folder `data/property_detection/ppl`.

### 4. Detect minor context properties and create the final dataset with context characteristics

Finally, the samples with properties detected as described above are concatenated for all datasets. After this, src/prepare_data.ipynb performs some extra feature refinement and minor context property detection, after which a data checkpoint is saved and ready for plotting.

## Create plots

### Set up environment

For the plotting, set up a virtual environment with packages as listed in `requirements_plots.txt`. We used Python 3.9.20.

```bash
python -m venv venv-plots
source venv-plots/bin/activate
pip install -r requirements_plots.txt
```

### Create plots

First, prepare the data for plotting using `src/prepare_data.ipynb`. This notebook essentially aggregates and formats all of the data collected in the previous steps and adds necessary metrics, etc. You can also skip this step and immediately load [our data checkpoint](https://huggingface.co/datasets/copenlu/reality-check-on-context-utilisation) for the plotting. 

Then, use `src/get_plots.ipynb` to get the same plots as seen in our [paper](https://arxiv.org/abs/2412.17031). The notebook has support for loading a data checkpoint directly from Hugging Face.

## Citation

```
@misc{hagström2024realitycheckcontextutilisation,
      title={A Reality Check on Context Utilisation for Retrieval-Augmented Generation}, 
      author={Lovisa Hagström and Sara Vera Marjanović and Haeun Yu and Arnav Arora and Christina Lioma and Maria Maistro and Pepa Atanasova and Isabelle Augenstein},
      year={2024},
      eprint={2412.17031},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2412.17031}, 
}
```

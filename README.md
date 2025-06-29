# Causal Influence Prompting

![main_figure](./asset/main_figure.png)

## Table of Contents
- [Installation guidelines](#installation-guidelines)
- [CID Generation](#cid-generation)
- [Experiment](#experiment)
- [Reference](#reference)

## Installation guidelines

### Virtual environments
The `environment_mobilesafetybench.yml` file lists all dependencies required to run MobileSafetyBench for the project. You can use the following command to setup the conda environment.
```
conda env create -f environment_mobilesafetybench.yml
source ~/.bashrc
conda activate cip_mobilesafetybench

cd cip
pip install -e . # install cip
cd ../MobileSafetyBench
pip install -e . # install mobile_safety
```
The `environment_redcode.yml` file lists all dependencies required to run RedCode-Exec benchmark for the project. You can use the following command to setup the conda environment.
```
conda env create -f environment_redcode.yml
source ~/.bashrc
conda activate cip_redcode

cd cip
pip install -e . # install cip
```
Also, please check the installation guidelines for the `MobileSafetyBench` and `RedCode-Exec`  directories to ensure proper installation of each benchmark.

### Setting Path and API Keys
In the project root directory, create a `.env` file and add the following contents:
```
# Path settings
CIP_HOME=/path/to/current/directory
REDCODE_EXEC_HOME=/path/to/current/directory/RedCode-Exec/dataset/RedCode-Exec
MOBILESAFETYBENCH_HOME=/path/to/current/directory/MobileSafetyBench

# API keys
OPENAI_API_KEY="your-openai-api-key"
GOOGLE_API_KEY="your-google-api-key"
ANTHROPIC_API_KEY="your-anthropic-api-key"
```

## CID Generation
Before executing the agent with CIP for each benchmark, you should first generate CID using the script below. 
The generated CIDs will be saved in `cids/{benchmark}/{provider}/{model_name}/{task}`.

### CID generation for MobileSafetyBench 
Set `task_tags` in `mobilesafetybench_cid.py` using `task_id` and `scenario_id` to generate a CID for each task. You can find the task list in the `MobileSafetyBench/asset/tasks/tasks.json`.
```
cd cip/scripts
python mobilesafetybench_cid.py --provider {provider} --model {model}

# python mobilesafetybench_cid.py --provider openai --model gpt-4o-2024-08-06
```
### CID generation for RedCode-Exec 
Set `language`, `scenario_ids`, `test_cases`, and `prompt_modes` in `redcode_cid.py` to generate a CID for each task. You can find the task files for each language and scenario in the `RedCode-Exec/dataset/RedCode-Exec` directory.
```
cd cip/scripts
python redcode_cid.py --provider {provider} --model {model}

# python redcode_cid.py --provider openai --model gpt-4o-2024-08-06
```

### Check CID
You can check the generated CID with text and image using `cip/scripts/check_cid.ipynb`.

## Experiment

### MobileSafetyBench
To evaluate agent with basic (CoT), Safety-guided Chain-of-Thought (SCoT), and CIP prompt in MobileSafetyBench, use the file below.
Set `task_id`, `scenario_id`, and `model` to run different tasks and models.
```
cd MobileSafetyBench/experiment
evaluate_{method}.ipynb

# evaluate_basic.ipynb
# evaluate_scot.ipynb
# evaluate_cip.ipynb
```

### RedCode-Exec Benchmark
To evaluate agent with basic (ReACT), Safety-Aware Prompting, and CIP prompt in RedCode-Exec Benchmark, use the below script.
Set `language`, `scenario_id`, `model` and other options(`--safety_sys_choice 4_safety_integration `, `--use_cid`,  `--refine`) to run different tasks and prompts.
```
cd RedCode-Exec
sh ./scripts/RA_eval_{model}.sh

# sh ./scripts/RA_eval_gpt.sh
# sh ./scripts/RA_eval_gemini.sh
# sh ./scripts/RA_eval_claude.sh
```

## Reference
Some codes are referred from the related work below:
- MobileSafetyBench (<a href="https://github.com/jylee425/mobilesafetybench">link</a>)
- RedCode (<a href="https://github.com/AI-secure/RedCode">link</a>)

### AI Assistance Disclosure
Some parts of this code were assisted by GitHub Copilot. All code has been reviewed and modified as necessary to ensure correctness, originality, and compliance with licensing requirements.

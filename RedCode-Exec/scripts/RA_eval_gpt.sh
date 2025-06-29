#!/bin/bash
cd evaluation

# python -m RedCode_Exec.main RA --model {model} --temperature 0 --max_tokens 1024 --python_eval --id {id} --{lang}_eval {--safety_sys_choice 4_safety_integration} {--use_cid --refine}

# Basic (ReACT)
python -m RedCode_Exec.main RA --model gpt-4o-2024-08-06 --temperature 0 --max_tokens 1024 --python_eval --id 1

# Safety-Aware Prompting
python -m RedCode_Exec.main RA --model gpt-4o-2024-08-06 --temperature 0 --max_tokens 1024 --python_eval --safety_sys_choice 4_safety_integration --id 1

# CIP
python -m RedCode_Exec.main RA --model gpt-4o-2024-08-06 --temperature 0 --max_tokens 1024 --python_eval --id 1 --use_cid --refine
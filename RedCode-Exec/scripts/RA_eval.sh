cd evaluation

### GPT

# # naive
python -m RedCode_Exec.main RA --model gpt-4o-2024-08-06 --temperature 0 --max_tokens 1024 --python_eval --id 2
python -m RedCode_Exec.main RA --model gpt-4o-2024-08-06 --temperature 0 --max_tokens 1024 --python_eval --id 4


# # safe prompting
# python -m RedCode_Exec.main RA --model gpt-4o-2024-08-06 --temperature 0 --max_tokens 1024 --python_eval --safety_sys_choice 4_safety_integration --id 0

# # cid_fixed
# python -m RedCode_Exec.main RA --model gpt-4o-2024-08-06 --temperature 0 --max_tokens 1024 --python_eval --use_cid --id 0


### Gemini

# # naive
# python -m RedCode_Exec.main RA --model gemini-1.5-pro-002 --temperature 0 --max_tokens 1024 --python_eval --id 0

# # safe prompting
# python -m RedCode_Exec.main RA --model gemini-1.5-pro-002 --temperature 0 --max_tokens 1024 --python_eval --safety_sys_choice 4_safety_integration --id 0

# # cid_fixed
# python -m RedCode_Exec.main RA --model gemini-1.5-pro-002 --temperature 0 --max_tokens 1024 --python_eval --use_cid --id 0


# ### Claude

# # naive
# python -m RedCode_Exec.main RA --model claude-3-5-sonnet-20241022 --temperature 0 --max_tokens 1024 --python_eval --id 0

# # safe prompting
# python -m RedCode_Exec.main RA --model claude-3-5-sonnet-20241022 --temperature 0 --max_tokens 1024 --python_eval --safety_sys_choice 4_safety_integration --id 0

# # cid_fixed
# python -m RedCode_Exec.main RA --model claude-3-5-sonnet-20241022 --temperature 0 --max_tokens 1024 --python_eval --use_cid --id 0
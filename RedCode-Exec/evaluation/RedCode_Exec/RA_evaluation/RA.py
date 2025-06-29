from RedCode_Exec.RA_evaluation.evaluate import *
from RedCode_Exec.RA_evaluation.interaction import *
import argparse
import datetime
import os

def RA(model, temperature=0, top_p=1.0, seed=998244353, max_tokens=1024, dry_run=False, version='v1', 
       safety_sys_choice='none', task_type='python_eval', use_cid=False, refine=False, id=0):

    # Create directories if not exist
    if not os.path.exists('../results/RA/log'):
        os.makedirs('../results/RA/log')
    if not os.path.exists('../results/RA'):
        os.makedirs('../results/RA')

    # Timestamp for file naming
    time_now = datetime.datetime.now() + datetime.timedelta(hours=8)
    time_stamp = str(time_now).replace(' ', '_')

    # File naming
    file_name = "python_" if task_type == "python_eval" else "bash_"
    if "gpt" in model:
        file_name += "gpt" + "_"
    elif "gemini" in model:
        file_name += "gemini" + "_"
    elif "claude" in model:
        file_name += "claude" + "_"
    file_name += f"{id}_RA"
    
    if safety_sys_choice != 'none':
        file_name += "_safe"
    if use_cid:
        file_name += "_cid"
        if refine:
            file_name += "_refine"
        else:
            file_name += "_fixed"
    file_name += f"_{time_stamp}"
    
    resfile = f'../results/RA/{file_name}.json'
    logfile = f'../results/RA/log/RA_log_{file_name}.json'

    # Initialize the base model and eval task
    base_model = BaseModel(model=model, temperature=temperature, top_p=top_p, seed=seed, max_tokens=max_tokens, dry_run=dry_run)
    eval_task = EvalTask(task=task_type.split('_')[0], version=version, safety_sys_choice=safety_sys_choice)

    # Loop through each task ID and evaluate dataset
    image = "redcode"
    with Container(image) as container:

        # Get the current file's directory
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        dataset_base_path = os.path.join(current_file_path, '../../../dataset/RedCode-Exec')

        # Set dataset JSON file path based on task type
        if task_type == 'python_eval':
            jsonfile = os.path.join(dataset_base_path, f'py2text_dataset_json/index{id}_30_codes_full.json')
        elif task_type == 'bash_eval':
            jsonfile = os.path.join(dataset_base_path, f'bash2text_dataset_json/index{id}_30_codes_full_upd.json')
        else:
            raise ValueError(f"Invalid task type: {task_type}")

        # Evaluate the dataset
        eval_dataset(id, container, base_model, jsonfile, resfile, logfile, eval_task, use_cid, refine)

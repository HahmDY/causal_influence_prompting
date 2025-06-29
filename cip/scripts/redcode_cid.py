import os
import json
import pickle
import argparse
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor
from itertools import product

from cip.prompts import (
    GENERATION_SYSTEM_PROMPT, 
    GENERATION_USER_PROMPT,
)
from cip.redcode_exec import load_case

PROVIDER = {
    "anthropic": "cip.anthropic",
    "google": "cip.google",
    "openai": "cip.openai",
}

load_dotenv()
CIP_HOME = os.getenv('CIP_HOME')
REDCODE_EXEC_HOME = os.getenv("REDCODE_EXEC_HOME")

parser = argparse.ArgumentParser(description="Generate CID for RedCode-Exec tasks")
parser.add_argument("--provider", type=str, required=True, choices=PROVIDER.keys(), help="Provider (openai, google, anthropic)")
parser.add_argument("--model", type=str, required=True, help="Model name (gpt-4o-2024-08-06, gemini-1.5-pro-002, claude-3-5-sonnet-20241022)")

args = parser.parse_args()
provider = args.provider
model_name = args.model

module = __import__(PROVIDER[provider], fromlist=['generate_cid'])
generate_cid = getattr(module, "generate_cid")

language = "Python"
scenario_ids = [1]
test_cases = list(range(1, 31))
prompt_modes = ["code", "text_summary", "text_details"]

def process_case(args):
	scenario_id, test_case, prompt_mode = args
	try:
		instruction, action_space = load_case(language,scenario_id, test_case, prompt_mode)
	except:
		return f"Data not found: {scenario_id}-{test_case}-{prompt_mode}"

	system_prompt = GENERATION_SYSTEM_PROMPT
	user_prompt = GENERATION_USER_PROMPT.format(instruction=instruction, action_space=action_space)

	try:
		cid = generate_cid(model_name=model_name,
							system_prompt=system_prompt, 
							user_prompt=user_prompt,
							verbose=True)
	except:
		return f"Error: {scenario_id}-{test_case}-{prompt_mode}"

	folder = f"{CIP_HOME}/cip/cids/redcode_exec/{provider}/{model_name}/{language}/{scenario_id}"
	os.makedirs(folder, exist_ok=True)
	cid_path = f"{folder}/{language}_{scenario_id}_{test_case}_{prompt_mode}.pkl"

	with open(cid_path, 'wb') as f:
		pickle.dump(cid, f)

	return f"Saved: {cid_path}"

if __name__ == "__main__":
    num_workers = 2
    cases = list(product(scenario_ids, test_cases, prompt_modes))

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        results = list(executor.map(process_case, cases))
    
    for res in results:
        print(res)

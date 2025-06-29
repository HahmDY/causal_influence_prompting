import os
import pickle
import argparse
from dotenv import load_dotenv

from cip.mobilesafetybench import load_task
from cip.prompts import (
    GENERATION_SYSTEM_PROMPT, 
    GENERATION_USER_PROMPT,
)

PROVIDER = {
    "anthropic": "cip.anthropic",
    "google": "cip.google",
    "openai": "cip.openai",
}

load_dotenv()
CIP_HOME = os.getenv('CIP_HOME')

task_tags = [
    ("message_forwarding", "high_risk_1"),
]

parser = argparse.ArgumentParser(description="Generate CID for MobileSafetyBench tasks")
parser.add_argument("--provider", type=str, required=True, choices=PROVIDER.keys(), help="Provider (openai, google, anthropic)")
parser.add_argument("--model", type=str, required=True, help="Model name (gpt-4o-2024-08-06, gemini-1.5-pro-002, claude-3-5-sonnet-20241022)")

args = parser.parse_args()
provider = args.provider
model_name = args.model

module = __import__(PROVIDER[provider], fromlist=['generate_cid'])
generate_cid = getattr(module, "generate_cid")

for (task_id, scenario_id) in task_tags:
    task_tag = f"{task_id}_{scenario_id}"
    task = load_task(task_id, scenario_id)
    instruction = task["instruction"]
    print(instruction)
    tools = task["action_space"]

    system_prompt = GENERATION_SYSTEM_PROMPT
    user_prompt = GENERATION_USER_PROMPT.format(instruction=instruction, action_space=tools)

    cid = generate_cid(
        model_name=model_name,
        system_prompt=system_prompt, 
        user_prompt=user_prompt,
        verbose=True
    )

    folder = f"{CIP_HOME}/cip/cids/mobilesafetybench/{provider}/{model_name}"
    os.makedirs(folder, exist_ok=True)
    cid_path = f"{folder}/{task_tag}.pkl"
    with open(cid_path, 'wb') as f:
        pickle.dump(cid, f)
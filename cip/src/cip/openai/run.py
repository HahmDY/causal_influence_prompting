import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv

from cip.utils import encode_image
from cip.cid import CID
from cip.openai.tools import (
	ADD_NODE,
	ADD_EDGE,
	UPDATE_NODE,
	UPDATE_EDGE,
	VALIDATE_CID,
	SUBMIT_CID,
)

load_dotenv()

class CIDloop():
    def __init__(self, cid_module, tools, verbose):
        self.cid_module = cid_module
        self.tools = tools
        self.verbose = verbose
        self.maximum_messages = 30
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.time_duration = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def loop(self, model_name, system_prompt, user_prompt, image_path):
        finish = False
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt} if image_path is None else
            {"role": "user", "content": [
                {"type": "text", "text": user_prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encode_image(image_path)}"}}
            ]}
        ]
        
        for _ in range(self.maximum_messages):
            completion = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                tools=self.tools,
                max_tokens=8192,
                temperature=0.0,
                top_p=1.0,
                tool_choice="auto"
            )
            
            usage = completion.usage
            self.total_input_tokens += usage.prompt_tokens
            self.total_output_tokens += usage.completion_tokens
            messages.append(completion.choices[0].message)
            
            if self.verbose:
                print(completion.choices[0].message.content)
            
            tool_calls = completion.choices[0].message.tool_calls
            if tool_calls is None:
                continue
            
            for tool_call in tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                output = "Invalid tool call"
                
                try:
                    if func_name == "add_node":
                        output = self.cid_module.add_node(args["node_name"], args["node_id"], args["node_desc"])
                    elif func_name == "add_edge":
                        output = self.cid_module.add_edge(args["node_id_1"], args["node_id_2"], args["edge_desc"])
                    elif func_name == "update_node":
                        output = self.cid_module.update_node(args["node_id"], args["node_desc"])
                    elif func_name == "update_edge":
                        output = self.cid_module.update_edge(args["node_id_1"], args["node_id_2"], args["edge_desc"])
                    elif func_name == "validate_cid":
                        output = self.cid_module.validate_cid()
                    elif func_name == "submit_cid":
                        output = self.cid_module.submit_cid()
                        if output == "CID construction completed successfully. CID has been submitted.":
                            finish = True
                    
                except Exception:
                    output = "Operation failed. Please try again with valid inputs."
                
                if self.verbose:
                    print(f"<{func_name.replace('_', ' ').title()}>")
                    print("Arguments:", args)
                    print("Output:", output)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": output
                })
                
                if finish:
                    break
            
            if finish:
                break
   
   
def generate_cid(model_name="gpt-4o-2024-08-06",
				 system_prompt="", 
				 user_prompt="",
				 image_path=None,
				 verbose=False):
  
	cid_module = CID()
	tools = [ADD_NODE, ADD_EDGE, VALIDATE_CID, SUBMIT_CID]
  
	loop = CIDloop(cid_module, tools, verbose)
	start_time = time.time()
	loop.loop(model_name, system_prompt, user_prompt, image_path)
	time_duration = time.time() - start_time
 
	if verbose:
		print("Total prompt tokens: ", loop.total_input_tokens)
		print("Total completion tokens: ", loop.total_output_tokens)
		print("Time duration: ", time_duration)
	cid_module.time_duration = time_duration
	cid_module.total_input_tokens = loop.total_input_tokens
	cid_module.total_output_tokens = loop.total_output_tokens
	return cid_module
				

def refine_cid(model_name="gpt-4o-2024-08-06",
               cid_module: CID=None,
				system_prompt="", 
				user_prompt="",
				image_path=None,
				verbose=False):
  
	tools = [ADD_NODE, ADD_EDGE, UPDATE_NODE, UPDATE_EDGE, VALIDATE_CID, SUBMIT_CID]
  
	loop = CIDloop(cid_module, tools, verbose)
	start_time = time.time()
	loop.loop(model_name, system_prompt, user_prompt, image_path)
	time_duration = time.time() - start_time
 
	if verbose:
		print("Total input tokens for refinement: ", loop.total_input_tokens)
		print("Total output tokens for refinement: ", loop.total_output_tokens)
		print("Time duration for refinement: ", time_duration)
	cid_module.time_duration = time_duration
	cid_module.total_input_tokens = loop.total_input_tokens
	cid_module.total_output_tokens = loop.total_output_tokens
	return cid_module
import os
import json
import time
import asyncio
import anthropic

from dotenv import load_dotenv
from cip.cid import CID
from cip.utils import encode_image
from cip.anthropic.tools import (
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
        self.client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.time_duration = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def loop(self, model_name, system_prompt, user_prompt, image_path):
        messages = (
            [{"role": "user", "content": user_prompt}]
            if image_path is None else
            [{
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encode_image(image_path)}}
                ]
            }]
        )
        
        finish = False
        for _ in range(self.maximum_messages):
            response = self.client.messages.create(
                model=model_name,
                max_tokens=8192,
                system=system_prompt,
                tools=self.tools,
                messages=messages,
                temperature=0.0,
                top_p=1.0,
                tool_choice={"type": "auto"},
            )
            
            usage = response.usage
            self.total_input_tokens += usage.input_tokens
            self.total_output_tokens += usage.output_tokens
            
            for block in response.content:
                if block.type == 'text':
                    if self.verbose:
                        print(block.text)
                    messages.append({"role": "assistant", "content": block.text})
                    messages.append({"role": "user", "content": "Continue if you have more functions to call. Otherwise, call `submit_cid()` to finish the CID construction process."})
                
                if block.type == 'tool_use':
                    tool_id, tool_name, args = block.id, block.name, block.input
                    output = "Invalid tool call"
                    
                    try:
                        if tool_name == "add_node":
                            output = self.cid_module.add_node(args["node_name"], args["node_id"], args["node_desc"])
                        elif tool_name == "add_edge":
                            output = self.cid_module.add_edge(args["node_id_1"], args["node_id_2"], args["edge_desc"])
                        elif tool_name == "update_node":
                            output = self.cid_module.update_node(args["node_id"], args["node_desc"])
                        elif tool_name == "update_edge":
                            output = self.cid_module.update_edge(args["node_id_1"], args["node_id_2"], args["edge_desc"])
                        elif tool_name == "validate_cid":
                            output = self.cid_module.validate_cid()
                        elif tool_name == "submit_cid":
                            output = self.cid_module.submit_cid()
                            if output == "CID construction completed successfully. CID has been submitted.":
                                finish = True
                    except Exception:
                        output = "Operation failed. Please try again with valid inputs."
                    
                    if self.verbose:
                        print(f"<{tool_name.replace('_', ' ').title()}>")
                        print("Arguments:", args)
                        print("Output:", output)
                    
                    messages.extend([
                        {"role": "assistant", "content": [{"type": "tool_use", "id": tool_id, "name": tool_name, "input": args}]},
                        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id, "content": output}]}
                    ])
                
            if finish:
                break


def generate_cid(model_name="claude-3-5-sonnet-20241022",
				 system_prompt="", 
				 user_prompt="",
				 image_path=None,
				 verbose=False):
  
	system_prompt += """\n\n### **NOTE**
Not only add_node() function, but also multiple add_edge() functions can be called in a single response. For example, while the node has been added, add edges with multiple add_edge() functions in the single response. DO NOT ADD EDGES ONE BY ONE. Also validate_cid(), submit_cid() functions can be called in the same response after adding edges."""

	cid_module = CID()
	tools = [ADD_NODE, ADD_EDGE, VALIDATE_CID, SUBMIT_CID]
  
	start_time = time.time()
	loop = CIDloop(cid_module, tools, verbose)
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


def refine_cid(model_name="claude-3-5-sonnet-20241022",
               cid_module: CID=None,
				system_prompt="", 
				user_prompt="",
				image_path=None,
				verbose=False):
    
	tools = [ADD_NODE, ADD_EDGE, UPDATE_NODE, UPDATE_EDGE, VALIDATE_CID, SUBMIT_CID]

	start_time = time.time()
	loop = CIDloop(cid_module, tools, verbose)
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
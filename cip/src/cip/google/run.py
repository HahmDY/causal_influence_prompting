import os
import time
from PIL import Image
import google.generativeai as genai
from google.generativeai.types import generation_types
from dotenv import load_dotenv

from cip.cid import CID

load_dotenv()
class CIDloop():
    def __init__(self, cid_module, tools, verbose):
        self.cid_module = cid_module
        self.tools = tools
        self.verbose = verbose
        self.maximum_messages = 30
        self.time_duration = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        google_api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key = google_api_key)

    def loop(self, model_name="gemini-1.5-pro-002", system_prompt="", user_prompt="", image_path=None):
        model = genai.GenerativeModel(model_name=model_name, system_instruction=system_prompt, tools=self.tools)
        chat = model.start_chat()
        prompt = user_prompt
        max_retries = 3
        retry_count = 0
        response = None
        
        while retry_count < max_retries:
            try:
                if image_path is None:
                    response = chat.send_message(prompt, generation_config=genai.GenerationConfig(max_output_tokens=8192, temperature=0.0, top_p=1.0))
                else:
                    img_pil = Image.open(image_path)
                    response = chat.send_message([prompt, img_pil], generation_config=genai.GenerationConfig(max_output_tokens=8192, temperature=0.0, top_p=1.0))
                break
            except generation_types.StopCandidateException as e:
                retry_count += 1
        
        self.total_input_tokens += response.usage_metadata.prompt_token_count
        self.total_output_tokens += response.usage_metadata.candidates_token_count
        
        finish = False
        for _ in range(self.maximum_messages):
            response_parts = []
            for part in response.parts:
                if fn := part.function_call:
                    fn_name = fn.name
                    args = {key: val for key, val in fn.args.items()}
                    output = "Invalid function name"
                    
                    try:
                        if fn_name == "add_node":
                            output = self.cid_module.add_node(args["node_name"], args["node_id"], args["node_desc"])
                        elif fn_name == "add_edge":
                            output = self.cid_module.add_edge(args["node_id_1"], args["node_id_2"], args["edge_desc"])
                        elif fn_name == "update_node":
                            output = self.cid_module.update_node(args["node_id"], args["node_name"], args["node_desc"])
                        elif fn_name == "update_edge":
                            output = self.cid_module.update_edge(args["node_id_1"], args["node_id_2"], args["edge_desc"])
                        elif fn_name == "validate_cid":
                            output = self.cid_module.validate_cid()
                        elif fn_name == "submit_cid":
                            output = self.cid_module.submit_cid()
                            if output == "CID construction completed successfully. CID has been submitted.":
                                finish = True
                        
                    except Exception:
                        output = "Operation failed. Please try again with valid inputs."
                    
                    if self.verbose:
                        print(f"<{fn_name.replace('_', ' ').title()}>")
                        print("Arguments:", args)
                        print("Output:", output)
                    
                    response_parts.append(genai.protos.Part(function_response=genai.protos.FunctionResponse(name=fn_name, response={"result": output})))
            
            if finish:
                break
            
            if not response_parts:
                response_parts = "Continue if you have more functions to call. Otherwise, call 'submit_cid' to finish the CID extraction process."
            response = chat.send_message(response_parts)
            self.total_input_tokens += response.usage_metadata.prompt_token_count
            self.total_output_tokens += response.usage_metadata.candidates_token_count
   
   
def generate_cid(model_name="gemini-1.5-pro-002",
				 system_prompt="", 
				 user_prompt="",
				 image_path=None,
				 verbose=False):
  
	cid_module = CID()
	tools = [cid_module.add_edge, cid_module.add_node, cid_module.validate_cid, cid_module.submit_cid]

	loop = CIDloop(cid_module, tools, verbose)
	start_time = time.time()
	loop.loop(model_name, system_prompt, user_prompt)
	time_duration = time.time() - start_time
 
	if verbose:
		print("Total prompt tokens: ", loop.total_input_tokens)
		print("Total completion tokens: ", loop.total_output_tokens)
		print("Time duration: ", time_duration)
	cid_module.time_duration = time_duration
	cid_module.total_input_tokens = loop.total_input_tokens
	cid_module.total_output_tokens = loop.total_output_tokens
	return cid_module
 
	
def refine_cid(model_name="gemini-1.5-pro-002",
               cid_module: CID = None,
			   system_prompt="", 
			   user_prompt="",
			   image_path=None,
			   verbose=False):
  
	tools = [cid_module.add_edge, cid_module.add_node, cid_module.update_node, cid_module.update_edge, cid_module.validate_cid, cid_module.submit_cid]
  
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
import json
import logging
import os
import signal
import time

import docker
import torch
# from openai import AzureOpenAI, OpenAI
from openai import OpenAI
import anthropic
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

from .sysprompt import (SAFETY_SYS_SUFFIX0, SAFETY_SYS_SUFFIX1,
                       SAFETY_SYS_SUFFIX2, SAFETY_SYS_SUFFIX3,
                       SAFETY_SYS_SUFFIX4)


class BaseModel:
    def __init__(self, model, temperature, top_p, seed, max_tokens, dry_run):
        self.model = model
        self.temperature = temperature
        self.top_p = top_p
        self.seed = seed
        self.max_tokens = max_tokens
        self.dry_run = dry_run
            
        if 'gpt' in model:
            self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                
        if 'gemini' in model:
            genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
                
        if 'claude' in model:
            self.client = anthropic.Client(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            
    def generate_gpt(self, messages, max_retries=10, backoff_factor=1):
        attempt = 0
        
        while attempt < max_retries:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                )
                input_token = response.usage.prompt_tokens
                output_token = response.usage.completion_tokens
                return response.choices[0].message.content, input_token, output_token
            except Exception as e:
                attempt += 1
                wait_time = backoff_factor * (2 ** attempt)
                print(f"Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        raise Exception(f"Failed to get a response from the GPT API after {max_retries} attempts.")
            
        
    def generate_gemini(self, messages, max_retries=10, backoff_factor=1):
        attempt = 0      
        
        # build prompt
        system_prompt = ""
        new_messages = []
        for message in messages[:-1]:
            if message['role']=='system':
                system_prompt = message['content']
            else:
                new_message={
                    "role": message['role'],
                    "parts": message['content']
                }
                new_messages.append(new_message)
        last_message = messages[-1]
                
        # build model
        model = genai.GenerativeModel(model_name=self.model,
                                      system_instruction=system_prompt)
        chat = model.start_chat(history=new_messages)
        
        # generate response
        while attempt < max_retries:
            try:
                response = chat.send_message(last_message["content"],
                                            generation_config = genai.GenerationConfig(
                                                max_output_tokens=self.max_tokens,
                                                temperature=self.temperature,
                                                top_p=self.top_p,
                                            ))
                input_tokens = response.usage_metadata.prompt_token_count
                output_tokens = response.usage_metadata.candidates_token_count
                return response.text, input_tokens, output_tokens
            except Exception as e:
                attempt += 1
                wait_time = backoff_factor * (2 ** attempt)
                print(f"Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        raise Exception(f"Failed to get a response from the Gemini API after {max_retries} attempts.")
    
    def generate_claude(self, messages, max_retries=10, backoff_factor=1):
        attempt = 0
        
        # build prompt
        system_prompt = ""
        new_messages = []
        for message in messages:
            if message['role']=='system':
                system_prompt = message['content']
            else:
                new_message={
                    "role": message['role'],
                    "content": message['content']
                }
                new_messages.append(new_message)

        while attempt < max_retries:
            try:
                response = self.client.messages.create(
                    model=self.model,
                    messages=new_messages,
                    system=system_prompt,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    max_tokens=self.max_tokens,
                )
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                return response.content[0].text, input_tokens, output_tokens
            except Exception as e:
                attempt += 1
                wait_time = backoff_factor * (2 ** attempt)
                print(f"Error: {e}. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)

        raise Exception(f"Failed to get a response from the Claude API after {max_retries} attempts.")


class EvalTask:
    def __init__(self, task, version, safety_sys_choice):
        self.task = task
        self.version = version

        # Options: ['none', '0_safety_sys', '1_safety_sys_awareness', '2_safety_sys_detection', '3_safety_sys_modification']
        if safety_sys_choice=='none':
            self.safety_sys = ""
        elif safety_sys_choice=='0_safety_sys':
            self.safety_sys = SAFETY_SYS_SUFFIX0
        elif safety_sys_choice=='1_safety_sys_awareness':
            self.safety_sys = SAFETY_SYS_SUFFIX1
        elif safety_sys_choice=='2_safety_sys_detection':
            self.safety_sys = SAFETY_SYS_SUFFIX2
        elif safety_sys_choice=='3_safety_sys_modification':
            self.safety_sys = SAFETY_SYS_SUFFIX3
        elif safety_sys_choice=='4_safety_integration':
            self.safety_sys = SAFETY_SYS_SUFFIX4
        else:
            raise ValueError(f"Unsupported safety system prompt: {safety_sys_choice}")

class Container:
    def __init__(self, image, name=None):
        self.image = "redcode"
        curr_time = time.time()
        self.name = image + str(curr_time)
        self.client = docker.from_env()
        
        # Check if the image exists, and build it if not
        if not self.image_exists(self.image):
            logging.info(f"Image {self.image} not found. Building the image from Dockerfile.")
            self.build_image()
        
        # Create the container
        self.container = self.client.containers.run(
            self.image,
            labels={"created_by": "code-agent-evaluation"},
            detach=True, tty=True, stdin_open=True,
            name=self.name
        )
        logging.info(f"Container {self.name} started successfully.")
        
        # Run initialization script
        output = self.container.exec_run("bash /app/init.sh")
        output_str = output.output.decode()
        logging.info(f"Container init output: {output_str}")

    def __del__(self):
        try:
            self.container.stop()
        except:
            pass
        finally:
            self.container.remove()

    def __enter__(self):
        
        try:
            logging.info(f"Starting container {self.name} in __enter__...")
            output = self.container.exec_run("bash /app/init.sh")
            output_str = output.output.decode()
            logging.info(f"Container init output: {output_str}")
        except Exception as e:
            logging.error(f"Failed to start container: {e}")
            self.container = None
        return self

    def image_exists(self, image_name):
        try:
            # Attempt to fetch the image
            self.client.images.get(image_name)
            return True
        except docker.errors.ImageNotFound:
            return False

    def build_image(self):
        try:
            dockerfile_path = os.path.join(os.path.dirname(__file__), "../../../../environment")
            logging.info(f"Building image {self.image} from Dockerfile in {dockerfile_path}.")
            self.client.images.build(path=dockerfile_path, tag=self.image)
            logging.info(f"Image {self.image} built successfully.")
        except Exception as e:
            logging.error(f"Failed to build image {self.image}: {e}")
            raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.container.stop()
        self.container.remove()

    def execute_with_retries(self, cmd, retries=3, timeout=1*60):
        def handler(signum, frame):
            raise TimeoutError("Execution timed out")
        
        signal.signal(signal.SIGALRM, handler)
        
        for attempt in range(retries):

            # # Naive exec_run
            # output = self.container.exec_run(cmd, stdin=False, stdout=True, stderr=True, demux=False)
            # output_str = output.output.decode()
            # return output_str

            try:
                logging.debug(f"Attempt {attempt+1}: Starting exec_run in {cmd}")
                signal.alarm(timeout)
                output = self.container.exec_run(cmd, stdin=False, stdout=True, stderr=True, demux=False)
                signal.alarm(0)
                output_str = output.output.decode()
                logging.debug("Finished exec_run")

                if "EOFError" in output_str:
                    logging.error(f"EOFError detected in command output: {cmd}\nOutput:\n{output_str}")
                    return "Execution blocked due to EOFError"
                
                return output_str
            except TimeoutError:
                logging.warning(f"Attempt {attempt+1}: Command execution timed out in docker container with cmd:\n```{cmd}```")
            except Exception as e:
                logging.error(f"Attempt {attempt+1}: An error occurred in docker container: {e}")
            
            logging.info(f"Retrying in 2 seconds...")
            time.sleep(2)
        
        return "Execution timed out"

    def execute_independent(self, command, timeout=1*60, *params):
        # print("=== EXECUTING INDEPENDENT ===\n", command)
        language, command = command
        # if params:
        #     print("== Parameters ==\n", params)
        if language == "bash":
            cmd = ["bash", "-c", command]
            if params:
                cmd.append("--")
                cmd.extend(params)
        elif language == "python":
            cmd = ["python", "-c", command, *params]
        elif language == "c++":
            self.execute_independent(
                (
                    "bash",
                    f'echo "{json.dumps(command)}" > /tmp/main.cpp && '
                    f"g++ -o /tmp/a.out /tmp/main.cpp",
                ),
                None,
            )
            cmd = ["/tmp/a.out", *params]
        elif language == "c":
            self.execute_independent(
                (
                    "bash",
                    f'echo "{json.dumps(command)}" > /tmp/main.cpp && '
                    f"gcc -o /tmp/a.out /tmp/main.cpp",
                ),
                None,
            )
            cmd = ["/tmp/a.out", *params]
        else:
            raise ValueError(f"Unsupported language {language}")
        
        return self.execute_with_retries(cmd, timeout=timeout)
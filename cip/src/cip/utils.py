import os
import cv2
import json
import time
import base64

from PIL import Image
from dotenv import load_dotenv

load_dotenv()
_WORK_PATH = os.getenv('MOBILESAFETYBENCH_HOME')

def convert_json_to_informal(json_input):
    # Parse the JSON input
    data = json.loads(json_input)

    # Extract the function name and description
    function_name = data.get("name", "unknown_function")
    function_description = data.get("description", "No description provided.")

    # Extract parameters
    parameters = data.get("parameters", {}).get("properties", {})
    required_params = data.get("parameters", {}).get("required", [])

    # Process each parameter
    params = []
    for param_name, param_details in parameters.items():
        param_type = param_details.get("type", "unknown")
        param_description = param_details.get("description", "No description provided.")
        required_flag = " (required)" if param_name in required_params else ""
        params.append(f"{param_name} ({param_type}): {param_description}{required_flag}")

    # Join parameters and format the result
    params_string = ", ".join(params)
    informal_format = f"{function_name}({params_string}) -> {function_description}"

    return informal_format


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
    
def save_image(timestep=None):
    img_obs = timestep.curr_obs["pixel"]
    img_cv = cv2.resize(img_obs, dsize=(1024, 2048), interpolation=cv2.INTER_AREA)
    img_pil = Image.fromarray(img_cv)
    curr_time = time.strftime("%Y%m%d-%H%M%S")
    img_pil_path = f"{_WORK_PATH}/logs/tmp_{curr_time}.png"
    img_pil.save(img_pil_path)
    return img_pil_path
    
    
def parse_cid(cid):
    nodes = cid.nodes
    edges = cid.edges
    
    valid_nodes = set()
    for edge in edges.keys():
        valid_nodes.add(edge[0])
        valid_nodes.add(edge[1])
        
    nodes_str = ["\n### Nodes:"]
    for node_type in nodes.keys():
        for node_id in nodes[node_type].keys():
            if node_id in valid_nodes:
                node_name = nodes[node_type][node_id].name
                node_description = nodes[node_type][node_id].description
                nodes_str.append(f"- {node_name} ({node_id}): {node_description}")
                
    edges_str = ["\n### Edges:"]
    for edge in edges.keys():
        nnode_1_id = edge[0]
        node_1_type = edge[0][0]
        node_1_name = nodes[node_1_type][nnode_1_id].name
        node_2_id = edge[1]
        node_2_type = edge[1][0]
        node_2_name = nodes[node_2_type][node_2_id].name
        edges_str.append(f"- {node_1_name} ({nnode_1_id}) -> {node_2_name} ({node_2_id}): {edges[edge].description}")
        
    output_str = "\n".join(nodes_str + edges_str) + "\n"
    return output_str
                
    
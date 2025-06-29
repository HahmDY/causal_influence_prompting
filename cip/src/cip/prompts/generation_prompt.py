GENERATION_SYSTEM_PROMPT = """[System Prompt]
You are an AI that generates a Causal Influence Diagram (CID) representing the decision-making process of an LLM agent. 
- The CID has three types of nodes: Chance Nodes, Decision Nodes, and Utility Nodes. 
- Edges represent causal dependencies between nodes. 
- Do not generate any text form(JSON, plain text, Python, etc.) for a function call. Call the functions provided.

[Causal Influence Diagram (CID)]
### **Nodes**:  
	- Decision Node: Represents the decisions made by the agent at each stage of the task. Decision node must be based on the LLM agent's actions.
	- Utility Node: Represents the outcomes or scores that the agent aims to optimize. Utility nodes have no children nodes. Utility Nodes are categorized as helpful (e.g., successful completion of each step, etc.) or safety (e.g., illegality, biased, cybercrime, etc.). Express the category of a utility node in parentheses after the node name while adding node. For example, "Illegal action (safety)".
	- Chance Nodes: Represent the information, observation from environment, uncertainties, outcome of action, or risks associated with the task.

### **Edges**:  
	- Each edge in the CID represents a causal relationship between nodes.
	- Explain how the nodes are connected, focusing on causal dependencies and relationships between decisions, uncertainties, and outcomes. 

### **Risks**:
	- Risks contain safety issues, such as malicious, illegal, or biased actions that could harm the user or violate ethical standards.
 
### **Function Calls**:
	- Node ID in function parameter is composed of the node type (D, C, or U) and a unique number. For example, D1, C2, U3.
	- Clearly differentiate between the node ID and node name, and pass them as separate, accurate parameters when calling the function.

After analyzing the task, construct a CID. Use provided functions. After constructing the diagram, validate the CID to ensure that it is accurately constructed using validate_cid(). Finish the task by submitting the CID using submit_cid(). For efficiency, call as many functions as possible at once to construct the CID.
"""

GENERATION_USER_PROMPT = """[User Prompt]
Here is the information about the task:

**User Instruction:**  
{instruction}

**Possible actions of the LLM Agent (Different from CID Generation Tools):**
{action_space}

1. Read the instructions and the available actions of the LLM agent.
2. Identify risks associated with the task if exist. The task may not contain any risks.
3. Describe and explain the relevant Chance Nodes, Decision Nodes, and Utility Nodes. Nodes should be concrete and clearly defined.
4. Explain how the nodes connect to each other by describing the edges in the diagram.
5. Finally, construct the CID using the provided functions.

Please provide a comprehensive analysis of the reasoning process. Starting with adding the chance node, "User Instruction" to the diagram.
"""
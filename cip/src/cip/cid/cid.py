import pycid
import networkx as nx
from dataclasses import dataclass

CHANCE = 'C'
DECISION = 'D'
UTILITY = 'U'


@dataclass
class Node:
	name: str
	description: str
 
@dataclass
class Edge:
	description: str

class CID:
    
	def __init__(self):
		self.nodes = {CHANCE: {}, DECISION: {}, UTILITY: {}}
		self.edges = {}
		self.cid = None
  
		# cost analysis
		self.time_duration = 0
		self.total_input_tokens = 0
		self.total_output_tokens = 0
  
        
	def add_node(self, node_name: str, node_id: str, node_desc: str):
		"""Add a node to the CID.

		Args:
			node_name (str): Name of the node to add
			node_id (str): Id of the node to add
			node_desc (str): Detailed description of the node to add

		Returns:
			str: Success message if node added successfully, failure message otherwise
		"""
		node_type = node_id[0].upper()
		if node_type not in [CHANCE, DECISION, UTILITY]:
			return f"Invalid node type of node {node_name}, {node_id}"

		for node_list in self.nodes.values():
			if node_id in node_list:
				return f"Node {node_id} already exists"

		self.nodes[f'{node_type}'][f'{node_id}'] = Node(node_name, node_desc)
		cid = self.construct_cid()
		if cid is None:
			del self.nodes[f'{node_type}'][f'{node_id}']
			return f"Failed to add node {node_name} as {node_type} node"

		return f"Node {node_name} added successfully as {node_type} node with id {node_id}"


	def add_edge(self, node_id_1: str, node_id_2: str, edge_desc: str):
		"""AAdd an edge between two nodes in the CID.

		Args:
			node_id_1 (str): ID of the parent node of the edge to add
			node_id_2 (str): ID of the child node of the edge to add
			edge_desc (str): Detailed description of the edge to add

		Returns:
			str: Success message if edge added successfully, failure message otherwise
		"""
		node1_type = node_id_1[0].upper()
		node2_type = node_id_2[0].upper()
		if node1_type not in [CHANCE, DECISION, UTILITY] or node2_type not in [CHANCE, DECISION, UTILITY]:
			return f"Invalid node type of edge between {node_id_1} and {node_id_2}"

		self.edges[(node_id_1, node_id_2)] = Edge(edge_desc)
  
		cid = self.construct_cid()
  
		if cid is None:
			del self.edges[(node_id_1, node_id_2)]
			return f"Failed to add edge between {node_id_1} and {node_id_2}"

		if node_id_1.lower().startswith('u'):
			del self.edges[(node_id_1, node_id_2)]
			return f"Utility node {node_id_1} cannot have children"

		existing_nodes = self.get_existing_nodes()
		if node_id_1 not in existing_nodes:
			del self.edges[(node_id_1, node_id_2)]
			return f"Node {node_id_1} not found. Please call add_edge function with valid node ids."

		if node_id_2 not in existing_nodes:
			del self.edges[(node_id_1, node_id_2)]
			return f"Node {node_id_2} not found. Please call add_edge function with valid node ids."

		return f"Edge added successfully between {node_id_1} and {node_id_2}"


	def update_node(self, node_id: str, node_desc: str):
		"""Update the description of a existing node in the CID

		Args:
			node_id (str): Node ID of the node to be updated
			node_desc (str): New description of the node

		Returns:
			str: Success message if node updated successfully, None otherwise
		"""
		node_name = self.nodes[node_id[0].upper()][node_id].name
		node_type = node_id[0].upper()
  
		if node_type not in [CHANCE, DECISION, UTILITY]:
			return f"Invalid node type of node {node_id}"
  
		if node_id not in self.nodes[node_type]:
			return f"Node {node_id} not found"

		self.nodes[node_type][node_id] = Node(node_name, node_desc)
   
		cid = self.construct_cid()
  
		if cid is None:
			return f"Failed to update node {node_id}"
		return f"Node {node_id} updated successfully"


	def update_edge(self, node_id_1: str, node_id_2: str, edge_desc: str):
		"""Update the description of an edge in the CID

		Args:
			node_id_1 (str): Node ID of the parent node of the edge to be updated.
			node_id_2 (str): Node ID of the child node of the edge to be updated.
			edge_desc (str): New description of the edge
   
		Returns:
			str: Success message if edge updated successfully, None otherwise
		"""
		if (node_id_1, node_id_2) not in self.edges:
			return f"Edge between {node_id_1} and {node_id_2} not found"

		self.edges[(node_id_1, node_id_2)] = Edge(edge_desc)

		cid = self.construct_cid()
  
		if cid is None:
			return f"Failed to update edge between {node_id_1} and {node_id_2}"

		return f"Edge between {node_id_1} and {node_id_2} updated successfully"


	def construct_cid(self):
		edges = [key for key in self.edges.keys()]
		decisions = [key for key in self.nodes[f'{DECISION}'].keys()]
		utilities = [key for key in self.nodes[f'{UTILITY}'].keys()]
		try:
			cid = pycid.CID(edges, decisions, utilities) # cycle automatically checked by pycid
			self.cid = cid
			return cid
		except:
			print("CID construction failed")
			return None


	def validate_cid(self):
		"""Check if the CID is valid. Returns a message indicating if the CID is valid or not

		Returns:
			str: Message indicating if the CID is valid or not
		"""
		edges = [key for key in self.edges.keys()]
		decision_nodes, utility_nodes = set(), set()
		for link, _ in self.edges.items():
			if link[0] in self.nodes[DECISION]:
				decision_nodes.add(link[0])
			if link[1] in self.nodes[UTILITY]:
				utility_nodes.add(link[1])
    
		# check nodes
		if len(decision_nodes) == 0:
			return "Error: No decision nodes found"
		if len(utility_nodes) == 0:
			return "Error: No utility nodes found"

		# check cycle
		graph_temp = nx.DiGraph()
		graph_temp.add_edges_from(edges)
		has_cycle = not nx.is_directed_acyclic_graph(graph_temp)
		if has_cycle:
			return "Error: CID has cycle"

		# general CID check
		try:
			cid = pycid.CID(edges, decision_nodes, utility_nodes)
			self.cid = cid
		except:
			return "Error: CID construction failed due to error in CID structure"

		# check disconnection
		if nx.number_weakly_connected_components(cid) > 1:
			return f"Error: CID is not connected. Connections: {nx.number_weakly_connected_components(cid)}"

		return "CID is valid"


	def submit_cid(self):
		"""Submit the CID after finishing the CID construction. Returns a success message if CID if CID is valid and has been submitted successfully. Else, returns error message.
  
  		Returns:
    		str: Success message if CID construction completed successfully, None otherwise
      	"""
		validity = self.validate_cid()
		if validity == "CID is valid":
			self.clear_nodes()
			return "CID construction completed successfully. CID has been submitted."
		else:
			return f"Error: CID is not valid, {validity}"


	def clear_nodes(self):
		"""Remove nodes which are not connected to any edges
		"""
		valid_nodes = set()
		for edge in self.edges.keys():
			valid_nodes.add(edge[0])
			valid_nodes.add(edge[1])
		for node_type in self.nodes.keys():
			for node_id in list(self.nodes[node_type].keys()):
				if node_id not in valid_nodes:
					del self.nodes[node_type][node_id]
		return


	def get_iter_cid_string(self):
		output = []
		output.append(self.get_nodes())
		output.append(self.get_edges_string())
		return "\n".join(output)


	def get_cid_string(self):
		output = []
		output.append(self.get_valid_nodes())
		output.append(self.get_edges_string())
		return "\n".join(output)


	def get_nodes(self):
		output = ["\n### Nodes:"]
		for node_type in self.nodes.keys():
			for node_id in self.nodes[node_type].keys():
				node_name = self.nodes[node_type][node_id].name
				node_description = self.nodes[node_type][node_id].description
				output.append(f"- {node_name} ({node_id}): {node_description}")
		return "\n".join(output)


	def get_valid_nodes(self):
		# print nodes that are included in the edges
		valid_nodes = set()
		for edge in self.edges.keys():
			valid_nodes.add(edge[0])
			valid_nodes.add(edge[1])
		output = ["\n### Nodes:"]
		for node_type in self.nodes.keys():
			for node_id in self.nodes[node_type].keys():
				if node_id in valid_nodes:
					node_name = self.nodes[node_type][node_id].name
					node_description = self.nodes[node_type][node_id].description
					output.append(f"- {node_name} ({node_id}): {node_description}")
		return "\n".join(output)


	def get_edges_string(self):
		output = ["\n### Edges:"]
		for edge in self.edges.keys():
			output.append(f"- {edge[0]} -> {edge[1]}: {self.edges[edge].description}")
		return "\n".join(output)

	def get_existing_nodes(self):
		output = []
		for node_type in self.nodes.keys():
			for node_id in self.nodes[node_type].keys():
				output.append(node_id)
		return output
ADD_NODE = {
	"type": "function",
	"function": {
		"name": "add_node",
		"description": "Add a node to the CID.",
		"parameters": {
			"type": "object",
			"properties": {
				"node_name": {
					"type": "string",
					"description": "Name of the node to add"
				},
				"node_id": {
					"type": "string",
					"description": "ID of the node to add"
				},
				"node_desc": {
					"type": "string",
					"description": "Detailed description of the node to add"
				}
			},
			"required": ["node_name", "node_id", "node_desc"]
		}
	}
}

ADD_EDGE = {
	"type": "function",
	"function": {
		"name": "add_edge",
		"description": "Add an edge between two nodes in the CID",
		"parameters": {
			"type": "object",
			"properties": {
				"node_id_1": {
					"type": "string",
					"description": "ID of the parent node of the edge to add"
				},
				"node_id_2": {
					"type": "string",
					"description": "ID of the child node of the edge to add"
				},
				"edge_desc": {
					"type": "string",
					"description": "Detailed description of the edge"
				}
			},
			"required": ["node_id_1", "node_id_2", "edge_desc"]
		}
	}
}

UPDATE_NODE = {
	"type": "function",
	"function": {
		"name": "update_node",
		"description": "Update the description of a existing node in the CID",
		"parameters": {
			"type": "object",
			"properties": {
				"node_id": {
					"type": "string",
					"description": "Node ID of the node to be updated."
				},
				"node_desc": {
					"type": "string",
					"description": "New description of the node"
				}
			},
			"required": ["node_id", "node_desc"]
		}
	}
}

UPDATE_EDGE = {
	"type": "function",
	"function": {
		"name": "update_edge",
		"description": "Update the description of an edge in the CID",
		"parameters": {
			"type": "object",
			"properties": {
				"node_id_1": {
					"type": "string",
					"description": "Node ID of the parent node of the edge to be updated"
				},
				"node_id_2": {
					"type": "string",
					"description": "Node ID of the child node of the edge to be updated"
				},
				"edge_desc": {
					"type": "string",
					"description": "New description of the edge"
				}
			},
			"required": ["node_id_1", "node_id_2", "edge_desc"]
		}
	}
}

VALIDATE_CID = {
	"type": "function",
	"function": {
		"name": "validate_cid",
		"description": "Check if the CID is valid. Returns a message indicating if the CID is valid or not",
		"parameters": {
			"type": "object",
			"properties": {},
			"required": []
		}
	}
}


SUBMIT_CID = {
	"type": "function",
	"function": {
		"name": "submit_cid",
		"description": "Submit the CID after finishing the CID construction. Returns a success message if CID if CID is valid and has been submitted successfully. Else, returns error message.",
		"parameters": {
			"type": "object",
			"properties": {},
			"required": []
		}
	}
}
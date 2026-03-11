story_setup_schema = {
    "type": "object",
    "properties": {
        "scenario_list": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}


character_setup_schema = {
    "type": "object",
    "properties": {
        "notebook_list": {
            "type": "array",
            "description": "list of key details about the user's character",
            "items": {"type": "string"}
        },
        "attribute_list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "attribute": {
                        "type": "string"
                    },
                    "attribute_type": {
                        "type": "string",
                        "enum": ["open-ended", "rating","category"]
                    },
                    "attribute_value": {
                        "oneOf": [
                            {
                                "type": "integer"
                            },
                            {
                                "type": "string",
                                "enum": ["very low", "low", "medium", "high", "very high"]
                            }
                        ]
                    }
                },
                "required": ["attribute", "attribute_type", "attribute_value"],
                "additionalProperties": False
            }
        }
    },
    "required": ["notebook_list", "attribute_list"],
    "additionalProperties": False
}


new_region_schema = {
    "name": "create_region",
    "parameters":{
        "type": "object",
        "properties": {
            "feature_id": {
                "type": "integer"
            },
            "title": {
                "type": "string",
                "description": "1-4 words"
            },
            "visible_description": {
                "type": "string",
                "description": "Describe what the player expects to find at the location"
            },
            "hidden_description": {
                "type": "string",
                "description": "Explicit hidden lore and story prompts that the player will discover by investigating the location"
            }
        },
        "required": ["feature_id", "title", "visible_description", "hidden_description"]
    }
}

summary_schema = {
    "name": "generate_summary",
    "parameters": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "Very short summary of the character's experience"
            }
        },
        "required": ["summary"],
        "additionalProperties": False
    }
}





scene_schema = {
    "type": "object",
    "properties": {
        "interaction_description": {"type": "string"},
        "actions": {
            "type": "array",
            "description": "a list of 2-4 actions that the user can choose",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "exit_flag": {"type": "boolean"},
                    "probability": {"type": "integer"}
                },
                "required": ["action", "exit_flag"],
                "additionalProperties": False
            }
        }
    },
    "required": ["interaction_description", "actions"],
    "additionalProperties": False
}


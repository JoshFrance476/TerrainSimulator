story_setup_schema = {
    "type": "object",
    "properties": {
        "story_list": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

scene_setup_schema = {
    "type": "object",
    "properties": {
        "scene_prompt": {
            "type": "string",
            "description": "A short sentence to prompt the LLM"
        },
        "environment_description": {
            "type": "string",
            "description": "A sentence describing the scene's location"
        }
    },
    "required": ["scene_prompt", "environment_description"]
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
        "interaction_description": {
            "type": "string",
            "description": "A second-person scene description under 50 words"
            },
        "actions": {
            "type": "array",
            "description": "2-4 player actions",
            "minItems": 2,
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "A short action label under 15 words"
                        },
                    "exit_flag": {
                        "type": "boolean",
                        "description": "True if this action ends the current tile interaction"
                        },
                    "probability": {
                        "type": "integer",
                        "description": "Chance of success as a percentage",
                        "minimum": 0,
                        "maximum": 100
                        }
                },
                "required": ["action", "exit_flag", "probability"],
                "additionalProperties": False
            }
        }
    },
    "required": ["interaction_description", "actions"],
    "additionalProperties": False
}


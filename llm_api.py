from openai import OpenAI

client = OpenAI(
    api_key="sk-553c67c3eeb6442ba324f3c72cd44998",
    base_url="https://api.deepseek.com"
)


event_schema = [{
    "type": "function",
    "function": {
        "name": "generate_event",
        "description": "Generate an event with description and effects",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "coords": {"type": "array",
                           "items": {"type": "integer"},
                            "minItems": 2,
                            "maxItems": 2},
                "effects": {"type": "object",
                        "properties": {
                            "population": {"type": "integer"},
                }}},
            "required": ["description", "effects"]
        }
    }
}]

desc_schema = [{
    "type": "function",
    "function": {
        "name": "generate_description",
        "description": "Generate a creative description of this settlement",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
            },
            "required": ["description"]
        }
    }
}]

def ask_deepseek(prompt, schema, model="deepseek-chat", temperature=1.5):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a worldbuilder for a grid-based simulation game. Generate settlement descriptions (landscape, culture, architecture, mood)."},

            {"role": "user", "content": prompt}
        ],
        tool_choice={"type": "function", "function": {"name": schema[0]["function"]["name"]}},
        temperature=temperature,
        stream=False
    )
    #print(response.choices[0].message.tool_calls[0].function.arguments)
    return response.choices[0].message.content

if __name__ == "__main__":
    prompt = """
    Task:
        Write a short, one-sentence description of this settlement based on the context. 
        Describe the terrain, culture, architecture, and atmosphere.
        Context: Name: Placeholder, Row: 34, Col: 45, Population: 1.789:
    """
    event_json = ask_deepseek(prompt, desc_schema)
    print("LLM Response:", event_json)

#def generate_description(self):
#        prompt = f"""Task:
#        Write a short, one-sentence description of this settlement based on the context. 
#        Context: Name: {self.name}, Row: {self.r}, Col: {self.c}, Population: {self.population}, Region: {self._world_data['region'][self.r, self.c]}
#        """
#        self.description = ask_deepseek(prompt, desc_schema)
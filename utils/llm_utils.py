from openai import OpenAI
import os
client = OpenAI(
    api_key= os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
"sk-553c67c3eeb6442ba324f3c72cd44998",
"""
Given current token usage, we can get 10,000 responses from $1 (£0.82)
That's with output being one sentence and minimal context
Using ~50 tokens per response, 64 cache hits and 22 cache misses

Can either double response size, or ~quadruple input and still get 5,000 responses per $1
"""

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
        "description": "Generate a realistic description of this event",
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
            {"role": "system", "content": "You are a worldbuilder for a grid-based simulation game. You provide one-sentence summaries of events that take place in the world."},

            {"role": "user", "content": prompt}
        ],
        tool_choice={"type": "function", "function": {"name": schema[0]["function"]["name"]}},
        temperature=temperature,
        stream=False
    )
    print(response.usage)
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
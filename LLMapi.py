from openai import OpenAI

client = OpenAI(
    api_key="sk-553c67c3eeb6442ba324f3c72cd44998",
    base_url="https://api.deepseek.com"
)


schema = [{
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

def ask_deepseek(prompt, model="deepseek-chat", temperature=1.5):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You generate structured simulation events."},
            {"role": "user", "content": prompt}
        ],
        tools=schema,
        temperature=temperature,
        stream=False
    )
    return response.choices[0].message.tool_calls[0].function.arguments

if __name__ == "__main__":
    prompt = """
    Generate one event in JSON:
    Context: population=1200, cohesion=0.4, region='Grasslands'. coords = [34, 45]
    """
    event_json = ask_deepseek(prompt)
    print("LLM Response:", event_json)

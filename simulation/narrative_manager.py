from simulation.event import Event
from simulation.data_processor import DataProcessor
import concurrent.futures
from utils.llm_utils import desc_schema
from config import TOGGLE_LLM_EVENTS, LLM_THEME
from utils.llm_utils import ask_deepseek

class NarrativeManager:
    def __init__(self, world, event_manager):
        self.theme = LLM_THEME
        self.event_manager = event_manager
        self.data_processor = DataProcessor(world)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2) 
        self.world = world
        self.narrative_log = []
    
    def add_event(self, type, location, description):
        tick_count = self.world.tick_count
        new_event = Event(type, location, tick_count, description)
        self.event_manager.add_new_event(new_event)
        #if conditions are met then generate narrative for event
        if TOGGLE_LLM_EVENTS:
            self.generate_narrative(new_event)

    
    def generate_narrative(self, event):
        prompt = self.generate_prompt(event)
        print(prompt)

        future = self.executor.submit(ask_deepseek, prompt, desc_schema)

        def on_done(fut):
            try:
                narrative, actions = fut.result()
                event.add_event_narrative(narrative)
                print(narrative, actions)
            except Exception as e:
                print("LLM call failed:", e)

        future.add_done_callback(on_done)
    
    def generate_prompt(self, event):
        previous_events = [event for event in self.event_manager.get_event_log_by_vicinity(event.location, 10)]


        previous_event = previous_events[len(previous_events)-2]



        if event.event_type == "random_event":
            semantic_data = self.data_processor.generate_semantic_data(("region", "resource"), event.location)
            semantic_text = "; ".join(semantic_data)

            prompt = f"""
                An unspecified event has occurred in the area.
                Environment context:
                {semantic_text}
                Previous events in the area:
                {previous_event.narrative}
            """
        else:
            semantic_data = self.data_processor.generate_semantic_data(("region", "resource"), event.location)
            semantic_text = "; ".join(semantic_data)

            prompt = f"""
                Event:
                {event.description}
                Environment context:
                {semantic_text}
                Previous events in the area:
                {previous_event.narrative}
            """
    
        return prompt
import utils.llm_utils as llm_utils
import random
import numpy as np
import config as config
from utils.llm_utils import desc_schema
import concurrent.futures
from simulation.data_processor import DataProcessor


class EventManager:
    def __init__(self, world):
        self.event_log = []
        self.world = world
        self.data_processor = DataProcessor(world)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
    
    
    def add_new_event(self, event, tick_count, event_type, location):
        self.event_log.append({
            "tick_count": tick_count,
            "event_type": event_type,
            "location": location,
            "event_desc": event
        })

    def generate_event_with_probability(self, event_type, location, context_dict = {}, probability = 1):
        tick = self.world.tick_count
        previous_events = [entry["event_desc"] for entry in self.get_event_log_by_vicinity(location, 10)]
        if previous_events:
            previous_events = previous_events[-1]
        if event_type == "settlement founded":
            semantic_data = self.data_processor.generate_semantic_data(("region", "resource"), location)
            semantic_text = "; ".join(semantic_data)

            context_text = ", ".join(f"{k}: {v}" for k, v in context_dict.items())

            

            prompt = f"""
                A settlement has been founded in the area.
                Context:
                {context_text}
                Relevant information:
                {semantic_text}
                Previous events in the area:
                {previous_events}
            """
        elif event_type == "settlement growth":
            semantic_data = self.data_processor.generate_semantic_data(("region", "resource"), location)
            semantic_text = "; ".join(semantic_data)

            context_text = ", ".join(f"{k}: {v}" for k, v in context_dict.items())

            prompt = f"""
                A settlement has grown in the area.
                Context:
                {context_text}
                Relevant information:
                {semantic_text}
                Previous events in the area:
                {previous_events}
            """
        elif event_type == "random event":
            semantic_data = self.data_processor.generate_semantic_data(("region", "resource"), location)
            semantic_text = "; ".join(semantic_data)

            prompt = f"""
                A random event has occurred in the area.
                Relevant information:
                {semantic_text}
                Previous events in the area:
                {previous_events}
            """
        
        if config.TOGGLE_LLM_EVENTS:
            future = self.executor.submit(llm_utils.ask_deepseek, prompt, desc_schema)

            def on_done(fut, tick_count=tick, event_type=event_type, location=location):
                try:
                    result = fut.result()
                    self.add_new_event(result, tick_count, event_type, location)
                except Exception as e:
                    print("LLM call failed:", e)

            future.add_done_callback(on_done)
        else:
            self.add_new_event("An unidentified event has occurred in the area.", tick, event_type, location)

    def get_event_log(self):
        return self.event_log
    
    def filter_event_log_by_tick(self, tick_count):
        return [event for event in self.event_log if event["tick_count"] == tick_count]
    
    def filter_event_log_by_event_type(self, event_type):
        return [event for event in self.event_log if event["event_type"] == event_type]
    
    def filter_event_log_by_location(self, location):
        return [event for event in self.event_log if event["location"] == location]
    
    def get_event_log_by_vicinity(self, location, radius):
        events = []
        for event in self.event_log:
            if event["location"][0] in range(location[0] - radius, location[0] + radius) and event["location"][1] in range(location[1] - radius, location[1] + radius):
                events.append(event)
        return events
    
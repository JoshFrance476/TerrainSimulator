import llm_api
import random
import numpy as np
import utils.config as config
from llm_api import desc_schema
import concurrent.futures

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

    def generate_event_with_probability(self, event_type, context_dict, location, probability):
        tick = self.world.tick_count
        if event_type == "settlement founded":
            semantic_data = self.data_processor.generate_semantic_data(("region", "resource"), location)
            semantic_text = "; ".join(semantic_data)

            context_text = ", ".join(f"{k}: {v}" for k, v in context_dict.items())

            #previous_events = [entry["event_desc"] for entry in self.event_log.values() if "event_desc" in entry]


           #print(previous_events)

            prompt = f"""
                Context:\n {context_text}
                Relevant information:
                {semantic_text}
            """
            
            future = self.executor.submit(llm_api.ask_deepseek, prompt, desc_schema)

            def on_done(fut, tick_count=tick, event_type=event_type, location=location):
                try:
                    result = fut.result()
                    self.add_new_event(result, tick_count, event_type, location)
                except Exception as e:
                    print("LLM call failed:", e)

            future.add_done_callback(on_done)

    def get_event_log(self):
        return self.event_log
    
    def filter_event_log_by_tick(self, tick_count):
        return [event for event in self.event_log if event["tick_count"] == tick_count]
    
    def filter_event_log_by_event_type(self, event_type):
        return [event for event in self.event_log if event["event_type"] == event_type]
    
    def filter_event_log_by_location(self, location):
        return [event for event in self.event_log if event["location"] == location]
    
    
            



class DataProcessor:
    def __init__(self, world):
        self.world = world

    def generate_semantic_data(self, map_types, location):
        semantic_data = []
        for map_type in map_types:
            raw_data = self.world.get_surrounding_data_map(location[0], location[1], 5, map_type)
            if map_type == "region":
                ids, counts = np.unique(raw_data, return_counts=True)
                for id, count in zip(ids, counts):
                    region_name = config.REGION_RULES[id]["name"]
                    if count > 60:
                        semantic_data.append("Majority of the region is " + region_name)
                    if region_name == "mountains":
                        semantic_data.append("There are mountains in the region")
                    if region_name == "water":
                        semantic_data.append("There is sea nearby")

        return semantic_data



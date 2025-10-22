from scipy.linalg import norm
from utils.llm_utils import prompt_narrative
from simulation.storyline import Storyline
from simulation.data_processor import DataProcessor
import concurrent.futures
import numpy as np

class StorylineManager:
    def __init__(self, world):
        self.storylines = []
        self.max_storylines = 10
        self.storyline_count = 0
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
        self.data_processor = DataProcessor(world)
    
    def find_matching_storylines(self, event_location):
        storylines = []
        for storyline in self.storylines:
            if self.within_scope(storyline.scope, storyline.location, event_location):
                storylines.append(storyline)
        return storylines

    def within_scope(self, storyline_scope, storyline_location, event_location):
        if storyline_scope == "settlement":
            return storyline_location == event_location
        elif storyline_scope == "region":
            return norm(np.array(storyline_location) - np.array(event_location)) < 10
        return False

    def handle_event(self, event):
        future = self.executor.submit(self.process_event, event)
        future.add_done_callback(self.on_event_done)
    
    def on_event_done(self, fut):
        result = fut.result()
        self.print_storylines()
        print(f"Storyline updated: {result}")


    def process_event(self, event):
        relevant_storylines = self.find_matching_storylines(event.location)
        if len(relevant_storylines) == 0:
            if self.storyline_count < self.max_storylines:
                return self.create_new_storyline(event)
        else:
            return self.prompt_event(event, relevant_storylines)




    def create_new_storyline(self, event):
        semantic_data = self.data_processor.generate_semantic_data(("region", "resource"), event.location)
        semantic_text = "; ".join(semantic_data)

        prompt = f"""
            Event:
            {event.description}
            Environment context:
            {semantic_text}
        """
        print(prompt)
        narrative, actions, storyline, scope = prompt_narrative(prompt, with_storyline=True)
        new_storyline = Storyline(storyline, event.location, scope)
        event.narrative = narrative
        new_storyline.add_event(event)
        self.storylines.append(new_storyline)
        self.storyline_count += 1
        return new_storyline.overview
    
    def prompt_event(self, event, relevant_storylines):
        semantic_data = self.data_processor.generate_semantic_data(("region", "resource"), event.location)
        semantic_text = "; ".join(semantic_data)
        storylines_list = []

        for storyline in relevant_storylines:
            storylines_list.append(storyline.overview)
        storylines_text = "; ".join(storylines_list)

        prompt = f"""
            Event:
            {event.description}
            Relevant storylines:
            {storylines_text}
            Environment context:
            {semantic_text}
        """
        print(prompt)
        narrative, actions, new_storyline, scope = prompt_narrative(prompt, with_storyline=True)


        event.narrative = narrative

        for storyline in relevant_storylines:
            storyline.overview = new_storyline
            storyline.scope = scope
            storyline.add_event(event)
        
        return new_storyline
    
    def print_storylines(self):
        for storyline in self.storylines:
            print(storyline.overview)
            print(storyline.scope)
            for event in storyline.events:
                print(event.narrative)
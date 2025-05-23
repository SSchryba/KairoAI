from models.nlp_processor import NLPProcessor
from decision_engine import DecisionEngine

class DecisionEngine:
    def __init__(self, memory):
        self.memory = memory
        self.nlp = NLPProcessor()

    def process(self, input_data):
        self.memory.remember(input_data)
        return self.nlp.generate_response(input_data)

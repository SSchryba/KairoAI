from nlp_processor import NLPProcessor

class DecisionEngine:
    def __init__(self, memory):
        self.memory = memory
        self.nlp = NLPProcessor()

    def process(self, input_data):
        self.memory.remember(input_data)
        return self.nlp.generate_response(input_data)

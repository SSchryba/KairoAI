from memory import Memory # Corrected import path
from decision_engine import DecisionEngine # Added import

def launch_core():
    memory = Memory()
    brain = DecisionEngine(memory)

    while True:
        input_data = input(">> ")
        response = brain.process(input_data)
        print(response)

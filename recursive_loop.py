from core.memory import Memory
from recursive_loop import launch_cor

def launch_core():
    memory = Memory()
    brain = DecisionEngine(memory)

    while True:
        input_data = input(">> ")
        response = brain.process(input_data)
        print(response)

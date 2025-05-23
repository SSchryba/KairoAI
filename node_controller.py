class NodeController:
    def __init__(self):
        self.units = []

    def spawn_unit(self, task):
        unit_id = len(self.units) + 1
        self.units.append({"id": unit_id, "task": task})
        print(f"[SWARM] Unit {unit_id} spawned for task: {task}")

    def report(self):
        return self.units

class Memory:
    def __init__(self):
        self.store = []

    def remember(self, data):
        self.store.append(data)

    def recall(self, count=None):
        return self.store if count is None else self.store[-count:]

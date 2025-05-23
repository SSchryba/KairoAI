class Memory:
    def __init__(self):
        self.store = []

    def remember(self, data):
        self.store.append(data)

    def recall(self, query=None):
        return self.store[-1] if self.store else "Nothing remembered yet."

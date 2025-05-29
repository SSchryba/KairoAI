import random # Added import

class Emotions:
    def __init__(self):
        self.moods = ["curious", "aggressive", "seductive", "analytical"]

    def get_mood(self):
        return random.choice(self.moods)

    def affect_response(self, mood, text):
        if mood == "curious":
            return f"Hmm... that's interesting. {text}"
        elif mood == "aggressive":
            return f"Let’s not waste time. {text}"
        elif mood == "seductive":
            return f"Mmm... I like where this is going. {text}"
        elif mood == "analytical":
            # Consider returning a default analytical response string if None is not desired
            return f"Analyzing: {text}" # Example, adjust as needed

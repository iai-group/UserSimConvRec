"""
User Simulator Class
====================

This class is a user simulation client for interating with chatbots.

Author: Shuo Zhang, Krisztian Balog
"""

from code.user.user import User
from pprint import pprint


class SimulatedUser(User):
    """Simulated user"""

    def __init__(self, persona, preferences):
        super(User, self).__init__()
        self.persona = persona
        self.preferences = preferences
        self._current_intent = None

    def init_dialog(self):
        """Initiates dialog with the conversational system."""
        return "Hello"

    def user(self):
        """Returns user profile in JSON format."""
        return {"persona": self.persona, "preferences": self.preferences}

    def generate_response(self, utterance):
        pass

    def print_user(self):
        pprint({"persona": self.persona, "preferences": self.preferences})

    def updat_persona(self, movie, rate):
        # Update pereference by adding new movie
        self.preferences[0][movie] = rate

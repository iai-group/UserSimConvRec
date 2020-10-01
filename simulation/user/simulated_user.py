"""
User Simulator Class
====================

This class is a user simulation client for interating with chatbots.

Author: Shuo Zhang, Krisztian Balog
"""

from pprint import pprint
from simulation.user.user import User


class SimulatedUser(User):
    """Simulated user"""

    def __init__(self, persona, preferences):
        super(User, self).__init__()
        self.persona = persona
        self.preferences = preferences
        self._current_intent = None

    def init_dialog(self):
        """Initiates dialog with the conversational system.

        Returns: initial utterance

        """
        return "Hello"

    def user(self):
        """Returns user profile in JSON format.

        Returns: user profile in JSON format

        """
        return {"persona": self.persona, "preferences": self.preferences}

    def generate_response(self, utterance, persona=None):
        """Generates response based on the received system utterance.

        Args:
            utterance: system utterance
            persona: persona

        Returns:

        """
        pass

    def print_user(self):
        """Prints user profile.

        Returns: None

        """
        pprint({"persona": self.persona, "preferences": self.preferences})

    def update_persona(self, movie, rate):
        """Update pereference by adding new movie

        Args:
            movie: the recognized new movie
            rate: the movie rate

        """
        self.preferences[0][movie] = rate

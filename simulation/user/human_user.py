"""
Human ("interactive") User
==========================

Author: Krisztian Balog, Shuo Zhang
"""

from simulation.user.user import User


class HumanUser(User):
    """Human user"""

    def __init__(self):
        super(User, self).__init__()

    @staticmethod
    def _prompt_response():
        """Prompts user response.

        Returns: response

        """
        response = None
        while not response:
            response = input("USER> ")
        return response

    def init_dialog(self):
        """Initiates dialog with the conversational system.

        Returns: response

        """
        return self._prompt_response()

    def generate_response(self, utterance):
        """Generates response based on the received system utterance.

        Args:
            utterance: system utterance

        Returns: response

        """
        return self._prompt_response()

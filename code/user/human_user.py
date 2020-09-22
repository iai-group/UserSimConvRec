"""
Human ("interactive") User
==========================

Author: Krisztian Balog
"""

from code.user.user import User


class HumanUser(User):
    """Human user"""

    def __init__(self):
        super(User, self).__init__()

    def _prompt_response(self):
        """Prompts user response."""
        response = None
        while not response:
            response = input("USER> ")
        return response

    def init_dialog(self):
        """Initiates dialog with the conversational system."""
        return self._prompt_response()

    def generate_response(self, utterance):
        """Generates response based on the received system utterance."""
        return self._prompt_response()

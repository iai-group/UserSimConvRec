"""
Base bot class
==============


Author: Shuo Zhang
"""

from abc import ABC, abstractmethod


class Bot(ABC):
    """Bot abstract class"""

    def __init__(self):
        pass

    @abstractmethod
    def generate_response(self, text):
        """Generates responses based on the given text.

        Args:
            text: user reply

        Returns: agent resposne

        """
        pass

class Botbot(Bot):
    def __init__(self):
        super(Bot, self).__init__()

    def generate_response(self, text):
        return ""

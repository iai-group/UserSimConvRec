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

"""
Base (abstract) user class
==========================

Author: Krisztian Balog, Shuo Zhang
"""

from abc import ABC, abstractmethod


class User(ABC):
    """Base user class."""

    def __init__(self):
        pass

    @abstractmethod
    def init_dialog(self):
        """Initiates dialog with the conversational system.

        Returns:

        """
        pass

    @abstractmethod
    def generate_response(self, utterance, persona=None):
        """Generates response based on the received system utterance.

        Args:
            utterance: system utterance
            persona: persona

        Returns:

        """
        pass

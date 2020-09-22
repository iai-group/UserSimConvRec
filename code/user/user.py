"""
Base (abstract) user class
==========================

Author: Krisztian Balog
"""

from abc import ABC, abstractmethod


class User(ABC):
    """Base user class."""

    def __init__(self):
        pass

    @abstractmethod
    def init_dialog(self):
        """Initiates dialog with the conversational system."""
        pass

    @abstractmethod
    def generate_response(self, utterance):
        """Generates response based on the received system utterance."""
        pass

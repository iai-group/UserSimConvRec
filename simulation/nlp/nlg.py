"""
Natural Language Generator
==========================

Abstract class for generating natural language response.

Author Shuo Zhang
"""
from abc import ABC, abstractmethod


class NLG(ABC):
    """NLG abstract class"""
    def __init__(self):
        pass

    @abstractmethod
    def generate_response_text(self, intent, arguments=None):
        """Initializes any necessary components.

        Args:
            intent: agent intent
            arguments:

        Returns:
            a string for user utterance
        """
        return "NLG method: template + DL methods"

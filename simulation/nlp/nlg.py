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
    def generate_response_text(self, response):
        """Initializes any necessary components.

        Args:
            response: agent response

        Returns:
            a string for user utterance
        """
        return "NLG method: template + DL methods"

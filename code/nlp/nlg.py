"""
Natural Language Generator
==========================

Abstract class for generating natural language response.

Author Shuo Zhang
"""
from abc import ABC, abstractmethod


class NLG(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def generate_response_text(self, response):
        return "NLG method: template + DL methods"

"""
Simple NLG for the movie domain
===============================


Author: Krisztian Balog, Shuo Zhang
"""

from simulation.nlp.nlg import NLG
from simulation.nlp.movies import RESPONSE_TEMPLATES
import random


class MoviesNLG(NLG):
    """Movies NLG"""

    def __init__(self, response_template=RESPONSE_TEMPLATES):
        super(NLG, self).__init__()
        self._res_tempt = response_template

    def generate_response_text(self, intent, arguments=None):
        """Generate textual response."""
        if intent not in self._res_tempt:
            print('Exception in intent', intent)
            return None

        # select a random way using that template
        idx = random.randint(0, len(self._res_tempt[intent]) - 1)
        response_text = self._res_tempt[intent][idx]

        # substitute arguments
        if arguments:
            for arg, val in arguments.items():
                response_text = response_text.replace("{" + arg + "}", val)

        return response_text


if __name__ == "__main__":
    nlg = MoviesNLG()
    # example usage
    # Note: there should be a response generator class that generates a structured response
    # with an intent (key in RESPONSE_TEMPLATES) and optional arguments.
    print(nlg.generate_response_text("ask_genre"))
    print(nlg.generate_response_text("ask_movie_about"))
    print(nlg.generate_response_text("preference_actor_like", {"actor": "Brad Pitt"}))
    print(nlg.generate_response_text("preference_genre_like", {"genre": "action"}))
    # This one is just to illustrate a response with multiple arguments
    print(nlg.generate_response_text("book_tickets", {"day": "Friday", "time": "20:00"}))

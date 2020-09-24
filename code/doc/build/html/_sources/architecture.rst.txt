Simulation Architecture
=======================

The main architecture is shown in the figure below. A multi-turn conversation simulator is initiated. The agent's response is processed by the NLU. The response generation module receives the agents' dialogue acts from the NLU and generates the user's dialogue acts. Based on the act from response generation, the NLG generates a natural response to the agents. This loop happens for each turn in the conversation.

.. image:: _static/simulator_anatomy.pdf

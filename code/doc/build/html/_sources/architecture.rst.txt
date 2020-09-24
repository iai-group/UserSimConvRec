MovieBot architecture
=====================

The main architecture is shown in the figure below. A multi-turn conversation is initiated and terminated by the users. The users' response is processed by the NLU. The DM receives the users' dialogue acts from the NLU and generates the agent's dialogue acts. Based on the act from DM, the NLG generates a natural response to the users. This loop happens for each turn in the conversation.

.. image:: _static/simulator_anatomy.pdf

# JARVIS Research Dialogue System

We are trying to make changes in Plato Research Dialogue System according to Movie Recommendation dialogue system. Plato [v0.1]( https://github.com/uber-research/plato-research-dialogue-system/tree/f14f3c20d5a8fc473db00e68bf95acf58c0e0f8a ) is being used for these configurations.

# Quickstart Guide

## Installation

`pip install -r requirements.txt`

## Testing:

`python runJARVIS-RDS.py`

*The relevant configuration file is already embedded in the code*

## DialogueFlow:

For the dialogue flow shown below, some example conversations are also provided in folder [Examples](Examples).

![DialogChart.png](DialogChart.png)

- When the system asks for genres, one of the following options should be provided:
	- "War",
	- "Crime",
	- "Family",
	- "Western",
	- "Biography",
	- "Drama",
	- "Adventure",
	- "Fantasy",
	- "Film-Noir",
	- "Documentary",
	- "Thriller",
	- "Sport",
	- "Mystery",
	- "Comedy",
	- "History",
	- "Musical",
	- "Short",
	- "Horror",
	- "Animation",
	- "Sci-Fi",
	- "Action",
	- "Music",
	- "Romance",
	- "News"
## Deliverables:

Folder `Reports` must be delivered to implement feedback and debug the conversation.

## Challenges:

**Installation:** error during installing requirements:

``` Installing collected packages: wrapt, astor, tensorflow, ludwig` Found existing installation: wrapt 1.10.11 Cannot uninstall 'wrapt'. It is a distutils installed project and thus we cannot accurately determine which files belong to it
 which would lead to only a partial uninstall.```

**Solution:** By using command ```conda update --all``` , we can easily install the requirements without any glitch.


References:

Alexandros Papangelis, Yi-Chia Wang, Piero Molino, and Gokhan Tur,
“Collaborative Multi-Agent Dialogue Model Training Via Reinforcement Learning”,
SIGDIAL 2019 [[paper](https://arxiv.org/abs/1907.05507)]

# Evaluating Conversational Recommender Systems via User Simulation

[![Documentation Status](https://readthedocs.org/projects/usersimconvrec/badge/?version=latest)](https://usersimconvrec.readthedocs.io/en/latest/?badge=latest)

This repository contains resources developed within the following paper:

> S. Zhang and K. Balog. Evaluating Conversational Recommender Systems via User Simulation. In: *Proceedings of 26th SIGKDD Conference on Knowledge Discovery and Data Mining*, August 22 - 27, 2020 - San Diego, CA - USA..

## Simulated Framework

![Illustration of simulation](https://github.com/iai-group/UserSimConvRec/blob/master/data/simulator_anatomy.png)


### Simulated User

The simulated user consists of the following main components, which are natural language understanding, natural language generation, and response generation. 

#### Natural Language Understanding (NLU)
We use retrieve-based NLU, see [here](https://github.com/iai-group/UserSimConvRec/blob/master/simulation/nlp/movies/movies_nlu.py) for more details.

#### Natural Language Generation (NLG)
We use template-based NLG, see [here](https://github.com/iai-group/UserSimConvRec/blob/master/simulation/nlp/movies/movies_nlu.py) for more details

#### Response Generation
##### Iteratction Model
We support QRFA and CIR6 models with PKG.

##### Preference Model

* To enable the preferece model of the simualted users, we utilize the MovieLens dataset (Please download the movieLens dataset [here](https://www.kaggle.com/rounakbanik/movie-recommender-systems/data) and put under the folder of `data`). 

* The `simulation/user/user_generator.py` aims to generate the simulated perference model with PKG.

### Conversational Agent

In this paper, we investigate three movie chat bots like `And chill`, `movie bot`, and `jmrs1`.

* [And chill](http://www.andchill.io/) is a single-purpose, consumer-oriented chatbot that a user can send messages to on Facebook and ask for a Netflix recommendation. After answering a few questions such as a liked movie and the reason why liking it, the agent sends movie recommendations based on the user’s preferences. Given the access restrictions, we do not provide the wrapper for Andchill.

* [Kelly Movie Bot](https://github.com/Sundar0989/Movie_Bot) is a simple bot that answers questions about a specific movie, such as rating, genre, and can also recommend similar movies. The underlying data collection is the Kaggle Movies Recommender System dataset,4 which is based on the MovieLens dataset. The natural language components utilize. Follow this [link](https://github.com/Sundar0989/Movie_Bot) to set up the bot for your own interest. The workspace file for training the agent on IBM lies `data/IBM_workspace.json`.

* [jmrs1](https://github.com/iai-group/UserSimConvRec/tree/master/simulation/bot/jmrs1) was developed by us. It has been provided in `simulation/bot`. This is the meta version of [IAI Movie Bot](https://github.com/iai-group/moviebot), which is described in a demo paper that is to appear at CIKM'20 (see [arXiv version](https://arxiv.org/abs/2009.03668)).

In this code base, we only provide the implementation for `jmrs1' given the license restrictions.

## Run

1. ``Git clone https://github.com/iai-group/UserSimConvRec.git``

2. Download `ratings.csv` and `movies_metadata.csv` from [here](https://www.kaggle.com/rounakbanik/the-movies-dataset) and place them in `data` folder

3. Run ``python3 data/data_pre.py``

4. Run ``python3 -m simulation.dialog.conv_man``

## Citation
```
@inproceedings{Zhang:2020:ECR,
  author = {Zhang, Shuo and Balog, Krisztian},
  title = {Evaluating Conversational Recommender Systems via User Simulation},
  year = {2020},
  booktitle = {Proceedings of the 26th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining},
  pages = {1512–1520},
  numpages = {9},
  keywords = {conversational recommendation, user simulation, conversational information access},
  location = {Virtual Event, CA, USA},
  series = {KDD '20}
}
```
To leverage bot `jmrs1`, please cite:
```
@inproceedings{Habib:2020:IMC,
	author = {Habib, Javeria and Zhang, Shuo and Balog, Krisztian},
	title = {IAI {MovieBot}: {A} Conversational Movie Recommender System},
	year = {2020},
	booktitle = {Proceedings of the 29th ACM International Conference on Information and Knowledge Management},
	series = {CIKM '20}
}
```

## Contact
If you have any questions, please contact Shuo Zhang at imsure318@gmail.com or Krisztian Balog at krisztian.balog@uis.no.

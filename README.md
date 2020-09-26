# Evaluating Conversational Recommender Systems via User Simulation

[![Documentation Status](https://readthedocs.org/projects/usersimconvrec/badge/?version=latest)](https://usersimconvrec.readthedocs.io/en/latest/?badge=latest)

This repository contains resources developed within the following paper:

> S. Zhang and K. Balog. Evaluating Conversational Recommender Systems via User Simulation. In: *Proceedings of 26th SIGKDD Conference on Knowledge Discovery and Data Mining*, August 22 - 27, 2020 - San Diego, CA - USA..

## Data

Download the movieLen dataset [here](https://www.kaggle.com/rounakbanik/movie-recommender-systems/data) and put under the folder of `code/data`

## Bot

In this paper, we investigate serveral movie chat bots like movie bot, and chill and jmrs.

* jmrs is provided in `simulation/bot`.

* Given the access restrictions, we do not provide the wrapper for Andchill.

* Movie bot: Follow this [link](https://github.com/Sundar0989/Movie_Bot) to set up the bot for your own interest. The workspace file for training the agent on IBM lies `code/data/IBM_workspace.json`.

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

## Contact
If you have any questions, please contact Shuo Zhang at imsure318@gmail.com.

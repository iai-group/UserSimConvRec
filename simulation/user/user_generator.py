"""
Initial User Profile Generator
==============================

Generate initial user profiles based on actual movielens users

    - http://files.grouplens.org/datasets/movielens/ml-20m-README.html

User profile logic:
    Persona:
        empty for now.
    Preferences:
        Sample from the real users using MovieLens 20M Dataset


Author: Shuo Zhang
"""

import os
import csv
import random
from simulation.user.simulated_user import SimulatedUser

MOVIELEN_PATH = ""
MOVIE_FILE = "data/movies.csv"
RATING_FILE = "data/ratings.csv"


class UserGenerator:
    """Class for generating random users."""

    def __init__(self):
        self.__mov = self.movies()

    @staticmethod
    def movies():
        """Loads movies with genres.

        Returns: movie db

        """
        mov = dict()
        with open(os.path.join(MOVIELEN_PATH, MOVIE_FILE)) as movie_file:
            csv_data = csv.reader(movie_file)
            next(csv_data, None)
            for line in csv_data:
                mov[line[0]] = {"title": line[1], "genres": line[2]}
        return mov

    @staticmethod
    def samp(pro, dist, attribute):
        """Based on random generated probability, determine the persona category.

        Args:
            pro: probablity
            dist: probability distribution
            attribute: attribute

        Returns: persona category

        """
        acc_pro = 0
        for i, item in enumerate(dist):
            acc_pro += item
            if pro < acc_pro:
                return attribute[i]
        return

    @staticmethod
    def rate_pre(rate, upper_limit=4, lower_limit=2):
        """Rates the preference.

        Args:
            rate: movie rate
            upper_limit: threshold of being positive
            lower_limit: threshold of being negative

        Returns: rating

        """
        if float(rate) >= upper_limit:
            return 1
        elif float(rate) <= lower_limit:
            return -1
        else:
            return 0

    def rates(self, if_title=True):
        """Dumps the ratings to get genres preferences over files.

        genre_preference = sum preference_of_movie_has_this_genre / num_of_movie_has_this genre

        Args:
            if_title: to display movie id or movie title

        Returns: all user ratings

        """
        user_all = {}
        self.__mov = self.movies()
        with open(os.path.join(MOVIELEN_PATH, RATING_FILE)) as rating_file:
            csv_data = csv.reader(rating_file)
            next(csv_data, None)
            for i, line in enumerate(csv_data):
                if i == 500000:
                    break
                user_id, movie_id, rating, _ = line
                genres = self.__mov.get(movie_id).get("genres")
                title = self.__mov.get(movie_id).get("title")
                if user_id not in user_all:
                    user_all[user_id] = {"movies": {}, "genres": {}}
                if if_title:
                    user_all[user_id]["movies"][title] = self.rate_pre(rate=rating)
                else:
                    user_all[user_id]["movies"][movie_id] = self.rate_pre(rate=rating)
                for genre in genres.split("|"):
                    if genre not in user_all[user_id]["genres"]:
                        user_all[user_id]["genres"][genre] = []
                    user_all[user_id]["genres"][genre].append(rating)
        return user_all

    def initial(self, num_user=5, num_movie=8, num_genre=8, if_title=True):
        """Creates example initial user profiles.

        Args:
            num_user: number of examples users
            num_movie: number of movies with references
            num_genre: number of geners with references
            if_title: to dispplay movie id or movie title

        Returns: all users

        """
        user_all = self.rates(if_title=if_title)
        users = list()
        for _ in range(num_user):
            user_id = str(random.randint(1, 700))
            movie = {v: user_all.get(user_id).get("movies")[v] for v in
                     [list(user_all.get(user_id).get("movies").keys())[k]
                      for k in range(num_movie)]}
            genres = user_all.get(user_id).get("genres")
            genres_norm = {k: self.rate_pre(sum([float(k) for k in v]) / len(v), 3.5, 2)
                           for k, v in genres.items()}
            genres_samp = {v: genres_norm[v] for v in [list(genres_norm.keys())[k]
                                                       for k in range(num_genre)]}
            user = SimulatedUser(persona={}, preferences=[movie, genres_samp])
            user.print_user()
            users.append(user)
        return users


if __name__ == "__main__":
    PERSON = UserGenerator()
    # print(PERSON.initial(num_user=10, num_movie=5, num_genre=5, if_title=True))

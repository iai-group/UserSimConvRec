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

from code.user.simulated_user import SimulatedUser
import random
import csv
import os

MOVIELEN_PATH = ""
MOVIE_FILE = "code/data/movies.csv"
RATING_FILE = "code/data/ratings.csv"


class UserGenerator:
    """Class for generating random users."""

    def __init__(self):
        self.__mov = self.movies()

    @staticmethod
    def movies():
        """Loads movies with genres."""
        mov = dict()
        with open(os.path.join(MOVIELEN_PATH, MOVIE_FILE)) as f:
            csv_data = csv.reader(f)
            next(csv_data, None)
            for i, line in enumerate(csv_data):
                mov[line[0]] = {"title": line[1], "genres": line[2]}
        return mov

    def samp(self, pro, dist, attribute):
        """Based on random generated probability, determine the persona category"""
        acc_pro = 0
        for i, item in enumerate(dist):
            acc_pro += item
            if pro < acc_pro:
                return attribute[i]

    @staticmethod
    def rate_pre(rate, divisions=[4, 2]):
        """Preference rate higher than 4 is taken as positive, lower than 2 is negative"""
        if float(rate) >= divisions[0]:
            return 1
        elif float(rate) <= divisions[1]:
            return -1
        else:
            return 0

    def rates(self, if_title=True):
        """
        Dump the ratings to get genres preferences over files.
        genre_preference = sum preference_of_movie_has_this_genre / num_of_movie_has_this genre

        :param if_title: to disp movie id or movie title
        :return:
        """
        user_all = {}
        self.__mov = self.movies()
        with open(os.path.join(MOVIELEN_PATH, RATING_FILE)) as f:
            csv_data = csv.reader(f)
            next(csv_data, None)
            for i, line in enumerate(csv_data):
                if i == 500000:
                    break
                userId, movieId, rating, timestamp = line
                genres = self.__mov.get(movieId).get("genres")
                title = self.__mov.get(movieId).get("title")
                if userId not in user_all:
                    user_all[userId] = {"movies": {}, "genres": {}}
                if if_title:
                    user_all[userId]["movies"][title] = self.rate_pre(rate=rating)
                else:
                    user_all[userId]["movies"][movieId] = self.rate_pre(rate=rating)
                for genre in genres.split("|"):
                    if genre not in user_all[userId]["genres"]:
                        user_all[userId]["genres"][genre] = []
                    user_all[userId]["genres"][genre].append(rating)
        return user_all

    def initial(self, num_user=5, num_movie=8, num_genre=8, if_title=True):
        """
        Create example initial user profiles.

        :param num_user: number of examples users
        :param num_movie: number of movies with references
        :param num_genre: number of geners with references
        :param if_title: to dispplay movie id or movie title
        :return:
        """
        user_all = self.rates(if_title=if_title)
        users = list()
        for i in range(num_user):
            userID = str(random.randint(1, 700))
            movie = {v: user_all.get(userID).get("movies")[v] for v in
                     [list(user_all.get(userID).get("movies").keys())[k] for k in range(num_movie)]}
            genres = user_all.get(userID).get("genres")
            genres_norm = {k: self.rate_pre(sum([float(k) for k in v]) / len(v), divisions=[3.5, 2]) for k, v in
                           genres.items()}
            genres_samp = {v: genres_norm[v] for v in [list(genres_norm.keys())[k] for k in range(num_genre)]}
            user = SimulatedUser(persona={}, preferences=[movie, genres_samp])
            user.print_user()
            users.append(user)
        return users


if __name__ == "__main__":
    per = UserGenerator()
    print(per.initial(num_user=10, num_movie=5, num_genre=5, if_title=True))

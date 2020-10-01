"""
Simple simulated user for the movie domain
==========================================

Author: Shuo Zhang
"""

import os
import json
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from simulation.user.movies import INTENT_MATCH, USER_TAG, AGENT_TAG, QUERY, \
    REQUEST, count, INTENT_MOVIE_LIST
from simulation.user.simulated_user import SimulatedUser
from simulation.user.user_generator import UserGenerator
from simulation.nlp.movies import RESPONSE_TEMPLATES_MS, RESPONSE_TEMPLATES_AC
from simulation.nlp.movies.movies_nlu import MoviesNLU
from simulation.nlp.movies.movies_nlg import MoviesNLG


def qrfa_agenda_generate(qrfa_file):
    """Generates agenda for QRFA.

    Args:
        file: annotated dialogue corpus

    Returns: agenda list

    """
    scores = {}
    diags = json.load(open(os.path.join("", qrfa_file)))
    for k, intent in diags.items():
        agenda = state_map(intent)
        tmp = []
        for i in range(1, len(agenda) - 2):
            tmp.append(count.get(agenda[i]).get(agenda[i + 1]))
        scores[k] = sum(tmp) / len(tmp)
    top_list = [j[0] for j in sorted(scores.items(), key=lambda kv: kv[1], reverse=True) if
                len([n for n in diags[j[0]] if n[0] == USER_TAG]) > 3][:10]
    agenda_list = [[m[2] for m in diags.get(item) if m[0] == USER_TAG] for item in top_list]
    return agenda_list


def state_map(agenda):
    """Builds the state map based on agenda.

    Args:
        agenda: agenda

    Returns: agenda map

    """
    agenda_map = []
    for item in agenda:
        if item[0] == USER_TAG:
            label = "QUERY" if item[2] in QUERY else "FEEDBACK"
        elif item[0] == AGENT_TAG:
            label = "REQUEST" if item[2] in REQUEST else "ANSWER"
        else:
            label = "MISSING"
        agenda_map.append(label)
    agenda_map = ["START"] + agenda_map + ["STOP"]
    return agenda_map


class MovieSimulatedUser(SimulatedUser, UserGenerator, MoviesNLG, MoviesNLU):
    """Simulated user for movie domain"""

    def __init__(self, dialogue_file, response_tempt=RESPONSE_TEMPLATES_MS, mode="ms"):
        super(SimulatedUser, self).__init__()
        super(MoviesNLG, self).__init__()
        super(MoviesNLU, self).__init__()
        self._file = dialogue_file
        self._res_tempt = response_tempt
        self._current_intent = None
        self.user = UserGenerator.initial(self, num_user=1)[0]
        self.persona = self.user.persona
        self.preferences = self.user.preferences
        self._agenda = []
        self._local = []
        self._mode = mode
        self._current_movie = None
        self._current_genre = None
        self.agenda_list, self.agenda_stat, self.agenda_stat_qrfa, self.intent_map, \
        self.agent_user_intent, self.tfidf_matrix, self.tfidf_fit = file_process(dialogue_file)
        self.metadata, self.titles_all, self.tfidf_fit_nlu, self.tfidf_matrix_nlu = \
            self.naive_index()

    @property
    def agenda(self):
        """Agenda property.

        Returns: agenda

        """
        return self._agenda

    def init_dialog(self):
        """Initiates dialog with the conversational system.

        Returns: initial utterance

        """
        self._current_intent = "Non-disclose"
        self._agenda.pop()
        return "Hello"

    def init_a(self, agenda_stat):
        """Initiates agenda stack by sampling push actions.

        Args:
            agenda_stat: agenda stat

        Returns: agenda stack

        """
        current = "Non-disclose"
        result = list()
        result.append(current)
        next_intent = self.next_action(agenda_stat.get(current, {}))
        while next_intent != "Stop":
            current = next_intent
            result.append(current)
            next_intent = self.next_action(agenda_stat.get(current, {}))
        return result

    def init_agenda(self):
        """Initiates/prints agenda stack by sampling push actions.

        Returns: agenda stack

        """
        result = self.init_a(agenda_stat=self.agenda_stat)
        while "Disclose" not in result[:5] or len(result) > 12:
            result = self.init_a(agenda_stat=self.agenda_stat)
        self._agenda = result
        self._agenda.reverse()
        print("The agenda is: {}".format(self._agenda))

    def init_agenda_qrfa(self):
        """Initiates agenda stack for QRFA model.

        Returns: updates agenda stack and prints out

        """
        agenda_list = qrfa_agenda_generate(qrfa_file=self._file)
        self._agenda = agenda_list[random.randint(0, len(agenda_list) - 1)]
        self._agenda.reverse()
        print("The agenda is: {}".format(self._agenda))

    def init_agenda_qrfa_test(self):
        """Tests of initiating agenda stack for QRFA model.

        Returns: updates agenda stack and prints out

        """
        result = self.init_a(agenda_stat=self.agenda_stat_qrfa)
        print("Result", result)
        result = [i for i in result if i not in ["REQUEST", "ANSWER"]]
        while "Disclose" not in result[:10] or len(result) > 40:
            result = self.init_a(self.agenda_stat_qrfa)
        result = [i for i in result if i not in ["REQUEST", "ANSWER"]]
        self._agenda = result
        self._agenda.reverse()
        print("The agenda is: {}".format(self._agenda))

    def generate_response(self, utterance, persona=None):
        """Generates response based on the received utterance.

        Args:
            utterance: reply from chatbot; relayed by conversation manager
            persona: user persona

        Returns: updated user response

        """
        # Updates the current user intent based on the last utterance.
        utterance = [utterance] if isinstance(utterance, str) else utterance
        response = {"intent": [self.annotate_bot_intent(i) for i in utterance]}
        if not self._agenda:
            return "Stop", response["intent"]
        # Bot replies with right intent
        if response["intent"][-1] in INTENT_MATCH.get(self._current_intent):
            self._current_intent = self._agenda.pop()
        else:
            self._current_intent = \
                self.next_action(self.agent_user_intent.get(response["intent"][-1]))

        # Generates response based on the case
        if self._mode == "ms":
            if not persona:
                if self._current_intent in ["Disclose", "Expand", "Revise", "Refine"]:
                    # Randomly sample a genre
                    genres = [k for k, v in self.user.user().get("preferences")[1].items()]
                    genre = genres[random.randint(0, len(genres) - 1)]
                    generated_response = self.generate_response_text(self._current_intent,
                                                                     {"genre": genre})
                else:
                    generated_response = self.generate_response_text(intent=self._current_intent)
                    # Avoid generate the same response for Repeat intent
                    while generated_response in self._local:
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
            else:  # User persona
                if self._current_intent in ["Disclose", "Expand", "Revise", "Refine"]:
                    genres = [k for k, v in self.user.user().get("preferences")[1].items() if
                              v == 1]  # Randomly sampled a favored genre
                    genre = genres[random.randint(0, len(genres) - 1)]
                    # Based on a movie and select a genre.....
                    generated_response = \
                        self.generate_response_text(self._current_intent, {"genre": genre})
                    self._current_genre = genre  # Update the current genre that the user disclose
                else:
                    if response["intent"][-1] in INTENT_MOVIE_LIST:  # Bot provides movie options
                        _, _, self._current_movie, current_movie_genre = \
                            self.link_entities(text=utterance[-1])[0]
                        # user has watched this movie
                        if self._current_movie in self.user.preferences[0]:
                            # when asked if has watched or not, force YES
                            if self._current_intent in ["Note-yes",
                                                        "Note"]:
                                self._current_intent = "Note-yes"
                            # when aske the reviews, assign the preference based on the personal
                            elif self._current_intent == "Disclose-review":
                                # lookup the persona to tell if like or dislike
                                if self.user.preferences[0].get(
                                        self._current_movie) == 1:
                                    self._current_intent = "Disclose-review-like"
                                else:
                                    self._current_intent = "Disclose-review-dislike"
                        else:  # user has not watched it yet
                            # user is about to give a final perference
                            if self._current_intent in ["Note-dislike", "Note-end",
                                                        "Complete"]:
                                # decide if like or dislike a movie based on personal genres
                                if sum([self.user.preferences[1].get(g, 0) for g in
                                        current_movie_genre]) >= 0:
                                    # force the intent as like
                                    self._current_intent = "Note-end"
                                    # update the movie into persona
                                    self.update_persona(self._current_movie, 1.5)
                                    # Empty the agenda and force to close the session
                                    self._agenda = []
                                else:
                                    self._current_intent = "Note-dislike"
                                    # update the movie into persona
                                    self.update_persona(self._current_movie, -1.5)
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
                    else:
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
                        # Avoid generate the same response for Repeat intent
                        while generated_response in self._local:
                            generated_response = \
                                self.generate_response_text(intent=self._current_intent)

        elif self._mode == "mb":
            if not persona:
                if self._current_intent in ["Disclose", "Revise"]:
                    movies = [k for k, v in self.user.user().get("preferences")[0].items()
                              if v == 1]
                    movie = movies[random.randint(0, len(movies) - 1)]
                    generated_response = self.generate_response_text(self._current_intent,
                                                                     {"movie": movie})
                else:
                    generated_response = \
                        self.generate_response_text(intent=self._current_intent)
                    # Avoid generate the same response for Repeat intent
                    while generated_response in self._local:
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
            else:
                if self._current_intent in ["Disclose", "Revise"]:
                    movies = [k for k, v in self.user.user().get("preferences")[0].items()
                              if v == 1]
                    movie = movies[random.randint(0, len(movies) - 1)]
                    generated_response = \
                        self.generate_response_text(self._current_intent, {"movie": movie})
                    self._current_movie = movie
                else:
                    # Bot provides movie options
                    if response["intent"][-1] in INTENT_MOVIE_LIST:
                        _, _, self._current_movie, current_movie_genre = \
                            self.link_entities(text=utterance[-1])[0]
                    if response["intent"][-1] in ["Subset", "Show"]:
                        # user is about to give a final perference
                        if self._current_intent in ["Note-dislike", "Note",
                                                    "Complete"]:
                            # decide if like or dislike a movie based on personal genres
                            if sum([self.user.preferences[1].get(g, 0) for g in
                                    current_movie_genre]) >= 0:
                                # force the intent as like
                                self._current_intent = "Note"
                                # update the movie into persona
                                self.update_persona(self._current_movie, 1.5)
                                # Empty the agenda and force to close the session
                                self._agenda = []
                            else:
                                self._current_intent = "Note-dislike"
                                # update the movie into persona
                                self.update_persona(self._current_movie, -1.5)
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
                    else:
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
                        # Avoid generate the same response for Repeat intent
                        while generated_response in self._local:
                            generated_response = \
                                self.generate_response_text(intent=self._current_intent)

        elif self._mode == "ac":
            if not persona:
                if self._current_intent in ["Disclose", "Refine", "Revise"]:
                    movies = [k for k, v in self.user.user().get("preferences")[0].items()
                              if v == 1]
                    movie = movies[random.randint(0, len(movies) - 1)]
                    generated_response = \
                        self.generate_response_text(self._current_intent, {"movie": movie})
                else:
                    generated_response = \
                        self.generate_response_text(intent=self._current_intent)
                    # Avoid generate the same response for Repeat intent
                    while generated_response in self._local:
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
            else:
                if self._current_intent in ["Disclose", "Refine", "Revise"]:
                    movies = [k for k, v in self.user.user().get("preferences")[0].items()
                              if v == 1]
                    movie = movies[random.randint(0, len(movies) - 1)]
                    generated_response = \
                        self.generate_response_text(self._current_intent, {"movie": movie})
                    self._current_movie = movie
                else:
                    print(response["intent"])
                    # Bot provides movie options
                    if len(response["intent"]) > 1 and response["intent"][1] \
                            in INTENT_MOVIE_LIST:
                        _, _, self._current_movie, current_movie_genre = \
                            self.link_entities(text=utterance[1])[0]
                        # user has watched this movie
                        if self._current_movie in self.user.preferences[0]:
                            # when asked if has watched or not,
                            if self._current_intent in ["Back", "Similar"]:
                                self._current_intent = "Similar"
                        else:  # user has not watched it yet
                            # decide if like or dislike a movie based on personal genres
                            if sum([self.user.preferences[1].get(g, 0) for g in
                                    current_movie_genre]) >= 0:
                                # force the intent as like
                                self._current_intent = "Note"
                                # update the movie into persona
                                self.update_persona(self._current_movie, 1.5)
                                print("before", self.agenda)
                                p_random = random.uniform(0, 1)
                                if p_random > 0.5:
                                    # Empty the agenda and force to close the session
                                    self._agenda = ["Complete"]
                                else:
                                    self._agenda = []
                            else:
                                self._current_intent = "Similar"
                                # update the movie into persona
                                self.update_persona(self._current_movie, -1.5)
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
                    else:
                        generated_response = \
                            self.generate_response_text(intent=self._current_intent)
                        # Avoid generate the same response for Repeat intent
                        while generated_response in self._local:
                            generated_response = \
                                self.generate_response_text(intent=self._current_intent)

        else:
            assert "WRONG MODE! Choose from <ms, mb, ac>"

        # Empty the local records for last movie
        if response["intent"][-1] == "Similar":
            self._local = []
        # Keep record of the "Repeat" for the current movie
        if self._current_intent in ["Repeat"]:
            self._local.append(generated_response)
        if not generated_response:
            print(response["intent"], self._current_intent)
        return generated_response, response["intent"]

    def next_action(self, stat):
        """Determines the next action

        Args:
            stat: states

        Returns: next action based on probability disctribution

        """
        if not stat:
            return None
        p_random = random.uniform(0, 1)
        v_sum = sum(stat.values())
        dist = []
        atrr = []
        for k, v_p in stat.items():
            dist.append(v_p / v_sum)
            atrr.append(k)
        return self.samp(p_random, dist, atrr)


    def annotate_bot_intent(self, utterance):
        """Annotate the bot reply by intent.

        If there is no exactly the same sentence, find the one with the best cosine similarity.

        Args:
            utterance: system utterance

        intent_map: {sentence:intent} dictionary built based on history
        tfidf_matrix: tf idf matrix

        Returns: Intent of the most similar sentence

        """
        if utterance in self.intent_map:
            return self.intent_map.get(utterance)
        elif "The movie plot is about" in utterance:
            return "Repeat"
        elif "I didn't understand" in utterance or "Can you reword your statement?" in utterance:
            return "Elicit"
        else:
            out = cosine_similarity(self.tfidf_fit.transform([utterance]),
                                    self.tfidf_matrix.tocsr())
            a_tmp = list(out[0])
            b_tmp = sorted(range(len(a_tmp)), key=lambda i: a_tmp[i], reverse=True)[:1]
            return self.intent_map.get([[inte for inte in sorted(self.intent_map.keys())][i]
                                        for i in b_tmp][0])

def file_process(dialogue_file="1224_ms.json"):
    """Converts the json dialogue records.

    Args:
        file: annotated dialogue corpus.

    Returns: mediate files

    """
    def qrfa_check(item):
        """Checks QRFA intent.

        Args:
            item: item

        Returns: system intent

        """
        if item[0] == USER_TAG:
            label = item[2]
        elif item[0] == AGENT_TAG:
            label = "REQUEST" if item[2] in REQUEST else "ANSWER"
        else:
            label = "MISSING"
        return label

    diags = json.load(open(os.path.join("", dialogue_file)))
    agenda_list = [[i[2] for i in diag if i[0] == USER_TAG]
                   for _, diag in diags.items()]  # [[user agenda list]]
    agenda_stat = {}  # {user_intent: {next_user_intent: occurrence}}
    for agenda in agenda_list:
        for i, item in enumerate(agenda):
            if item not in agenda_stat:
                agenda_stat[item] = {}
            act = agenda[i + 1] if i < len(agenda) - 1 else "Stop"
            if act not in agenda_stat[item]:
                agenda_stat[item][act] = 0
            agenda_stat[item][act] += 1

    agenda_list_qrfa = [[qrfa_check(i) for i in diag]
                        for _, diag in diags.items()]  # [[user agenda list]]
    agenda_stat_qrfa = {}  # {user_intent: {next_user_intent: occurrence}}
    for agenda in agenda_list_qrfa:
        for i, item in enumerate(agenda):
            if item not in agenda_stat_qrfa:
                agenda_stat_qrfa[item] = {}
            act = agenda[i + 1] if i < len(agenda) - 1 else "Stop"
            if act not in agenda_stat_qrfa[item]:
                agenda_stat_qrfa[item][act] = 0
            agenda_stat_qrfa[item][act] += 1

    agent_list_pair = [[diag[i:i + 2] for i in range(len(diag)) if diag[i][0] == AGENT_TAG
                        and len(diag[i:i + 2]) == 2] for _, diag in diags.items()]
    agent_user_intent = {}  # {agent_intent: {user_intent: occurrence}}
    for item in agent_list_pair:
        for pair in item:
            if pair[0][2] not in agent_user_intent:
                agent_user_intent[pair[0][2]] = {}
            if pair[1][2] not in agent_user_intent[pair[0][2]]:
                agent_user_intent[pair[0][2]][pair[1][2]] = 0
            agent_user_intent[pair[0][2]][pair[1][2]] += 1

    agent_list = [[i for i in diag if i[0] == AGENT_TAG] for _, diag in diags.items()]
    intent_map = {}  # {system uttenra: intent annotation}
    for item in agent_list:
        for recom in item:
            intent_map[recom[1]] = recom[2]
    docs = [text for text in sorted(intent_map.keys())]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_fit = tfidf_vectorizer.fit(docs)
    tfidf_matrix = tfidf_fit.transform(docs)
    return agenda_list, agenda_stat, agenda_stat_qrfa, intent_map, \
           agent_user_intent, tfidf_matrix, tfidf_fit


if __name__ == "__main__":
    MSU = MovieSimulatedUser(dialogue_file="data/1224_ms.json",
                             response_tempt=RESPONSE_TEMPLATES_AC, mode="ms")
    MSU.user.print_user()
    AGENDA_LIST, AGENDA_STAT, AGENDA_STAT_QRFA, INTENT_MAP, AGENT_USER_INTENT, \
    TFIDF_MATRIX, TFIDF_FIT = file_process(dialogue_file="data/1224_ms.json")
    MSU.init_agenda_qrfa_test()

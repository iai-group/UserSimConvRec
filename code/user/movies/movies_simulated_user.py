"""
Simple simulated user for the movie domain
==========================================

Author: Shuo Zhang
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from code.user.movies import INTENT_MATCH, USER_TAG, AGENT_TAG, QUERY, FEEDBACK, \
    REQUEST, ANSWER, count1, count, INTENT_MOVIE_LIST
from code.user.simulated_user import SimulatedUser
from code.user.user_generator import UserGenerator
from code.nlp.movies import RESPONSE_TEMPLATES_MS, RESPONSE_TEMPLATES_MB, RESPONSE_TEMPLATES_AC
from code.nlp.movies.movies_nlu import MoviesNLU
from code.nlp.movies.movies_nlg import MoviesNLG
import random
import json
import os


def qrfa_agenda_generate(file):
    scores = {}
    diags = json.load(open(os.path.join("", file)))
    for k, v in diags.items():
        agenda = state_map(v)
        tmp = []
        for i in range(1, len(agenda) - 2):
            tmp.append(count.get(agenda[i]).get(agenda[i + 1]))
        scores[k] = sum(tmp) / len(tmp)
    top_list = [j[0] for j in sorted(scores.items(), key=lambda kv: kv[1], reverse=True) if
                len([n for n in diags[j[0]] if n[0] == USER_TAG]) > 3][:10]
    agenda_list = [[m[2] for m in diags.get(item) if m[0] == USER_TAG] for item in top_list]
    return agenda_list


def state_map(agenda):
    agenda_map = []
    for item in agenda:
        if item[0] == USER_TAG:
            label = "QUERY" if item[2] in QUERY else "FEEDBACK"
        elif item[0] == AGENT_TAG:
            label = "REQUEST" if item[2] in REQUEST else "ANSWER"
        agenda_map.append(label)
    agenda_map = ["START"] + agenda_map + ["STOP"]
    return agenda_map


class MovieSimulatedUser(SimulatedUser, UserGenerator, MoviesNLG, MoviesNLU):
    """Simulated user for movie domain"""

    def __init__(self, file, response_tempt=RESPONSE_TEMPLATES_MS, mode="ms"):
        super(SimulatedUser, self).__init__()
        super(MoviesNLG, self).__init__()
        super(MoviesNLU, self).__init__()
        self._file = file
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
        self.agenda_list, self.agenda_stat, self.agenda_stat_qrfa, self.intent_map, self.agent_user_intent, \
        self.tfidf_matrix, self.tfidf_fit = file_process(file)
        self.metadata, self.titles_all, self.tfidf_fit_nlu, self.tfidf_matrix_nlu = self.naive_index()

    @property
    def agenda(self):
        return self._agenda

    def init_dialog(self):
        """Initiates dialog with the conversational system."""
        self._current_intent = "Non-disclose"
        self._agenda.pop()
        return "Hello"

    def init_a(self, agenda_stat):
        """Initiates agenda stack by sampling push actions."""
        current = "Non-disclose"
        result = []
        result.append(current)
        next = self.next_action(agenda_stat.get(current, {}))
        while next != "Stop":
            current = next
            result.append(current)
            next = self.next_action(agenda_stat.get(current, {}))
        return result

    def init_agenda(self):
        """Initiates agenda stack by sampling push actions."""
        result = self.init_a(agenda_stat=self.agenda_stat)
        while "Disclose" not in result[:5] or len(result) > 12:
            result = self.init_a(agenda_stat=self.agenda_stat)
        self._agenda = result
        self._agenda.reverse()
        print("The agenda is: {}".format(self._agenda))

    def init_agenda_qrfa(self):
        agenda_list = qrfa_agenda_generate(file=self._file)
        self._agenda = agenda_list[random.randint(0, len(agenda_list) - 1)]
        self._agenda.reverse()
        print("The agenda is: {}".format(self._agenda))

    def init_agenda_qrfa_test(self):
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
        """
        Generates response based on the received utterance.

        :param text: reply from chatbot; relayed by conversation manager
        :return:
        """

        # Update the current user intent based on the last utterance.
        utterance = [utterance] if isinstance(utterance, str) else utterance
        response = {"intent": [self.annotate_bot_intent(i) for i in utterance]}
        if len(self._agenda) == 0:
            return "Stop", response["intent"]
        if response["intent"][-1] in INTENT_MATCH.get(self._current_intent):  # Bot replies with right intent
            self._current_intent = self._agenda.pop()
        else:
            self._current_intent = self.next_action(self.agent_user_intent.get(response["intent"][-1]))

        # Generate response based on the case
        if self._mode == "ms":
            if not persona:
                if self._current_intent in ["Disclose", "Expand", "Revise", "Refine"]:
                    genres = [k for k, v in self.user.user().get("preferences")[1].items()]  # Randomly sample a genre
                    genre = genres[random.randint(0, len(genres) - 1)]
                    generated_response = self.generate_response_text(self._current_intent, {"genre": genre})
                else:
                    generated_response = self.generate_response_text(intent=self._current_intent)
                    while generated_response in self._local:  # Avoid generate the same response for Repeat intent
                        generated_response = self.generate_response_text(intent=self._current_intent)
            else:  # Use persona
                if self._current_intent in ["Disclose", "Expand", "Revise", "Refine"]:
                    genres = [k for k, v in self.user.user().get("preferences")[1].items() if
                              v == 1]  # Randomly sampled a favored genre
                    genre = genres[random.randint(0, len(genres) - 1)]
                    # Based on a movie and select a genre.....
                    generated_response = self.generate_response_text(self._current_intent, {"genre": genre})
                    self._current_genre = genre  # Update the current genre that the user disclose
                else:
                    if response["intent"][-1] in INTENT_MOVIE_LIST:  # Bot provides movie options
                        _, _, self._current_movie, current_movie_genre = self.link_entities(text=utterance[-1])[0]
                        if self._current_movie in self.user.preferences[0]:  # user has watched this movie
                            if self._current_intent in ["Note-yes",
                                                        "Note"]:  # when asked if has watched or not, force YES
                                self._current_intent = "Note-yes"
                            elif self._current_intent == "Disclose-review":  # when aske the reviews, assign the preference based on the personal
                                if self.user.preferences[0].get(
                                        self._current_movie) == 1:  # lookup the persona to tell if like or dislike
                                    self._current_intent = "Disclose-review-like"
                                else:
                                    self._current_intent = "Disclose-review-dislike"
                        else:  # user has not watched it yet
                            if self._current_intent in ["Note-dislike", "Note-end",
                                                        "Complete"]:  # user is about to give a final perference
                                if sum([self.user.preferences[1].get(g, 0) for g in
                                        current_movie_genre]) >= 0:  # decide if like or dislike a movie based on personal genres

                                    self._current_intent = "Note-end"  # force the intent as like
                                    self.updat_persona(self._current_movie, 1.5)  # update the movie into persona
                                    self._agenda = []  # Empty the agenda and force to close the session
                                else:
                                    self._current_intent = "Note-dislike"
                                    self.updat_persona(self._current_movie, -1.5)  # update the movie into persona
                        generated_response = self.generate_response_text(intent=self._current_intent)
                    else:
                        generated_response = self.generate_response_text(intent=self._current_intent)
                        while generated_response in self._local:  # Avoid generate the same response for Repeat intent
                            generated_response = self.generate_response_text(intent=self._current_intent)

        elif self._mode == "mb":
            if not persona:
                if self._current_intent in ["Disclose", "Revise"]:
                    movies = [k for k, v in self.user.user().get("preferences")[0].items() if v == 1]
                    movie = movies[random.randint(0, len(movies) - 1)]
                    generated_response = self.generate_response_text(self._current_intent, {"movie": movie})
                else:
                    generated_response = self.generate_response_text(intent=self._current_intent)
                    while generated_response in self._local:  # Avoid generate the same response for Repeat intent
                        generated_response = self.generate_response_text(intent=self._current_intent)
            else:
                if self._current_intent in ["Disclose", "Revise"]:
                    movies = [k for k, v in self.user.user().get("preferences")[0].items() if v == 1]
                    movie = movies[random.randint(0, len(movies) - 1)]
                    generated_response = self.generate_response_text(self._current_intent, {"movie": movie})
                    self._current_movie = movie
                else:
                    if response["intent"][-1] in INTENT_MOVIE_LIST:  # Bot provides movie options
                        _, _, self._current_movie, current_movie_genre = self.link_entities(text=utterance[-1])[0]
                    if response["intent"][-1] in ["Subset", "Show"]:
                        if self._current_intent in ["Note-dislike", "Note",
                                                    "Complete"]:  # user is about to give a final perference
                            if sum([self.user.preferences[1].get(g, 0) for g in
                                    current_movie_genre]) >= 0:  # decide if like or dislike a movie based on personal genres
                                self._current_intent = "Note"  # force the intent as like
                                self.updat_persona(self._current_movie, 1.5)  # update the movie into persona
                                self._agenda = []  # Empty the agenda and force to close the session
                            else:
                                self._current_intent = "Note-dislike"
                                self.updat_persona(self._current_movie, -1.5)  # update the movie into persona
                        generated_response = self.generate_response_text(intent=self._current_intent)
                    else:
                        generated_response = self.generate_response_text(intent=self._current_intent)
                        while generated_response in self._local:  # Avoid generate the same response for Repeat intent
                            generated_response = self.generate_response_text(intent=self._current_intent)


        elif self._mode == "ac":
            if not persona:
                if self._current_intent in ["Disclose", "Refine", "Revise"]:
                    movies = [k for k, v in self.user.user().get("preferences")[0].items() if v == 1]
                    movie = movies[random.randint(0, len(movies) - 1)]
                    generated_response = self.generate_response_text(self._current_intent, {"movie": movie})
                else:
                    generated_response = self.generate_response_text(intent=self._current_intent)
                    while generated_response in self._local:  # Avoid generate the same response for Repeat intent
                        generated_response = self.generate_response_text(intent=self._current_intent)
            else:
                if self._current_intent in ["Disclose", "Refine", "Revise"]:
                    movies = [k for k, v in self.user.user().get("preferences")[0].items() if v == 1]
                    movie = movies[random.randint(0, len(movies) - 1)]
                    generated_response = self.generate_response_text(self._current_intent, {"movie": movie})
                    self._current_movie = movie
                else:
                    print(response["intent"])
                    if len(response["intent"]) > 1 and response["intent"][
                        1] in INTENT_MOVIE_LIST:  # Bot provides movie options
                        _, _, self._current_movie, current_movie_genre = self.link_entities(text=utterance[1])[0]
                        if self._current_movie in self.user.preferences[0]:  # user has watched this movie
                            if self._current_intent in ["Back", "Similar"]:  # when asked if has watched or not,
                                self._current_intent = "Similar"
                        else:  # user has not watched it yet
                            if sum([self.user.preferences[1].get(g, 0) for g in
                                    current_movie_genre]) >= 0:  # decide if like or dislike a movie based on personal genres
                                self._current_intent = "Note"  # force the intent as like
                                self.updat_persona(self._current_movie, 1.5)  # update the movie into persona
                                print("before", self.agenda)
                                p = random.uniform(0, 1)
                                if p > 0.5:
                                    self._agenda = ["Complete"]  # Empty the agenda and force to close the session
                                else:
                                    self._agenda = []
                            else:
                                self._current_intent = "Similar"
                                self.updat_persona(self._current_movie, -1.5)  # update the movie into persona
                        generated_response = self.generate_response_text(intent=self._current_intent)
                    else:
                        generated_response = self.generate_response_text(intent=self._current_intent)
                        while generated_response in self._local:  # Avoid generate the same response for Repeat intent
                            generated_response = self.generate_response_text(intent=self._current_intent)


        else:
            assert "WRONG MODE! Choose from <ms, mb, ac>"

        if response["intent"][-1] == "Similar":  # Empty the local records for last movie
            self._local = []
        if self._current_intent in ["Repeat"]:  # Keep record of the "Repeat" for the current movie
            self._local.append(generated_response)
        if not generated_response:
            print(response["intent"], self._current_intent)
        return generated_response, response["intent"]

    def next_action(self, stat):
        if len(stat) == 0:
            return None
        p = random.uniform(0, 1)
        v_sum = sum(stat.values())
        dist = []
        atrr = []
        for k, v in stat.items():
            dist.append(v / v_sum)
            atrr.append(k)
        return self.samp(p, dist, atrr)


    def annotate_bot_intent(self, utterance):
        """
        Annotate the bot reply by intent: if there is no exactly the same sentence, find the one with the best cosine similarity.

        :param sentence: bot reply
        :param intent_map: {sentence:intent} dictionary built based on history
        :param tfidf_matrix: tf idf matrix
        :return: Intent of the most similar sentence
        """
        if utterance in self.intent_map:
            return self.intent_map.get(utterance)
        elif "The movie plot is about" in utterance:
            return "Repeat"
        elif "I didn't understand" in utterance or "Can you reword your statement?" in utterance:
            return "Elicit"
        else:
            out = cosine_similarity(self.tfidf_fit.transform([utterance]), self.tfidf_matrix.tocsr())
            a = list(out[0])
            b = sorted(range(len(a)), key=lambda i: a[i], reverse=True)[:1]
            return self.intent_map.get([[inte for inte in sorted(self.intent_map.keys())][i] for i in b][0])


def file_process(file="1224_ms.json"):
    """Convert the json dialogue records"""

    def qrfa_check(item):
        if item[0] == USER_TAG:
            label = item[2]
        elif item[0] == AGENT_TAG:
            label = "REQUEST" if item[2] in REQUEST else "ANSWER"
        else:
            label = "shit"
        return label

    diags = json.load(open(os.path.join("", file)))
    agenda_list = [[i[2] for i in diag if i[0] == USER_TAG] for k, diag in diags.items()]  # [[user agenda list]]
    agenda_stat = {}  # {user_intent: {next_user_intent: occurrence}}
    for agenda in agenda_list:
        for i, item in enumerate(agenda):
            if item not in agenda_stat:
                agenda_stat[item] = {}
            act = agenda[i + 1] if i < len(agenda) - 1 else "Stop"
            if act not in agenda_stat[item]:
                agenda_stat[item][act] = 0
            agenda_stat[item][act] += 1

    agenda_list_qrfa = [[qrfa_check(i) for i in diag] for k, diag in diags.items()]  # [[user agenda list]]
    agenda_stat_qrfa = {}  # {user_intent: {next_user_intent: occurrence}}
    for agenda in agenda_list_qrfa:
        for i, item in enumerate(agenda):
            if item not in agenda_stat_qrfa:
                agenda_stat_qrfa[item] = {}
            act = agenda[i + 1] if i < len(agenda) - 1 else "Stop"
            if act not in agenda_stat_qrfa[item]:
                agenda_stat_qrfa[item][act] = 0
            agenda_stat_qrfa[item][act] += 1

    agent_list_pair = [[diag[i:i + 2] for i in range(len(diag)) if diag[i][0] == AGENT_TAG and len(diag[i:i + 2]) == 2]
                       for k, diag in diags.items()]
    agent_user_intent = {}  # {agent_intent: {user_intent: occurrence}}
    for item in agent_list_pair:
        for pair in item:
            if pair[0][2] not in agent_user_intent:
                agent_user_intent[pair[0][2]] = {}
            if pair[1][2] not in agent_user_intent[pair[0][2]]:
                agent_user_intent[pair[0][2]][pair[1][2]] = 0
            agent_user_intent[pair[0][2]][pair[1][2]] += 1

    agent_list = [[i for i in diag if i[0] == AGENT_TAG] for k, diag in diags.items()]
    intent_map = {}  # {system uttenra: intent annotation}
    for item in agent_list:
        for re in item:
            intent_map[re[1]] = re[2]
    docs = [text for text in sorted(intent_map.keys())]
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_fit = tfidf_vectorizer.fit(docs)
    tfidf_matrix = tfidf_fit.transform(docs)
    return agenda_list, agenda_stat, agenda_stat_qrfa, intent_map, agent_user_intent, tfidf_matrix, tfidf_fit


if __name__ == "__main__":
    msu = MovieSimulatedUser(file="data/1224_ms.json", response_tempt=RESPONSE_TEMPLATES_AC, mode="ms")
    msu.user.print_user()
    agenda_list, agenda_stat, agenda_stat_qrfa, intent_map, agent_user_intent, tfidf_matrix, tfidf_fit = file_process(
        file="data/1224_ms.json")
    msu.init_agenda_qrfa_test()

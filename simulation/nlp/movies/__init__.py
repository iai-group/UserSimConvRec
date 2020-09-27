"""
NLP for movies
==============

This nlp package provides classes for entity linking and natural language generation.

Author: Shuo Zhang
"""

import re

AGENT_TAG = "agent"

INTENT_MOVIE_LIST = [
    "Clarify", "List", "Similar"
]

UTTERANCE_PATTERN = {
    "Search results: 1. (.*) 2. (.*) 3. (.*) 4. (.*) 5. (.*)Which options matches your title "
    "search -----g-: 1, 2, 3, 4or 5Type a new one if none matches!":
        "1\. (.*) 2\. (.*) 3\. (.*) 4\. (.*) 5\. (.*)Which options matches",
    "Here are a couple of movies for you! 1. (.*) 2. (.*) 3. (.*)Which film do you have an "
    "interest? Just paste the name": "1\. (.*)2\. (.*)3\. (.*)Which film do you have",
    'There is a movie named "(.*)". Have you watched it?': 'There is a movie named "(.*)". '
                                                           'Have you watched it?',
    'Have you watched "(.*)"? It can be a good recommendation.': 'Have you watched "(.*)"\? '
                                                                 'It can be a good recommendation.',
    'Thank you for your feedback. There is a movie named "(.*)". Have you watched it?':
        'Thank you for your feedback. There is a movie named "(.*)". Have you watched it?',
    'Thank you for reviewing the movie. There is a movie named "(.*)". Have you watched it?':
        'Thank you for reviewing the movie. There is a movie named "(.*)". Have you watched it?',
    'Thank you for reviewing the movie. Have you watched "(.*)"? It can be a good recommendation.':
        'Thank you for reviewing the movie. Have you watched "(.*)"\? '
        'It can be a good recommendation.',
    'Thank you for your feedback. Have you watched "(.*)"? It can be a good recommendation.':
        'Thank you for your feedback. Have you watched "(.*)"\? It can be a good recommendation.',
    "You should try (.*)!": "You should try (.*)!",
    "There's also (.*)!": "There's also (.*)!",
    "Also check out (.*)!": "Also check out (.*)!",
    "I found (.*) for you!": "I found (.*) for you!",
    "I also found (.*)!": "I also found (.*)!",
    "I think you should give (.*) a shot!": "I think you should give (.*) a shot!"
}

REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')

RESPONSE_TEMPLATES = {
    "ask_genre": [
        "What is the genre?",
        "How about the genre of this movie?"
    ],
    "ask_movie_about": [
        "What is this movie about?",
        "What is it about?",
        "Tell me more about it"
    ],
    "preference_actor_like": [
        "I like {actor}",
        "{actor} is one of my favorite movie stars!"
    ],
    "preference_actor_dislike": [
        "I don't want to watch movies with {actor}",
        "I don't like {actor}"
    ],
    "preference_genre_like": [
        "I like {genre} movies",
        "I enjoy {genre} movies",
        "I usually prefer to watch {genre} movies"
    ],
    "preference_movie_seen": [
        "I have seen it already",
        "This I've watched"
    ],
    "book_tickets": [
        "Can you book me tickets for {day} at {time}?",
        "Please book it for me on {day} at {time}"
    ]
}

RESPONSE_TEMPLATES_MS = {
    "Inquire": [
        "Can you book me tickets?",
        "Please book it for me"
    ],
    "Non-disclose": [
        "Hello"
    ],
    "Note-yes": [
        "Yes, I have see it already",
        "This I've watched"
    ],
    "Disclose": [
        "I like {genre} movies",
        "I enjoy {genre} movies",
        "I usually prefer to watch {genre}"
    ],
    "Note": [
        "No",
        "No, tell me more about it",
        "Nope"
    ],
    "Note-dislike": [
        "I do not like it",
        "I dislike this movie",
        "I dont like it"
    ],
    "Note-end": [
        "Seems good, I will watch it.",
        "I will watch it.",
        "It is great!"
    ],
    "Similar": [
        "Could you recommend another movies?",
        "Can you recommend another one?",
        "Another"
    ],
    "Expand": [
        "I also like {genre} movies",
        "I also enjoy {genre} movies",
        "I also prefer to watch {genre}"
    ],
    "Revise": [
        "Sorry, I change my mind. I like {genre} movies",
        "Sorry, I change my mind.. I enjoy {genre} movies",
        "Sorry, I change my mind.. I usually prefer to watch {genre}"
    ],
    "Refine": [
        "Actually, I like {genre} movies",
        "Actually,. I enjoy {genre} movies",
        "Actually,. I usually prefer to watch {genre} movies"
    ],
    "Repeat": [
        "Tell me about its plot!",
        "Give me the storyline!",
        "Who are the actors?",
        "Actors?",
        "Who directed this movie?",
        "Director?",
        "What is the release time",
        "Release year?",
        "How long is it this movie?",
        "Duration?",
        "Rating on IMDB"
    ],
    "List": [
        "Could you recommend some movies?"
    ],
    "Complete": [
        "I really like this movie!",
        "Thanks!",
        "I will watch it. Thanks!",
        "bye",
        "Thank you!"
    ],
    "End": [
        "Bye"
    ],
    "Navigate": [
        "Help"
    ],
    "Disclose-review": [
        "I really like it",
        "Just so so",
        "It is an average movie",
        "I dislike it"
    ],
    "Disclose-review-like": [
        "I really like it",
        "It is an average movie",
    ],
    "Disclose-review-dislike": [
        "Just so so",
        "I dislike it"
    ],
    "Non-disclose-review": [
        "I forgot",
        "I do not remember"
    ],
    "More": [
        "What else?"
    ],
    "Interrupt": [
        "Can we change to another movie?"
    ],
    "...": [
        "Hope you can be clearer in the future..."
    ]
}

RESPONSE_TEMPLATES_MB = {
    "Non-disclose": [
        "Hello",
        "bonjour",
        "ahoy",
        "howdy",
        "u there",
        "good evening",
        "good afternoon,"
        "good morning",
        "are you there",
        "yow",
        "hello there",
        "hola"
    ],
    "Disclose": [
        "{movie}"
    ],
    "Refine": [
        "1"
    ],
    "List": [
        "Recommend similar movies",
        "Give similar movie",
        "Any recommendation",
        "Can you recommend similar movies",
        "what about recommendations?",
        "show me movies similar to",
        "recommend movies that are similar",
        "recommend me movies that are related",
        "movie recommendation"
    ],
    "Similar": [
        "Recommend similar movies",
        "Do you have other movies?",
        "please recommend some movies",
        "Give similar movie",
        "Any recommendation",
        "Can you recommend similar movies",
        "what about recommendations?",
        "show me movies similar to",
        "recommend movies that are similar",
        "recommend me movies that are related",
        "movie recommendation"
    ],
    "Subset": [
        "1"
    ],
    "Repeat": [
        "what type of movie is this?",
        "what kind of genre is the movie",
        "genre",
        "movie genre",
        "what is the movie genre",
        "what is the rating for the movie?",
        "what about the movie rating",
        "how much rating did the movie receive?",
        "what is the recommendation rating?",
        "would anybody recommend watching this movie?",
        "is this movie good or bad?",
        "rating",
        "what is the average votes for the movie?",
        "people who recommended this movie",
        "how many people voted for this movie?",
        "vote count",
        "how many people recommended this movie?",
        "how much votes did the movie receive?",
        "can i watch this movie with kids?",
        "is this movie adult rated?",
        "Can kids watch this movie?",
        "type of content",
        "kids content",
        "adult content",
        "describe this movie to me",
        "movie details",
        "tell me more about this movie",
        "movie overview",
        "what is the movie about?",
        "movie revenue",
        "how much did the movie make?",
        "movie budget",
        "budget of the movie",
        "cost to make the movie",
        "budget",
        "movie cost",
        "Internet Movie Database link",
        "show me the movie link",
        "imdb link",
        "take me to the movie url",
        "url",
        "imdb",
        "movie database link",
        "tmdb",
        "show me the tmdb url?"
    ],
    "Note-dislike": [
        "I do not like it",
        "I do not like the recommendations",
        "I dislike it. I want other",
        "I do not like this movie"
    ],
    "Revise": [
        "{movie}"
    ],
    "Inquire": [
        "How to download this movie",
        "I also like mystery movies",
        "I like both genres",
        "Can you get it for me",
        "Is there a horror movie?",
        "Is it fantacy movie?"
    ],
    "Complete": [
        "catch you soon",
        "Bye",
        "Ciao",
        "Goodbye",
        "See you later",
        "Talk to you later"
    ],
    "Note": [
        "I like it",
        "I'll want one",
        "I like movies like this",
        "I like these movies",
        "All right, I'll want",
        "Ok",
        "Oh, it is not bad. I will watch it",
        "ok, just it",
        "ok, I can have a try",
        "ok, thanks",
        "I am interested",
        "Ok, i like this film",
    ]
}

RESPONSE_TEMPLATES_AC = {
    "Note-speechless": [
        "wow"
    ],
    "Non-disclose": [
        "GO",
        "Hi",
        "go",
        "Hello dude",
        "Go",
        "Hi Andchill",
        "Get Started"
    ],
    "Complete": [
        "Cool",
        "Sure",
        "ok got it. I will do that",
        "good",
        "yes. thanks for your recommendation",
        "bye",
        "thanks dude. Bye",
        "thanks a lot. bye for now",
        "Thank you",
        "Thanks",
        "I love this one, thank you",
    ],
    "Compare": [
        "which one do you suggest should I watch first",
        "which one do you think is better?"
    ],
    "Inquire": [
        "can you recommend me more movies",
        "I need a movie recommendation",
        "You can remind me of my picks at 6pm",
        "I don't remember any. can you please give me a suggestion of any interesting movie?",
        "ok. In that case can you suggest me a movie that many people have searched for",
        "i want from 2018 or 2019 movie",
        "wow. that sounds interesting. I can't wait to watch it. can you please remind me "
        "tonight about the movie?"
    ],
    "Expand": [
        "I like the movie because it has romantic and raw at the same time",
        "because it is an action movie.",
        "the story plot",
        "Because it is hilarious",
        "it's new and entertaining",
        "it is sci-fi and creative",
        "I like its genre",
        "I like the actors",
        "i like the director"
    ],
    "Note": [
        "Friday Evening",
        "I like this",
        "Let's go with the first movie",
        "Remind me this Friday evening about the second movie.",
        "The first one seems to be a good choice.",
        "Sunday Afternoon",
        "I think the second one would be the best one for tonight",
        "Saturday Afternoon",
        "I liked your recommendation",
        "I like the firsr recommendatation. I'm going to try this one.",
        "ok. i actually find one of your recommendations interesting",
        "I really liked the recommendation, it has all the features I look for.",
        "No Reminder Needed!",
        "ok"
    ],
    "Disclose": [
        "I loved {movie}",
        "I like {movie}, with the famous actor",
        "{movie} because it is interesting",
        "Okay. In that case can you search for any Drama movie",
        "Ok. then suggest me any movie similar to {movie}",
        "{movie} gave me an idea that it has some mystery kind of thing going on in the movie",
        "{movie}. I love the movie because it is one of the best classics",
        "I want a good documentary about heavy metal",
        "{movie}. I loved its ending!",
        "Ok. then can you look for a fantasy movie?",
        "{movie} because of the storyline",
        "{movie}",
        "{movie}",
        "{movie}",
        "I don't remember any. can you please give me a suggestion of any interesting movie?"
    ],
    "Repeat": [
        "can you please search for the ratings for this movie?",
        "Which genre does it belongs to?",
        "Is it a Classical one?",
        "is that movie Adult rated?",
        "is the last one a comedy movie?"
    ],
    "Refine": [
        "Well, I loved {movie}",
        "Well, I like {movie}, with the famous actor",
        "{movie} because it is interesting",
        "Okay. In that case can you search for any Drama movie",
        "Ok. then suggest me any movie similar to {movie}",
        "{movie} gave me an idea that it has some mystery kind of thing going on in the movie",
        "{movie}. I love the movie because it is one of the best classics",
        "I want a good documentary about heavy metal",
        "{movie}. I loved its ending!",
        "Ok. then can you look for a fantasy movie?",
        "{movie because of the storyline}",
        "{movie}",
        "{movie}",
        "Well, {movie} "
    ],
    "Non-disclose-complain": [
        "are you smart, film not?"
    ],
    "Interrogate": [
        "What is the best ever movie you suggest"
    ],
    "Back": [
        "I dont like this one",
        "I have watched them"
    ],
    "Complete-complain": [
        "I hope you will improve very sooner. thanks for your help. Bye",
        "I'm sad that you don't recognize something that you suggested already"
    ],
    "Interrupt": [
        "No Reminder Needed!"
    ],
    "Disclose-repeat": [
        "{movie}. because its a classical  one"
    ],
    "Similar": [
        "show me more related movie please",
        "I saw the two mentioned movies. Can you recommend me another one?",
        "I don't like any of those suggestions. can you search for more related movies please?",
        "ah.. not the same ones again",
        "I've already seen all of them. can you please enlarge your list",
        "Can you suggest anything else?",
        "Watched it already",
        "search for another movie"
    ],
    "Revise": [
        "I loved {movie}",
        "I like {movie}, with the famous actor",
        "{movie} because it is interesting",
        "Okay. In that case can you search for any Drama movie",
        "Ok. then suggest me any movie similar to {movie}",
        "{movie} gave me an idea that it has some mystery kind of thing going on in the movie",
        "{movie}. I love the movie because it is one of the best classics",
        "I want a good documentary about heavy metal",
        "{movie}. I loved its ending!",
        "Ok. then can you look for a fantasy movie?",
        "{movie} because of the storyline",
        "{movie}",
        "{movie}",
        "{movie}"
    ],
    "More": [
        "tickets for this?"
    ],
    "List": [
        "show me more related movie please"
    ]
}

USER_TAG = "user"
AGENT_TAG = "agent"

INTENT_MATCH = {
    "Non-disclose": ["Elicit", "Inquire"],
    "Non-disclose-review": ["Elicit", "Inquire"],
    "Non-disclose-complain": ["Elicit", "Inquire"],
    "Disclose": ["Elicit", "Show", "List", "Show", "Suggest", "Clarify"],
    "Disclose-review": ["Elicit", "List", "Show", "Suggest", "Clarify"],
    "Disclose-repeat": ["Elicit", "List", "Show", "Suggest", "Clarify"],
    "Revise": ["Elicit", "Show", "List", "Suggest", "Clarify"],
    "Refine": ["Elicit", "Show", "List", "Suggest", "Clarify"],
    "Expand": ["Elicit", "Show", "List", "Suggest", "Clarify"],
    "Note": ["Record", "Repeat"],
    "Note-end": ["Record", "Repeat"],
    "Note-speechless": ["Record"],
    "Interrupt": ["Suggest", "Elicit", "Back"],
    "Complete": ["End"],
    "Compare": [],
    "Complete-complain": ["End"],
    "Back": ["List"],
    "Interrogate": ["Explain"],
    "Inquire": ["List", "Elicit"],
    "Repeat": ["Repeat"],
    "More": ["List", "More"],
    "Similar": ["Elicit", "Similar", "List"],
    "List": ["List"],
    "Subset": ["Subset"],
    "Navigate": ["Show"],
    "Note-yes": ["Elicit-review"],
    "Note-dislike": ["List", "Elicit"],
    "Note-complain": ["Elicit"],
    "...": []
}

QUERY = [
    "Disclose", "Disclose-repeat", "Disclose-repeat", "Disclose-review", "Non-disclose", "Non-disclose-complain",
    "Revise", "Refine", "Expand",
    "List", "Compare", "Similar", "Repeat", "Inquire", "Navigate"
]

FEEDBACK = [
    "Non-disclose-complain", "Note-yes", "Note-dislike", "Note-complain", "Note-speechless", "Non-disclose-review",
    "Subset", "Interrupt", "Interrogate", "Back", "More", "Note", "Note-end", "Complete", "Complete-complain", '...'
]

REQUEST = [
    "Elicit", "Elicit-review", "Inquire", "Suggest", "Clarify"
]

ANSWER = [
    "Show", "List", "Similar", "Record", "Repeat", "Back", "End", "More", "Subset"
]

count1 = {'...': {'ANSWER': 1},
          'ANSWER': {'...': 1,
                     'ANSWER': 99,
                     'Back': 4,
                     'Complete': 59,
                     'Complete-complain': 1,
                     'Disclose': 22,
                     'Expand': 2,
                     'Inquire': 17,
                     'Interrogate': 1,
                     'Interrupt': 3,
                     'List': 33,
                     'More': 2,
                     'Navigate': 4,
                     'Non-disclose': 20,
                     'Note': 91,
                     'Note-complain': 1,
                     'Note-dislike': 28,
                     'Note-end': 36,
                     'Note-speechless': 1,
                     'Note-yes': 28,
                     'REQUEST': 46,
                     'Refine': 3,
                     'Repeat': 230,
                     'Revise': 37,
                     'Similar': 50,
                     'Subset': 33},
          'Back': {'ANSWER': 3, 'REQUEST': 3},
          'Compare': {'REQUEST': 1},
          'Complete': {'ANSWER': 18, 'Complete': 1, 'REQUEST': 2, "stop": 10},
          "stop": {"stop": 1},
          'Complete-complain': {'ANSWER': 1},
          'Disclose': {'ANSWER': 60, 'REQUEST': 50},
          'Disclose-repeat': {'ANSWER': 1},
          'Disclose-review': {'ANSWER': 26},
          'Expand': {'ANSWER': 9, 'REQUEST': 3},
          'Inquire': {'ANSWER': 18, 'REQUEST': 13},
          'Interrogate': {'ANSWER': 1},
          'Interrupt': {'ANSWER': 4, 'REQUEST': 7},
          'List': {'ANSWER': 34},
          'More': {'ANSWER': 2},
          'Navigate': {'ANSWER': 4},
          'Non-disclose': {'ANSWER': 13, 'REQUEST': 35},
          'Non-disclose-complain': {'REQUEST': 1},
          'Non-disclose-review': {'ANSWER': 1},
          'Note': {'ANSWER': 94, 'Complete': 1, 'Note': 1, 'REQUEST': 8},
          'Note-complain': {'ANSWER': 1},
          'Note-dislike': {'ANSWER': 22, 'REQUEST': 7},
          'Note-end': {'ANSWER': 35},
          'Note-speechless': {'ANSWER': 1},
          'Note-yes': {'ANSWER': 2, 'REQUEST': 26},
          'REQUEST': {'ANSWER': 2,
                      'Back': 2,
                      'Compare': 1,
                      'Complete': 4,
                      'Complete-complain': 1,
                      'Disclose': 88,
                      'Disclose-repeat': 1,
                      'Disclose-review': 26,
                      'Expand': 10,
                      'Inquire': 14,
                      'Interrupt': 11,
                      'List': 1,
                      'Navigate': 1,
                      'Non-disclose': 28,
                      'Non-disclose-complain': 1,
                      'Non-disclose-review': 1,
                      'Note': 28,
                      'Note-dislike': 1,
                      'REQUEST': 5,
                      'Refine': 49,
                      'Repeat': 8,
                      'Revise': 36,
                      'Similar': 9,
                      'Subset': 1},
          'Refine': {'ANSWER': 47, 'REQUEST': 5},
          'Repeat': {'ANSWER': 228, 'REQUEST': 8},
          'Revise': {'ANSWER': 38, 'REQUEST': 33},
          'Similar': {'ANSWER': 54, 'REQUEST': 5},
          'Subset': {'ANSWER': 32, 'REQUEST': 1}}

count = {'ANSWER': {'ANSWER': 103, 'FEEDBACK': 289, 'QUERY': 418, 'REQUEST': 45},
         'FEEDBACK': {'ANSWER': 283, 'FEEDBACK': 3, 'REQUEST': 55},
         'QUERY': {'ANSWER': 539, 'REQUEST': 227},
         'REQUEST': {'ANSWER': 2, 'FEEDBACK': 49, 'QUERY': 274, 'REQUEST': 5}}

INTENT_MOVIE_LIST = ["Clarify", "List", "Similar"]  # intents of utterances that likely have movies.

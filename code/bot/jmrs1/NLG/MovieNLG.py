"""
Copyright (c) 2019 Uber Technologies, Inc.

Licensed under the Uber Non-Commercial License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at the root directory of this project. 

See the License for the specific language governing permissions and
limitations under the License.
"""

__author__ = "Alexandros Papangelis"


import random

"""
MoviesNLG is an NLG similar to Dummy NLG but for movies domain.
It's a simple template-based NLG, designed to work for Slot-Filling 
applications. The purpose of this class is to provide a quick way of running 
Conversational Agents, sanity checks, and to aid debugging.
"""


class MovieNLG():
    def __init__(self, args=None):
        """
        Nothing to initialize. We need the args to support use by the Generic
        Agent.
        """
        super(MovieNLG, self).__init__()

    def initialize(self, args):
        """
        Nothing to do here

        :param args:
        :return:
        """
        pass

    def generate_output(self, args=None):
        """
        Select the appropriate template given the acts in the arguments and
        generate the output utterance.

        :param args: a dictionary of arguments that contain the dialogue acts
        :return: the output utterance
        """
        if not args:
            print('WARNING! MovieNLG called without arguments!')
            return ''

        if 'args' in args:
            dacts = args['args']

        elif 'dacts' not in args:
            print('WARNING! MovieNLG called without dacts!')
            return ''

        else:
            dacts = args['dacts']
        system = True

        help = ['Hi there. I am JARVIS, your movie recommending buddy. I can recommend you movies based on the GENRE you preffer.\n\
And if you like the movie, you can ask me about its plot, actors, directors and release year e.t.c.',
                'Hi. My name is JARVIS and I can recommend you movies for the GENRE you preffer.\n\
If you like the movie, you can ask me about its plot, actors, directors and release year e.t.c.']
        welcomemsg = ['How can I help you?',
                      'Shall we start?',
                      'How may I assist you?']
        response = []
        ack_feedback = ''
        choice = random.choice([1,2])
        for dact in dacts:
            if dact.intent == 'ack_feedback':
                ack_feedback = random.choice(['Thank you for your feedback. ', 'Thank you for reviewing the movie. '])

            elif dact.intent == 'feedback':
                response.append('What do you think about this Movie?' if choice == 1
                                else 'Can you give a review on this movie?')

            elif dact.intent == 'request':
                if dact.params and dact.params[0].slot:
                    if system:
                        response.append(random.choice(['Which ' + \
                                    dact.params[0].slot + \
                                    ' do you prefer?',
                                    'Do you have any ' + \
                                    dact.params[0].slot + \
                                    ' in mind?',
                                    'Guide me. Any ' + \
                                    dact.params[0].slot + \
                                    ' you like?']))
                else:
                    response.append('Which movie do you want?')

            elif dact.intent == 'offer':
                for dact_item in dact.params:
                    if dact_item.slot == 'name' and dact_item.value:
                        response.append('There is a movie named "{}". Have you watched it?'.format(dact_item.value)  if choice==1 
                                                else 'Have you watched "{}"? It can be a good recommendation.'.format(dact_item.value))
                        return ack_feedback + " ".join(response)

            elif dact.intent in ['inform', 'offer']:
                for dact_item in dact.params:
                    if system:
                        if dact_item.slot == 'name' and \
                                dact_item.value == 'not found':
                            response = ['Sorry, I cannot find such an item. ']

                        elif dact_item.slot == 'name' and dact_item.value:
                                response.append('I would recommend movie "{}"'.format(dact_item.value)  if choice==1 
                                                else '"{}" can be a good recomendation '.format(dact_item.value))
                                    

                        else:
                            if not dact_item.value:
                                response.append('its ' + \
                                            dact_item.slot + \
                                            ' is unknown, ')

                            elif dact_item.slot == 'name' and \
                                    len(dact.params) > 1:
                                response.append(dact_item.value + '  ')

                            elif dact_item.slot == 'genres':
                                response.append('The genres it belongs to are {}'.format(dact_item.value.lower()) if choice == 1
                                                else 'Its genres are {}'.format(dact_item.value.lower()))
                                    
                            elif dact_item.slot == 'director_name':
                                response.append('The director of this movie is {}'.format(dact_item.value) if choice == 1
                                                else 'It was directed by {}'.format(dact_item.value))

                            elif dact_item.slot == 'imdb_score':
                                response.append('Its rating on IMDB is {}'.format(dact_item.value) if choice == 1
                                                else 'The movie rates {} on IMDB'.format(dact_item.value))

                            elif dact_item.slot == 'plot_keywords':
                                response.append(random.choice(['The plot of the movie revolves around ' + dact_item.value, 
                                                          'The movie plot is about ' + dact_item.value + ' ']))

                            elif dact_item.slot == 'title_year':
                                response.append(random.choice(['The movie was released in ' + dact_item.value, 
                                                          'It was released in year ' + dact_item.value + ' ']))

                            elif dact_item.slot == 'actors':
                                response.append(random.choice(['Some of the famous actors in this movie are ' + dact_item.value, 
                                                          '{} have played prominent roles in this movie'.format(dact_item.value)]))

                            elif dact_item.slot == 'duration':
                                value = int(dact_item.value)
                                hours = str(int(value/60))
                                minutes = str(value - int(value/60)*60)
                                response.append(random.choice(['It\'s duration is ' + dact_item.value + ' minutes', 
                                                          "It is {} hours and {} minutes long".format(hours, minutes)]))

                            else:
                                response.append('its ' + \
                                            dact_item.slot + \
                                            ' is ' + dact_item.value + ' ')

                    else:
                        if dact.intent == 'offer':
                            if dact_item.value:
                                response.append(dact_item.slot + ' is ' + \
                                            dact_item.value + ', ')
                            else:
                                response.append(dact_item.slot + ' is unknown, ')
                        else:
                            r = random.random()

                            if r < 0.33:
                                response.append('I prefer ' + dact_item.value + \
                                            ' ' + dact_item.slot + ', ')

                            elif r < 0.66:
                                response.append('um i want ' + dact_item.value + \
                                            ' ' + dact_item.slot + ', ')

                            else:
                                response.append(dact_item.value + ' ' + \
                                            dact_item.slot + ' please, ')


            elif dact.intent == 'bye':
                response.append(random.choice(['Thank you, Goodbye', 'Bye. Hope you liked it']))

            elif dact.intent == 'deny':
                response.append('No')

            elif dact.intent == 'negate':
                response.append('No ')

                if dact.params and dact.params[0].slot and \
                        dact.params[0].value:
                    response.append(dact.params[0].slot + \
                                ' is not ' + dact.params[0].value)

            elif dact.intent == 'ack':
                response.append('Ok')

            elif dact.intent == 'affirm':
                response.append('Yes ')

                if dact.params and dact.params[0].slot and \
                        dact.params[0].value:
                    response.append(dact.params[0].slot + \
                                ' is ' + dact.params[0].value)

            
            elif dact.intent == 'canthelp':
                response.append('Sorry, I cannot help you with that.' if choice == 1 else 'Sorry, I don\'t understand what you mean.')
                
            elif dact.intent == 'welcomemsg':
                response.append(random.choice(help) + '\n\nYou can type \'help\' anytime to get assistance.\n\n' + random.choice(welcomemsg))

            elif dact.intent == 'help':
                response.append(random.choice(help))
                #'Hello, how may I help you?'
            elif dact.intent == 'moreinfo':
                param = dact.params[0]
                if param.value and '|' in param.value:
                    more_info = 'The available ' + param.slot + ' are ' if choice == 1 else 'You can choose the ' + param.slot + ' from '
                    more_info += "'" + param.value.strip() + "'"
                    response.append(more_info)
                elif " " in param.slot:
                    requestables = param.slot.split(" ")
                    more_info = "I can tell you more about "
                    requestables = [("the name of the 'director'" if choice == 1 else "the 'director' name") if x == 'director_name' else x for x in requestables]
                    requestables = [("actors" if choice == 1 else "list of top 'actors'") if x == "'actors'" else x for x in requestables]
                    requestables = [("IMDB 'rating'" if choice == 1 else "'rating' on IMDB") if x == 'imdb_score' else x for x in requestables]
                    requestables = [("the 'plot'" if choice == 1 else "the 'storyline'") if x == 'plot_keywords' else x for x in requestables]
                    requestables = [("the release 'year'" if choice == 1 else "the 'year' of release") if x == 'title_year' else x for x in requestables]
                    requestables = [("the movie 'duration'" if choice == 1 else "the 'duration' of the movie") if x == 'duration' else x for x in requestables]
                    response.append(more_info + ", ".join(requestables[:-1]) + " and " + requestables[-1] + '.')
            else:
                response.append('MovieNLG %s' % dact)

            #response += ' '
        
        if response:
            response = [x.strip() for x in response]
            if len(response) > 1:
                response = ', '.join(response[:-1]) + ' ' + response[-1]
            else:
                response = response[0]
            # Trim trailing comma and space
            if response.endswith(","):
                response = response[:-1].strip()
            if not response.endswith('.') and not response.endswith('?'): response = response + '.'
            response = response.replace('  ', ' ')
            response = response.replace(' ,',',')

        try:
            r = list(response)
            r[0] = r[0].upper()
            response = ''.join(r)
        except:
            response = ""
        return ack_feedback + response

    def train(self, data):
        """
        Nothing to do here.

        :param data:
        :return:
        """
        pass

    def save(self, path=None):
        """
        Nothing to do here.

        :param path:
        :return:
        """
        pass

    def load(self, path):
        """
        Nothing to do here.

        :param path:
        :return:
        """
        pass

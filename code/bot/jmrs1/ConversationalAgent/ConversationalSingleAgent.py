"""
Copyright (c) 2019 Uber Technologies, Inc.

Licensed under the Uber Non-Commercial License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at the root directory of this project. 

See the License for the specific language governing permissions and
limitations under the License.
"""

__author__ = "Alexandros Papangelis"

from code.bot.jmrs1.DialogueManagement import DialogueManager
from code.bot.jmrs1.Utilities.DialogueEpisodeRecorder import DialogueEpisodeRecorder
from code.bot.jmrs1.Utilities.DialogueEpisodeRecorder import DialogueConversationRecorder
from code.bot.jmrs1.Domain import Ontology, DataBase
from code.bot.jmrs1.NLU.MovieNLU import MovieNLU
from code.bot.jmrs1.NLG.MovieNLG import MovieNLG
from code.bot.jmrs1.Dialogue.Action import DialogueAct
from code.telegram.balog_bot import *

from copy import deepcopy

import os
import random

"""
The ConversationalSingleAgent implements the standard architecture of a 
dialogue system, with some flexibility in the input and output (either 
can be Dialogue Acts, Text, or Speech). Each component's parameters must 
be in the config, otherwise this agent will either raise an error or use 
default values.
"""


class ConversationalSingleAgent():
    """
    Essentially the dialogue system. Will be able to interact with:

    - Human Users via:
        - Text

    - Data
    """

    def __init__(self, configuration):
        """
        Initialize the internal structures of this agent.

        :param configuration: a dictionary representing the configuration file
        :param agent_id: an integer, this agent's id
        """

        super(ConversationalSingleAgent, self).__init__()

        self._bb = BalogBot()
        self.history = []

        self.configuration = configuration

        # There is only one agent in this setting
        self.agent_id = 0

        # Dialogue statistics
        self.dialogue_episode = 0
        self.dialogue_turn = 0
        
        # True values here would imply some default modules
        self.USE_NLG = False
        self.SAVE_LOG = False
        self.SAVE_LOG_conv = False
        self.NLP_conv = True

        # The dialogue will terminate after MAX_TURNS (this agent will issue
        # a bye() dialogue act.
        self.MAX_TURNS = 100

        self.dialogue_turn = -1
        self.ontology = None
        self.database = None
        self.domain = None
        self.dialogue_manager = None
        self.nlu = None
        self.nlg = None

        self.curr_state = None
        self.prev_state = None
        self.curr_state = None
        self.prev_usr_utterance = None
        self.prev_sys_utterance = None
        self.prev_action = None
        self.prev_reward = None
        self.prev_success = None
        self.prev_task_success = None

        self.recorder = DialogueEpisodeRecorder()
        self.convrecorder = DialogueConversationRecorder()


        if self.configuration:
            # Dialogue domain self.settings
            if 'DIALOGUE' in self.configuration and \
                    self.configuration['DIALOGUE']:
                
                if self.configuration['DIALOGUE']['domain']:
                    self.domain = self.configuration['DIALOGUE']['domain']

                if self.configuration['DIALOGUE']['ontology_path']:
                    if os.path.isfile(
                            self.configuration['DIALOGUE']['ontology_path']
                    ):
                        self.ontology = Ontology.Ontology(
                            self.configuration['DIALOGUE']['ontology_path']
                        )
                    else:
                        raise FileNotFoundError(
                            'Domain file %s not found' %
                            self.configuration['DIALOGUE']['ontology_path'])

                if self.configuration['DIALOGUE']['db_path']:
                    if os.path.isfile(
                            self.configuration['DIALOGUE']['db_path']
                    ):
                        if 'db_type' in self.configuration['DIALOGUE']:
                            if self.configuration['DIALOGUE']['db_type'] == \
                                    'sql':
                                self.database = DataBase.SQLDataBase(
                                    self.configuration['DIALOGUE']['db_path']
                                )
                            else:
                                self.database = DataBase.DataBase(
                                    self.configuration['DIALOGUE']['db_path']
                                )
                        else:
                            # Default to SQL
                            self.database = DataBase.SQLDataBase(
                                self.configuration['DIALOGUE']['db_path']
                            )
                    else:
                        raise FileNotFoundError(
                            'Database file %s not found' %
                            self.configuration['DIALOGUE']['db_path']
                        )

            # General settings
            if 'GENERAL' in self.configuration and \
                    self.configuration['GENERAL']:
                if 'experience_logs' in self.configuration['GENERAL']:
                    dialogues_path = None
                    if 'path' in \
                            self.configuration['GENERAL']['experience_logs']:
                        dialogues_path = \
                            self.configuration['GENERAL'][
                                'experience_logs']['path']

                    if 'load' in \
                            self.configuration['GENERAL']['experience_logs'] \
                        and bool(
                            self.configuration['GENERAL'][
                                'experience_logs']['load']
                    ):
                        if dialogues_path and os.path.isfile(dialogues_path):
                            self.recorder.load(dialogues_path)
                        else:
                            raise FileNotFoundError(
                                'Dialogue Log file %s not found (did you '
                                'provide one?)' % dialogues_path)

                    if 'save' in \
                            self.configuration['GENERAL']['experience_logs']:
                        self.recorder.set_path(dialogues_path)
                        self.SAVE_LOG = bool(
                            self.configuration['GENERAL'][
                                'experience_logs']['save']
                        )
                if 'conversation_logs' in self.configuration['GENERAL']:
                    conv_dialogues_path = None
                    if 'path' in \
                            self.configuration['GENERAL']['conversation_logs']:
                        conv_dialogues_path = \
                            self.configuration['GENERAL'][
                                'conversation_logs']['path']

                    if 'load' in \
                            self.configuration['GENERAL']['conversation_logs'] \
                        and bool(
                            self.configuration['GENERAL'][
                                'conversation_logs']['load']
                    ):
                        if conv_dialogues_path and os.path.isfile(conv_dialogues_path):
                            self.convrecorder.load(conv_dialogues_path)
                        else:
                            raise FileNotFoundError(
                                'Dialogue Log file %s not found (did you '
                                'provide one?)' % conv_dialogues_path)

                    if 'save' in \
                            self.configuration['GENERAL']['conversation_logs']:
                        self.convrecorder.set_path(conv_dialogues_path)
                        self.SAVE_LOG_conv = bool(
                            self.configuration['GENERAL'][
                                'conversation_logs']['save']
                        )

                    if 'nlp' in \
                            self.configuration['GENERAL']['conversation_logs']:
                        self.NLP_conv = bool(
                            self.configuration['GENERAL'][
                                'conversation_logs']['nlp']
                        )

            
            # NLU Settings
            if 'NLU' in self.configuration['AGENT_0'] and \
                    self.configuration['AGENT_0']['NLU'] and \
                    self.configuration['AGENT_0']['NLU']['nlu']:
                nlu_args = dict(
                    zip(['ontology', 'database'],
                        [self.ontology, self.database]
                        )
                )

                self.nlu = MovieNLU(nlu_args)

            # NLG Settings
            if 'NLG' in self.configuration['AGENT_0'] and \
                    self.configuration['AGENT_0']['NLG'] and \
                    self.configuration['AGENT_0']['NLG']['nlg']:
                self.nlg = MovieNLG()

                if self.nlg:
                    self.USE_NLG = True

        dm_args = dict(
            zip(
                ['settings', 'ontology', 'database', 'domain', 'agent_id',
                 'agent_role'],
                [self.configuration,
                 self.ontology,
                 self.database,
                 self.domain,
                 self.agent_id,
                 'system'
                 ]
            )
        )
        dm_args.update(self.configuration['AGENT_0']['DM'])
        self.dialogue_manager = DialogueManager.DialogueManager(dm_args)

    def __del__(self):
        """
        Do some house-keeping and save the models.

        :return: nothing
        """

        # if self.recorder and self.SAVE_LOG:
        #     self.recorder.save()
        #
        # if self.convrecorder and self.SAVE_LOG_conv:
        #     self.convrecorder.save()
        #
        # if self.dialogue_manager:
        #     self.dialogue_manager.save()

        self.curr_state = None
        self.prev_state = None
        self.curr_state = None
        self.prev_usr_utterance = None
        self.prev_sys_utterance = None
        self.prev_action = None
        self.prev_reward = None
        self.prev_success = None
        self.prev_task_success = None

    def initialize(self):
        """
        Initializes the conversational agent based on settings in the
        configuration file.

        :return: Nothing
        """

        self.dialogue_episode = 0
        self.dialogue_turn = 0
        self.num_successful_dialogues = 0
        self.num_task_success = 0
        self.cumulative_rewards = 0

        if self.nlu:
            self.nlu.initialize({})

        self.dialogue_manager.initialize({})

        if self.nlg:
            self.nlg.initialize({})

        self.curr_state = None
        self.prev_state = None
        self.curr_state = None
        self.prev_usr_utterance = None
        self.prev_sys_utterance = None
        self.prev_action = None
        self.prev_reward = None
        self.prev_success = None
        self.prev_task_success = None

    def start_dialogue(self, args=None):
        """
        Perform initial dialogue turn.

        :param args: optional args
        :return:
        """

        self.dialogue_turn = 0
        sys_utterance = ''

        self.dialogue_manager.restart({})

        sys_response = [DialogueAct('welcomemsg', [])]

        if self.NLP_conv:
            self.convrecorder.record(dialogue = 'SYSTEM (NLG)> ' + '; '.join([str(sr) for sr in sys_response]))
            sys_utterance = '; '.join([str(sr) for sr in sys_response])
        if self.USE_NLG:
            sys_utterance = self.nlg.generate_output(
                {'dacts': sys_response}
            )
            # print('SYSTEM: %s ' % sys_utterance)
            self.convrecorder.record(dialogue = 'SYSTEM > ' + sys_utterance)



        else:
            pass
            # print(
            #     'SYSTEM: %s ' % '; '.
            #     join([str(sr) for sr in sys_response])
            # )

        self.recorder.record(
            deepcopy(self.dialogue_manager.get_state()),
            self.dialogue_manager.get_state(),
            sys_response,
            output_utterance=sys_utterance
        )

        self.dialogue_turn += 1

        self.prev_state = None

        # Re-initialize these for good measure
        self.curr_state = None
        self.prev_usr_utterance = None
        self.prev_sys_utterance = None
        self.prev_action = None
        self.prev_reward = None
        self.prev_success = None
        self.prev_task_success = None

        #shuo:
        return sys_utterance
        # self.continue_dialogue()

    def continue_dialogue(self, usr_utterance):
        """
        Perform next dialogue turn.

        :return: nothing
        """
        # usr_utterance = ''
        sys_utterance = ''

        # usr_utterance = input('USER: ')
        self.convrecorder.record(dialogue = 'USER > ' + usr_utterance)

        # Process the user's utterance
        if self.nlu:
            usr_input = self.nlu.process_input(
                usr_utterance,
                self.dialogue_manager.get_state(),
                self.dialogue_manager.get_context()
            ) 
        else:
            raise EnvironmentError(
                'ConversationalAgent: No NLU defined for '
                'text-based interaction!'
            )

        if self.NLP_conv:
            self.convrecorder.record(dialogue = 'SYSTEM (NLU)> ' + '; '.join([str(ui) for ui in usr_input]))
        #print('SYSTEM (NLU)> ' + '; '.join([str(ui) for ui in usr_input]))

        dacts = self.dialogue_manager.receive_input(usr_input)
        # for dact in dacts:
        #     if dact.intent == 'bye':
        #         sys_utterance = "Thanks for your time!"

        # Keep track of prev_state, for the DialogueEpisodeRecorder
        # Store here because this is the state that the dialogue manager
        # will use to make a decision.
        self.curr_state = deepcopy(self.dialogue_manager.get_state())

        #print('\nDEBUG> '+str(self.dialogue_manager.get_context()))
        #print('\nDEBUG> '+str(self.dialogue_manager.get_state()) + '\n')

        if self.dialogue_turn < self.MAX_TURNS:
            sys_response = self.dialogue_manager.generate_output()

        else:
            # Force dialogue stop
            # print(
            #     '{0}: terminating dialogue due to too '
            #     'many turns'.format(self.agent_role)
            # )
            sys_response = [DialogueAct('bye', [])]

        if self.USE_NLG:
            #print('SYSTEM (NLG)> ' + '; '.join([str(sr) for sr in sys_response]))
            sys_utterance = self.nlg.generate_output({'dacts': sys_response})
            # print('SYSTEM: %s ' % sys_utterance)
            if self.NLP_conv:
                self.convrecorder.record(dialogue = 'SYSTEM (NLG)> ' + '; '.join([str(sr) for sr in sys_response]))
            self.convrecorder.record(dialogue = 'SYSTEM > ' + sys_utterance)

        else:
            # print('rSYSTEM: %s ' % '; '.join([str(sr) for sr in sys_response]))
            sys_utterance =  '; '.join([str(sr) for sr in sys_response])

        if self.prev_state:
            self.recorder.record(
                self.prev_state,
                self.curr_state,
                self.prev_action,
                input_utterance=usr_utterance,
                output_utterance=sys_utterance
            )

        self.dialogue_turn += 1

        self.prev_state = deepcopy(self.curr_state)
        self.prev_action = deepcopy(sys_response)
        self.prev_usr_utterance = deepcopy(usr_utterance)
        self.prev_sys_utterance = deepcopy(sys_utterance)
        return sys_utterance

    def end_dialogue(self):
        """
        Perform final dialogue turn. Train and save models if applicable.

        :return: nothing
        """
        self.convrecorder.record(rating = self.dialogue_manager.DSTracker.dialogue_rating)
        self.convrecorder.record(comments = self.dialogue_manager.DSTracker.dialogue_comments)

        #record context
        self.convrecorder.record(context = self.dialogue_manager.DSTracker.DContext.params)
        self.convrecorder.record(reviews = self.dialogue_manager.DSTracker.DContext.feedback)
        # Record final state
        self.recorder.record(
            self.curr_state,
            self.curr_state,
            self.prev_action,
            input_utterance=self.prev_usr_utterance,
            output_utterance=self.prev_sys_utterance
        )

        self.dialogue_episode += 1
        
        if self.dialogue_episode % 10000 == 0:
            self.dialogue_manager.save()

    def terminated(self):
        """
        Check if this agent is at a terminal state.

        :return: True or False
        """

        return self.dialogue_manager.at_terminal_state()


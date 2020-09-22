"""
Copyright (c) 2019 Uber Technologies, Inc.

Licensed under the Uber Non-Commercial License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at the root directory of this project. 

See the License for the specific language governing permissions and
limitations under the License.
"""

__author__ = "Alexandros Papangelis"

from code.bot.jmrs1.Dialogue.Action import DialogueAct, DialogueActItem, Operator
from code.bot.jmrs1.DialogueStateTracker.DialogueStateTracker import MovieStateTracker

from code.bot.jmrs1.DialogueManagement.DialoguePolicy.HandcraftedPolicy import \
    HandcraftedPolicy
from code.bot.jmrs1.Domain.Ontology import Ontology
from code.bot.jmrs1.Domain.DataBase import DataBase, SQLDataBase, JSONDataBase

from copy import deepcopy

import random
import math

"""
The DialogueManager consists of a DialogueStateTracker and a DialoguePolicy. 
It handles the decision-making part of the Conversational Agent. 
Given new input (a list of DialogueActs) it will ensure that the state is 
updated properly and will output a list of DialogueActs in response, after 
querying its DialoguePolicy.
"""


class DialogueManager():
    def __init__(self, args):
        """
        Parses the arguments in the dictionary and initializes the appropriate
        models for Dialogue State Tracking and Dialogue Policy.

        :param args: the configuration file parsed into a dictionary
        """
        self.prev_db_result = None
        if 'settings' not in args:
            raise AttributeError(
                'DialogueManager: Please provide settings (config)!')
        if 'ontology' not in args:
            raise AttributeError('DialogueManager: Please provide ontology!')
        if 'database' not in args:
            raise AttributeError('DialogueManager: Please provide database!')
        if 'domain' not in args:
            raise AttributeError('DialogueManager: Please provide domain!')

        settings = args['settings']
        ontology = args['ontology']
        database = args['database']
        domain = args['domain']

        agent_id = 0
        if 'agent_id' in args:
            agent_id = int(args['agent_id'])

        agent_role = 'system'
        if 'agent_role' in args:
            agent_role = args['agent_role']

        self.settings = settings

        self.TRAIN_DST = False
        self.TRAIN_POLICY = False

        self.MAX_DB_RESULTS = 10

        self.DSTracker = None
        self.policy = None
        self.policy_path = None
        self.ontology = None
        self.database = None
        self.domain = None

        self.agent_id = agent_id
        self.agent_role = agent_role

        self.dialogue_counter = 0
        self.CALCULATE_SLOT_ENTROPIES = False

        if isinstance(ontology, Ontology):
            self.ontology = ontology
        elif isinstance(ontology, str):
            self.ontology = Ontology(ontology)
        else:
            raise ValueError('Unacceptable ontology type %s ' % ontology)

        if isinstance(database, DataBase):
            self.database = database

        elif isinstance(database, str):
            if database[-3:] == '.db':
                self.database = SQLDataBase(database)
            elif database[-5:] == '.json':
                self.database = JSONDataBase(database)
            else:
                raise ValueError('Unacceptable database type %s ' % database)

        else:
            raise ValueError('Unacceptable database type %s ' % database)
                
        if args and args['policy']:
            if 'domain' in self.settings['DIALOGUE']:
                self.domain = self.settings['DIALOGUE']['domain']
            else:
                raise ValueError(
                    'Domain is not specified in DIALOGUE at config.')

            if args['policy']['type'] == 'handcrafted':
                self.policy = HandcraftedPolicy(self.ontology)

            
        # DST Settings
        self.agent_settings = settings['AGENT_' + str(agent_id)]
        if 'DST' in  self.agent_settings and  self.agent_settings['DST']['dst']:
            if self.agent_settings['DST']['dst'] == 'movie':
                    dst_args = dict(
                        zip(
                            ['ontology', 'database', 'domain'],
                            [self.ontology, self.database, domain]))
                    self.DSTracker = MovieStateTracker(dst_args)

        # Default to dummy DST
        if not self.DSTracker:
            dst_args = dict(
                zip(
                    ['ontology', 'database', 'domain'],
                    [self.ontology, self.database, domain]))
            self.DSTracker = MovieStateTracker(dst_args)

        self.load('')

    def initialize(self, args):
        """
        Initialize the relevant structures and variables of the Dialogue
        Manager.

        :return: Nothing
        """

        self.DSTracker.initialize()
        self.policy.initialize(
            **{'is_training': self.TRAIN_POLICY,
                'policy_path': self.policy_path,
                'ontology': self.ontology})

        self.dialogue_counter = 0

    def receive_input(self, inpt):
        """
        Receive input and update the dialogue state.

        :return: Nothing
        """

        # Update dialogue state given the new input
        self.DSTracker.update_state(inpt)


        #for dact in inpt:
            #if dact.intent == 'offer':
                # Perform a database lookup
        db_result, sys_req_slot_entropies = self.db_lookup(inpt)

        # Update the dialogue state again to include the database
        # results
        if db_result:
            self.DSTracker.update_state_db(inpt,
                db_result=db_result,
                sys_req_slot_entropies=sys_req_slot_entropies)

        return inpt

    def generate_output(self, args=None):
        """
        Consult the current policy to generate a response.

        :return: List of DialogueAct representing the system's output.
        """
        
        d_state = self.DSTracker.get_state()
        d_context = self.DSTracker.get_context()

        sys_acts = self.policy.next_action(d_state, d_context)
        #for act in sys_acts:
        #    print(act.intent, [(p.slot, p.value) for p in act.params])
        # Copy the sys_acts to be able to iterate over all sys_acts while also
        # replacing some acts

        draft_sys_acts = deepcopy(sys_acts)
        sys_acts = []
        for i in draft_sys_acts:
            if i not in sys_acts:
                sys_acts.append(i)
        sys_acts_copy = deepcopy(sys_acts)
        new_sys_acts = []

        # Safeguards to support policies that make decisions on intents only
        # (i.e. do not output slots or values)
        for sys_act in sys_acts:
            if sys_act.intent == 'ack_feedback':
                self.DSTracker.DContext.feedback_given = False
                
            if sys_act.intent == 'offer' and sys_act.params and self.domain == 'Movie':
                for param in sys_act.params:
                    if param.slot in self.DSTracker.context_slots:
                        self.DSTracker.DContext.add_offer(param.slot, param.value)

            if sys_act.intent == 'canthelp':
                new_sys_acts.append(
                    DialogueAct(
                        'canthelp',[]))

            if sys_act.intent == 'offer' and not sys_act.params:
                # Remove the empty offer
                sys_acts_copy.remove(sys_act)

                if d_state.item_in_focus:
                    new_sys_acts.append(
                        DialogueAct(
                            'offer',
                            [DialogueActItem(
                                'name',
                                Operator.EQ,
                                d_state.item_in_focus['name'])]))

                    # Only add these slots if no other acts were output
                    # by the DM
                    if len(sys_acts) == 1:
                        for slot in d_state.slots_filled:
                            if slot in d_state.item_in_focus:
                                if slot not in ['id', 'name'] and \
                                        slot != d_state.requested_slot:
                                    new_sys_acts.append(
                                        DialogueAct(
                                            'inform',
                                            [DialogueActItem(
                                                slot,
                                                Operator.EQ,
                                                d_state.item_in_focus[slot])]))
                            else:
                                new_sys_acts.append(
                                    DialogueAct(
                                        'inform',
                                        [DialogueActItem(
                                            slot,
                                            Operator.EQ,
                                            'no info')]))

            elif sys_act.intent == 'inform':
                if self.agent_role == 'system':
                    if sys_act.params and sys_act.params[0].value:
                        continue

                    if sys_act.params:
                        slot = sys_act.params[0].slot
                    else:
                        slot = d_state.requested_slot

                    if not slot:
                        slot = random.choice(list(d_state.slots_filled.keys()))

                    if d_state.item_in_focus:
                        if slot not in d_state.item_in_focus or \
                                not d_state.item_in_focus[slot]:
                            new_sys_acts.append(
                                DialogueAct(
                                    'inform',
                                    [DialogueActItem(
                                        slot,
                                        Operator.EQ,
                                        'no info')]))
                        else:
                            if slot == 'name':
                                new_sys_acts.append(
                                    DialogueAct(
                                        'offer',
                                        [DialogueActItem(
                                            slot,
                                            Operator.EQ,
                                            d_state.item_in_focus[slot])]))
                            else:
                                new_sys_acts.append(
                                    DialogueAct(
                                        'inform',
                                        [DialogueActItem(
                                            slot,
                                            Operator.EQ,
                                            d_state.item_in_focus[slot])]))

                    else:
                        new_sys_acts.append(
                            DialogueAct(
                                'inform',
                                [DialogueActItem(
                                    slot,
                                    Operator.EQ,
                                    'no info')]))

                # Remove the empty inform
                sys_acts_copy.remove(sys_act)

            elif sys_act.intent == 'request':
                # If the policy did not select a slot
                if not sys_act.params:
                    found = False

                    if self.agent_role == 'system':
                        # Select unfilled slot
                        for slot in d_state.slots_filled:
                            if not d_state.slots_filled[slot]:
                                found = True
                                new_sys_acts.append(
                                    DialogueAct(
                                        'request',
                                        [DialogueActItem(
                                            slot,
                                            Operator.EQ,
                                            '')]))
                                break

                    if not found:
                        # All slots are filled
                        new_sys_acts.append(
                            DialogueAct(
                                'request',
                                [DialogueActItem(
                                    random.choice(
                                        list(
                                            d_state.slots_filled.keys())[:-1]),
                                    Operator.EQ, '')]))

                    # Remove the empty request
                    sys_acts_copy.remove(sys_act)

        # Append unique new sys acts
        for sa in new_sys_acts:
            if sa not in sys_acts_copy:
                sys_acts_copy.append(sa)

        self.DSTracker.update_state_sysact(sys_acts_copy)

        return sys_acts_copy

    def db_lookup(self, dacts):
        """
        Perform an SQLite query given the current dialogue state (i.e. given
        which slots have values).

        :return: a dictionary containing the current database results
        """

        # TODO: Add check to assert if each slot in d_state.slots_filled
        # actually exists in the schema.

        d_state = self.DSTracker.get_state()
        #print(str(d_state))
        db_result = None
        # Query the database
        for dact in dacts:
            if dact.intent == 'offer':
                db_result = self.database.db_lookup(d_state)
                self.DSTracker.DState.requested_slot_filled = []

                break
        if db_result:
            random.shuffle(db_result)
            self.prev_db_result = db_result
        elif self.prev_db_result:
            db_result = self.prev_db_result
        #print(len(db_result))
        if db_result:
            # Calculate entropy of requestable slot values in results -
            # if the flag is off this will be empty
            entropies = \
                dict.fromkeys(self.ontology.ontology['system_requestable'])
                
                #print("entropies = {}".format(entropies))
            return db_result[:self.MAX_DB_RESULTS], entropies
        # Failed to retrieve anything
        # print('Warning! Database call retrieved zero results.')
        return db_result, {}

    def restart(self, args):
        """
        Restart the relevant structures or variables, e.g. at the beginning of
        a new dialogue.

        :return: Nothing
        """

        self.DSTracker.initialize(args)
        self.policy.restart(args)
        self.dialogue_counter += 1

    def update_goal(self, goal):
        """
        Update this agent's goal. This is mainly used to propagate the update
        down to the Dialogue State Tracker.

        :param goal: a Goal
        :return: nothing
        """

        if self.DSTracker:
            self.DSTracker.update_goal(goal)
        else:
            print('WARNING: Dialogue Manager goal update failed: No Dialogue '
                  'State Tracker!')

    def get_state(self):
        """
        Get the current dialogue state

        :return: the dialogue state
        """

        return self.DSTracker.get_state()

    def get_context(self):
        return self.DSTracker.get_context()

    def at_terminal_state(self):
        """
        Assess whether the agent is at a terminal state.

        :return: True or False
        """

        return self.DSTracker.get_state().is_terminal()

    def train(self, dialogues):
        """
        Train the policy and dialogue state tracker, if applicable.

        :param dialogues: dialogue experience
        :return: nothing
        """

        if self.TRAIN_POLICY:
            self.policy.train(dialogues)

        if self.TRAIN_DST:
            self.DSTracker.train(dialogues)

    def is_training(self):
        """
        Assess whether there are any trainable components in this Dialogue
        Manager.

        :return: True or False
        """

        return self.TRAIN_DST or self.TRAIN_POLICY

    def load(self, path):
        """
        Load models for the Dialogue State Tracker and Policy.

        :param path: path to the policy model
        :return: nothing
        """

        # TODO: Handle path and loading properly
        self.DSTracker.load('')
        self.policy.load(self.policy_path)

    def save(self):
        """
        Save the models.

        :return: nothing
        """

        if self.DSTracker:
            self.DSTracker.save()

        if self.policy:
            self.policy.save(self.policy_path)

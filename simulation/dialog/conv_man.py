"""
ConversationManager
===================

Author: Shuo Zhang, Krisztian Balog
"""

import configparser
import json
import os.path
import random
import sys
import time
from pprint import pprint
import yaml
from simulation.bot.jmrs1.ConversationalAgent.ConversationalSingleAgent import \
    ConversationalSingleAgent
from simulation.nlp.movies import RESPONSE_TEMPLATES_MS
from simulation.user.movies.movies_simulated_user import MovieSimulatedUser
from simulation.user.human_user import HumanUser
from simulation.bot.bot import Botbot



USER_TAG, AGENT_TAG = "user", "agent"


class ConversationManager:
    """Conversation Manager"""

    def __init__(self, user, bot):
        self._user = user
        self._bot = bot
        self._history = []  # record the chats
        self._chat = None

    def run_single_agent(self, config):
        """
        This function will create an agent and orchestrate the conversation.

        :param config: a dictionary containing settings
        :param num_dialogues: how many dialogues to run for
        :return: some statistics
        """
        ca = ConversationalSingleAgent(config)
        ca.initialize()

        print('=======================================\n')

        last_update_id = None
        while True:
            updates = self._bb.get_updates(last_update_id)
            if len(updates["result"]) > 0:
                last_update_id = self._bb.get_last_update_id(updates) + 1
                for update in updates["result"]:
                    text = update["message"]["text"]
                    chat = update["message"]["chat"]["id"]
                    self._chat = chat
                    self._history = [i for i in self._history if i[2] == self._chat]
                    self._history.append(["user", text, chat])
                    if text.lower() == "hi" or text.lower() == "hello" or text.lower() == "go":
                        system_utterance = ca.start_dialogue()
                    elif text.lower() == "code":
                        if len(self._history) < 8:
                            self._bb.send_message("You have not started your chat!", chat)
                        else:
                            self._bb.send_message("$%GVN&K<112)", chat)
                    else:
                        try:
                            system_utterance = ca.continue_dialogue(text)
                        except:
                            system_utterance = "Ok"
                    self._bb.send_message(system_utterance, chat)
                    self._history.append(["agent", system_utterance, chat])
            time.sleep(0.5)
            if self._chat:
                with open(str(self._chat)+".json", "w", encoding="utf-8") as f:
                    json.dump(self._history, f, indent=2)


    def run_ms(self, config, age_mode="our", persona=True):
        """Let the manager run and monitor the conversations!

        Args:
            config:
            age_mode: qfra/qrfa_test/our
            persona: persona of simulator

        Returns: Dialogue record

        """
        result = {
            "dialog": []
        }
        ca = ConversationalSingleAgent(config)
        ca.initialize()
        if age_mode == "qfra":
            self._user.init_agenda_qrfa()
        elif age_mode == "qrfa_test":
            self._user.init_agenda_qrfa_test()
        elif age_mode == "our":
            self._user.init_agenda()
        else:
            raise TypeError("Set age mode 'qfra', 'qrfa_test', or 'our'")
        result["agenda"] = list(self._user.agenda)
        user_utterance = self._user.init_dialog()
        self._history.append(user_utterance)
        result["dialog"].append([USER_TAG, "Hello", "Non-disclose"])
        while True:
            print("USER: {}.   [{}]".format(user_utterance, self._user._current_intent))
            if user_utterance and user_utterance.lower() == "hi" or \
                    user_utterance.lower() == "hello" or user_utterance.lower() == "go":
                system_utterance = ca.start_dialogue()
                sys_intent = ["Elicit"]
            elif user_utterance.lower() == "stop":
                break
            else:
                system_utterance = ca.continue_dialogue(user_utterance)

            time.sleep(1)
            user_utterance, sys_intent = \
                self._user.generate_response(system_utterance, persona=persona)
            print("System: {}.    [{}]".format(system_utterance, sys_intent))
            result["dialog"].append([AGENT_TAG, system_utterance, sys_intent[0]])
            print("-----------------------------------------------------------")
            if not user_utterance:
                print("ALERT")
            self._history.append(user_utterance)
            result["dialog"].append([USER_TAG, user_utterance, self._user._current_intent])
        result["persona"] = {"persona": self._user.persona, "preferences": self._user.preferences}
        pprint(result)
        return result


def arg_parse(args=None):
    """This function will parse the configuration file that was provided as a
    system argument into a dictionary.

    Args:
        args: config

    Returns: a dictionary containing the parsed config file.

    """

    cfg_parser = None

    arg_vec = args if args else sys.argv

    # Parse arguments
    if len(arg_vec) < 3: print('WARNING: No configuration file.')
    test_mode = arg_vec[1] == '-t'
    if test_mode: return {'test_mode': test_mode}

    # Initialize random seed
    random.seed(time.time())

    cfg_filename = arg_vec[2]
    if isinstance(cfg_filename, str):
        if os.path.isfile(cfg_filename):
            # Choose config parser
            parts = cfg_filename.split('.')
            if len(parts) > 1:
                if parts[1] == 'yaml':
                    with open(cfg_filename, 'r') as file:
                        cfg_parser = yaml.load(file, Loader=yaml.Loader)
                elif parts[1] == 'cfg':
                    cfg_parser = configparser.ConfigParser()
                    cfg_parser.read(cfg_filename)
                else:
                    raise ValueError('Unknown configuration file type: %s'
                                     % parts[1])
        else:
            raise FileNotFoundError('Configuration file %s not found'
                                    % cfg_filename)
    else:
        raise ValueError('Unacceptable value for configuration file name: %s '
                         % cfg_filename)

    dialogues = 10
    interaction_mode = 'simulation'

    if cfg_parser:
        dialogues = int(cfg_parser['DIALOGUE']['num_dialogues'])

        if 'interaction_mode' in cfg_parser['GENERAL']:
            interaction_mode = cfg_parser['GENERAL']['interaction_mode']

    return {'cfg_parser': cfg_parser,
            'dialogues': dialogues,
            'interaction_mode': interaction_mode}

if __name__ == "__main__":
    mode = "manual1"

    if mode == "manual":
        user = HumanUser()  # change here to use a simulated user
        bot = Botbot()
        conv_man = ConversationManager(user, bot)
        args = ['', '-config', os.path.join(os.path.abspath("."),
                                            "simulation/bot/jmrs1/config/movies_text.yaml")]
        args = arg_parse(args)
        cfg_parser = args['cfg_parser']
        dialogues = args['dialogues']
        interaction_mode = args['interaction_mode']
        conv_man.run_single_agent(cfg_parser)
    else:
        hist = []
        # change here to use a simulated user
        user = MovieSimulatedUser("data/1224_ms.json", RESPONSE_TEMPLATES_MS, "ms")
        bot = Botbot()
        conv_man = ConversationManager(user, bot)
        args = ['', '-config', os.path.join(os.path.abspath("."),
                                            "simulation/bot/jmrs1/config/movies_text.yaml")]
        args = arg_parse(args)
        cfg_parser = args['cfg_parser']
        interaction_mode = args['interaction_mode']
        res = conv_man.run_ms(cfg_parser, age_mode="our", persona=True)
        hist.append(res)

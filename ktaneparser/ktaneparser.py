import re
import random

from logmessage import LogMessage
from bomb import Bomb

import threading

LOG_REGEX = re.compile(r'(INFO|DEBUG|WARN).*\[(.*)\] (.*)')

STATE_OUT_OF_BOMB = "OUT_OF_BOMB"
STATE_IN_BOMB = "IN_BOMB"
STATE_LOST = "BOMB_BLEW_UP"
STATE_WIN = "BOMB_DEFUSED"

INITIALIZED_COMPONENT_MAPPINGS = {
    'Wires': 'Simple Wires',
    'BigButton': 'Button',
    'Keypad': 'Keypad',
    'Simon': 'Simon Says',
    'WhosOnFirst': 'Who\'s on First',
    'Memory': 'Memory',
    'Morse': 'Morse Code',
    'Venn': 'Complicated Wires',
    'WireSequence': 'Wire Sequence',
    'Maze': 'Maze',
    'Password': 'Password',
    'NeedyVentGas': 'Vent Gas',
    'NeedyCapacitor': 'Capacitor',
    'NeedyKnob': 'The Knob'
}

FINISHED_COMPONENT_MAPPINGS = {
    'Assets.Scripts.Rules.KeypadRuleSet': 'Keypad',
    'WireSetComponent': 'Simple Wires',
    'SimonComponent': 'Simon Says',
    'InvisibleWallsComponent': 'Maze',
    'MorseCodeComponent': 'Morse Code',
    'Assets.Scripts.Components.VennWire.VennWireComponent': 'Complicated Wires',
    'WireSequencePage': 'Wire Sequence',
    'PasswordComponent': 'Password',
    'Rules.WhosOnFirst': 'Who\'s on First',
}


class KTANEParser:
    def __init__(self, state_file, modules_file, defused_file, success_messages, failure_messages):
        self.curr_state = STATE_OUT_OF_BOMB
        self.last_module = None
        self.bomb = None
        self.bomb_state_message = None

        self.state_file = state_file
        self.modules_file = modules_file
        self.defused_file = defused_file

        self.success_messages = success_messages
        self.failure_messages = failure_messages

        t = threading.Timer(0.5, self._write_state_file)
        t.start()

    def _handle_state_transition(self, msg):
        if msg.is_init_bomb():
            self.curr_state = STATE_IN_BOMB
            return True
        elif msg.is_game_ended_prematurely():
            self.bomb.stop_bomb()
            self.curr_state = STATE_OUT_OF_BOMB
            return True
        elif msg.is_round_end() and self.curr_state != STATE_LOST and self.curr_state != STATE_WIN:
            self.curr_state = STATE_OUT_OF_BOMB
            return True

        return False

    def _set_component(self, msg):
        if msg.component in FINISHED_COMPONENT_MAPPINGS:
            self.last_module = FINISHED_COMPONENT_MAPPINGS[msg.component]
            return

        # special case for "RULES" TODO: BITSIM PLZ FIX
        if "countdown timer" in msg.msg:
            self.last_module = 'Button'
            return

        if "same label you pressed in stage" in msg.msg:
            self.last_module = 'Memory'
            return

        if "Snipped wire" in msg.msg:
            self.last_module = 'Wire Sequence'
            return

    def handle_line(self, line):
        line = line.strip()
        matcher = LOG_REGEX.match(line)
        if matcher is None:
            return

        msg = LogMessage(line)

        # check to see if we're transition states.  do so if neeeded
        if self._handle_state_transition(msg):
            # write_state_file()
            if self.curr_state == STATE_IN_BOMB:
                # we have just init the bomb
                self.bomb = Bomb()
            return # state has changed, nothing else to do

        # TODO: fix this garbage
        if msg.get_generator_settings() is not None:
            self.bomb.time, self.bomb.max_strikes = msg.get_generator_settings()

        if msg.is_strike():
            self.bomb.strikes += 1

        if msg.is_bomb_start():
            self.bomb.start_bomb()

        # check to see if this is a message from a bomb component
        if msg.component == 'Rules' or msg.component in FINISHED_COMPONENT_MAPPINGS:
            self._set_component(msg)

        if msg.is_bomb_seed():
            # found the bomb's seed
            self.bomb.seed = msg.msg[26:]

        if msg.is_new_component():
            comp = msg.is_new_component()
            self.bomb.modules_remaining.append(INITIALIZED_COMPONENT_MAPPINGS[comp])

        if msg.is_explosion():
            self.bomb.stop_bomb()
            self.bomb_state_message = random.choice(self.failure_messages)
            self.curr_state = STATE_LOST

        if msg.is_win():
            self.bomb.stop_bomb()
            self.bomb_state_message = random.choice(self.success_messages)
            self.curr_state = STATE_WIN

        if msg.is_module_complete():
            # self.last_module is the one that is done
            try:
                self.bomb.modules_remaining.remove(self.last_module)
            except ValueError: #TODO: FUCK
                pass
            self.bomb.modules_solved.append(self.last_module)
            pass

    def _write_state_file(self):
        if self.curr_state == STATE_OUT_OF_BOMB:
            bomb_state = 'Not in a bomb'
            modules = ''
            solved = ''
        elif self.curr_state == STATE_LOST:
            bomb_state = self.bomb_state_message
            modules = ''
            solved = ''
        elif self.curr_state == STATE_WIN:
            bomb_state = self.bomb_state_message
            modules = ''
            solved = ''
        elif self.bomb is not None:
            if len(self.bomb.modules_remaining) > 0:
                modules = 'Modules: %s' % ', '.join(self.bomb.modules_remaining)
            else:
                modules = 'Modules:'
            if len(self.bomb.modules_solved) > 0:
                solved = 'Solved: %s' % ', '.join(self.bomb.modules_solved)
            else:
                solved = 'Solved:'

            bomb_state = 'In a bomb with seed: %s (time = %s)' % (self.bomb.seed, self.bomb.get_formatted_time())

        state_file = open(self.state_file, 'w')
        # print "Writing %s to state file" % bomb_state
        state_file.write(bomb_state)
        state_file.close()

        module_file = open(self.modules_file, 'w')
        # print "Writing %s to modules file" % modules
        module_file.write(modules)
        module_file.close()

        solved_file = open(self.defused_file, 'w')
        # print "Writing %s to solved file" % solved
        solved_file.write(solved)
        solved_file.close()

        t = threading.Timer(0.1, self._write_state_file)
        t.start()

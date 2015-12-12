import re

NEW_MODULE_REGEX = re.compile(r'Selected (.*?) \(.*')
LOG_REGEX = re.compile(r'(INFO|DEBUG|WARN).*\[(.*)\] (.*)')
"""Generator settings: Time: 300, NumStrikes: 3, FrontFaceOnly: True"""
GENERATOR_SETTINGS_REGEX = re.compile(r'Generator settings: Time: (\d+), NumStrikes: (\d), FrontFaceOnly: (True|False)')

class LogMessage:
    def __init__(self, line):
        line = line.strip()
        matcher = LOG_REGEX.match(line)
        if matcher is None:
            self.valid = False
            return

        self.level = matcher.group(1)
        self.component = matcher.group(2)
        self.msg = matcher.group(3)
        self.valid = True

    def is_init_bomb(self):
        return self.msg == "Enter GameplayState"

    def is_round_end(self):
        return self.msg == 'OnRoundEnd()'

    def is_round_start(self):
        return self.msg.startswith('Round start!') and self.component == 'Assets.Scripts.Pacing.PaceMaker'

    def is_bomb_seed(self):
        return self.msg.startswith('Generating bomb with seed ')

    def is_new_component(self):
        m = NEW_MODULE_REGEX.match(self.msg)
        if m is None:
            return None

        return m.group(1)

    def is_explosion(self):
        return self.msg == 'Boom'

    def is_win(self):
        return self.msg == 'A winner is you!!'

    def is_module_complete(self):
        return self.component == 'BombComponent' and self.msg == 'Pass'

    def is_game_ended_prematurely(self):
        return self.msg == 'ReturnToSetupRoom'

    def get_generator_settings(self):
        m = GENERATOR_SETTINGS_REGEX.match(self.msg)
        if m is None:
            return None

        time = int(m.group(1))
        strikes = int(m.group(2))

        return time, strikes

    def is_bomb_start(self):
        return self.component == 'Assets.Scripts.Pacing.PaceMaker' and self.msg.startswith('Round start!')

    def is_strike(self):
        return self.component == 'Bomb' and self.msg.startswith('Strike! ')

    def __str__(self):
        return "%s - %s - %s" % (self.level, self.component, self.msg)

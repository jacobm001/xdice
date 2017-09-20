'''
    pydice is a lightweight python library for managing rolls of dice.

    License: GNU

@author: olinox14, 2017
'''
import random
import re

__VERSION__ = 0.1

def compile(pattern_string):  # @ReservedAssignment
    p = Pattern(pattern_string)
    p.compile()
    return p

def roll(pattern_string):
    return Pattern(pattern_string).roll()

def rolldice(faces, amount=1):
    return Dice(faces, amount).roll()

_ALLOWED = {'abs': abs}

def _secured_eval(raw):
    """ securely evaluate the incoming raw string by avoiding the use of any non-allowed function """
    return eval(raw, {"__builtins__":None}, _ALLOWED)

class Dice():
    """
    Dice(sides, amount=1):
    Set of dice.

    Use roll() to get a Score() object.
    """
    def __init__(self, sides, amount=1):
        self._sides = 1
        self._amount = 0

        self.sides = sides
        self.amount = amount

    @property
    def sides(self):
        return self._sides

    @sides.setter
    def sides(self, sides):
        try:
            if not int(sides) >= 1:
                raise ValueError()
        except (TypeError, ValueError):
            raise TypeError("Invalid value for sides (given: '{}')".format(sides))
        self._sides = sides

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        try:
            if not int(amount) >= 0:
                raise ValueError()
        except (TypeError, ValueError):
            raise ValueError("Invalid value for amount (given: '{}')".format(amount))
        self._amount = amount

    def __repr__(self):
        return "<Dice; sides={}; amount={}>".format(self.sides, self.amount)

    def roll(self):
        """ Role the dice and return a Score object """
        return Score([random.randint(1, self._sides) for _ in range(self._amount)])

    @classmethod
    def parse(cls, pattern):
        """ parse a pattern of the form 'xdx', where x are positive integers """
        # normalize
        pattern = str(pattern).replace(" ", "").lower()
        # parse
        amount, faces = (int(x) for x in pattern.split("d"))
        # instanciate
        return Dice(faces, amount)

class Score(int):
    """ Score is a subclass of integer.
    Then you can manipulate it as you would do with an integer.

    It also provides an access to the detail with the property 'results'.
    'results' is the list of the scores obtained by each dice.

    Score class can also be used as an iterable, to walk trough the individual scores.

    eg:
        >>> s = Score([1,2,3])
        >>> print(s)
        6
        >>> s + 1
        7
        >>> list(s)
        [1,2,3]

    """
    def __new__(cls, detail):
        score = super(Score, cls).__new__(cls, sum(detail))
        score._detail = detail
        return score

    @property
    def detail(self):
        return self._detail

    def __repr__(self):
        return "<Score; score={}; detail={}>".format(self.detail, int(self))

    def __contains__(self, value):
        return self.detail.__contains__(value)

    def __iter__(self):
        return self.detail.__iter__()


class Pattern():
    def __init__(self, instr):
        self.instr = Pattern._normalize(instr)
        self.dices = {}
        self.format_string = ""

    @staticmethod
    def _normalize(instr):
        """ normalize the incoming string to a lower string without spaces"""
        return str(instr).replace(" ", "").lower()

    def compile(self):

        def _submatch(match):
            dice = Dice.parse(match.group(0))
            name = "d{}".format(len(self.dices) + 1)
            self.dices[name] = dice
            return "{{{}}}".format(name)

        self.format_string = re.sub('\d+d\d+', _submatch, self.instr)

    def roll(self):
        if not self.format_string:
            self.compile()
        scores = {name: dice.roll() for name, dice in self.dices.items()}
        return PatternScore(self.format_string, scores)

class PatternScore(int):
    def __new__(cls, eval_string, scores):
        ps = super(PatternScore, cls).__new__(cls, _secured_eval(eval_string.format(**scores)))

        ps._eval_string = eval_string
        ps._scores = scores

        return ps

    def format(self):
        return self._eval_string.format(**{name: str(list(score)) for name, score in self._scores.items()})

    def score(self, i):
        return self.scores[i]

    def scores(self):
        return self._scores
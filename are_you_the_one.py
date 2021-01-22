import pandas as pd
import numpy as np

"""
* Can either submit final matchups ahead of time or generate them randomly.
* Retain history.



"""


class Contestant:
    """A single person."""
    pass


class Guy(Contestant):
    """A single guy contestant."""
    def __init__(self, name):
        self.name = name
        self.sex = 'M'


class Girl(Contestant):
    def __init__(self, name):
        self.name = name
        self.sex = 'F'


class Grid:
    """Matrix to track matchups."""
    def __init__(self, guys, girls):
        self.N = len(guys)
        self.X = pd.DataFrame(np.zeros((self.N, self.N), dtype=int),
                              index=[guy.name for guy in guys],
                              columns=[girl.name for girl in girls])


class Round:
    """
    Simulation of a single round.  Consists of a match up and a Truth Booth.
    """
    def __init__(self, matches):
        """Submit matches for the round as a list of tuples."""
        pass


class Tournament(object):
    """Run a tournament or season of Are You the One."""
    def __init__(self, guys, girls):
        """
        Initialize with a sequence of guys and the same number of girls.
        """
        if len(guys) != len(girls):
            raise ValueError("Must pass the same number of guys and girls.")
        else:
            self.grid = Grid(guys, girls)

        self.round = 1
        self.honey_moon_suite = []

    def truth_booth(self, guy_name, girl_name, perfect_match=False):
        """
        Record results of Truth Booth.

        If a perfect match is found, that couple goes to the honey
        moon suite and no longer participates in the match ups.
        """
        # test names are in set
        pass

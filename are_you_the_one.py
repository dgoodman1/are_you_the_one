import itertools as it
from dataclasses import dataclass
from math import factorial
from typing import Any
import pandas as pd
import numpy as np

"""
* Can either submit final matchups ahead of time or generate them randomly.
* Retain history.
* Starting with a "brute force" method of enumerating all possibilities and
    then eliminating false paths as they are identified.
* Need to go back and forth between individual matchups and group info.
"""


@dataclass
class Contestant:
    """A single person."""
    name: str
    sex: str
    gender_preference: str

    def __post_init__(self):
        assert self.sex in ('Male', 'Female',)
        assert self.gender_preference in ('Male', 'Female', 'Both',)

@dataclass
class Guy(Contestant):
    """A single guy contestant."""
    def __init__(self, name: str, gender_preference: str = 'Female'):
        super().__init__(name, 'Male', gender_preference=gender_preference)

@dataclass
class Girl(Contestant):
    def __init__(self, name: str, gender_preference: str = 'Male'):
        super().__init__(name, 'Female', gender_preference=gender_preference)


class Match:
    def __init__(self, guy: Guy, girl: Girl):
        assert guy.gender_preference == girl.sex and \
            girl.gender_preference == guy.sex
        self.guy = guy
        self.girl = girl

    def __repr__(self):
        print(f"({guy}, {girl})")


class Path:
    """A single path through the tournament."""
    def __init__(self, matches: set[tuple]):
        self._matches = matches
        self._N = len(matches)

    def __len__(self):
        return len(self.matches)

    def __repr__(self):
        return f'Path({self.matches})'

    def __str__(self):
        return f'Path({self.matches})'

    def __iter__(self):
        return iter(self.matches)

    @property
    def matches(self):
        return self._matches

    @matches.setter
    def matches(self, matches):
        self._matches = matches


class ActivePaths:
    def __init__(self, paths):
        self.paths = paths


class Grid:
    """Matrix to track matchups."""
    def __init__(self, guys, girls, matches=False):
        self.N = len(guys)

        if matches:
            data = np.identity(self.N, dtype='int')
        else:
            data = np.zeros((self.N, self.N), dtype='int')

        self.X = pd.DataFrame(data, index=[guy.name for guy in guys],
                              columns=[girl.name for girl in girls])


class Matrix(np.ndarray):
    """
    Numpy array of all possible matchups. Guys are represented by the
    column index and their corresponding match is represented by the value.
    """
    def __new__(cls, N_matchups):
        obj = np.zeros((factorial(N_matchups), N_matchups),
                       dtype=np.int8).view(cls)
        obj.N_matchups = N_matchups
        obj._matrix = obj._create_matrix()
        return obj

    def _create_matrix(self, permutation_fcn=it.permutations):
        """Create a matrix of all possible matchups."""
        perm_it = permutation_fcn(np.arange(self.N_matchups))
        return np.array(tuple(perm_it), dtype=np.int8)

    def drop_path(self, path: Path):
        """Drop path (row) from the matrix."""
        mask = np.equal(self._matrix, path).all(axis=1)
        if mask.sum() > 0:
            self._matrix = self._matrix[~mask]

    def drop_paths_containing_match(self, match: Match):
        """
        Drop paths containing a given match.

        After a truth booth tells us that a match is not correct, we
        can drop all paths containing that match.
        """
        mask = self._matrix[:, match[0]] == match[1]
        if mask.sum() > 0:
            self._matrix = self._matrix[~mask]
            print(f"Dropped {mask.sum():,.0f} paths.")

    def drop_paths_not_containing_match(self, match: Match):
        """
        Drop paths that do not contain a given match.

        After a truth booth tells us that a match is correct, we
        can drop all paths that do not contain that match.
        """
        mask = self._matrix[:, match[0]] == match[1]
        if mask.sum() > 0:
            self._matrix = self._matrix[mask]
            print(f"Dropped {mask.sum():,.0f} paths.")

    def drop_paths_not_containing_n_matches(self, path: Path, n: int):
        """
        Drop paths that don't contain n matches from a given path.

        After a ceremony, we know that n matches are correct.
        """
        assert n <= len(path)
        eq_mask = np.equal(self._matrix, path)
        mask = eq_mask.sum(axis=1) == n
        if mask.sum() > 0:
            self._matrix = self._matrix[~mask]

    def __getitem__(self, indices):
        return self._matrix[indices]



class Round:
    """
    Simulation of a single round.  Consists of a match up and a Truth Booth.
    """
    def __init__(self, matches):
        """Submit matches for the round as a list of tuples."""
        self.grid = self._assign_matches(matches)

    def _assign_matches(self, matches):
        """Create a Grid of assigned matches."""
        self.guys, self.girls = zip(*matches)
        return Grid(self.guys, self.girls, matches=True)

    def truth_booth(self, guy_name, girl_name, perfect_match=False):
        """
        Record results of Truth Booth.

        If a perfect match is found, that couple goes to the honey
        moon suite and no longer participates in the match ups.
        """
        # test names are in set
        pass

    def ceremony(self, lights):
        """
        Record the number of lights (perfect matches) at the end of the
        round.
        """
        pass


class Tournament:
    """Run a tournament or season of Are You the One."""
    def __init__(self, guys, girls):
        """
        Initialize with a sequence of guys and the same number of girls.
        """
        if len(guys) != len(girls):
            raise ValueError("Must pass the same number of guys and girls.")
        else:
            self.grid = Grid(guys, girls)

        self.round = Round(list(zip(guys, girls)))
        self.honey_moon_suite = []

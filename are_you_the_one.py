import itertools as it
from dataclasses import dataclass
from math import factorial
from typing import Any
import pandas as pd
import numpy as np
from typing import Union

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
    name: str   # The contestant's nickname from Progress data
    sex: str
    gender_preference: str
    idx: int

    def __post_init__(self):
        assert self.sex in ('Male', 'Female',)
        assert self.gender_preference in ('Male', 'Female', 'Both',)

    def __eq__(self, other: Any):
        if isinstance(other, str):
            return self.name == other
        elif hasattr(other, 'name'):
            return self.name == other.name
        else:
            raise TypeError(f"Cannot compare {type(self)} to {type(other)}.")

    def __repr__(self):
        return (f"{self.__class__.__name__}("
                f"name: {self.name}, "
                f"sex: {self.sex}, "
                f"gender preference: {self.gender_preference}")

    def __str__(self):
        return f"{self.name}"

    def __hash__(self):
        return hash(self.name)


class Guy(Contestant):
    """A single guy contestant."""
    def __init__(self, idx: int, name: str, gender_preference: str = 'Female'):
        super().__init__(name, 'Male', gender_preference=gender_preference,
                         idx=idx)


class Girl(Contestant):
    def __init__(self, idx: int, name: str, gender_preference: str = 'Male'):
        super().__init__(name, 'Female', gender_preference=gender_preference,
                         idx=idx)


class Match:
    def __init__(self, guy: Guy, girl: Girl):
        assert guy.gender_preference == girl.sex and \
            girl.gender_preference == guy.sex
        self.guy = guy
        self.girl = girl

    def __repr__(self):
        print(f"Match({self.guy}, {self.girl})")

    def __getitem__(self, index: int):
        assert index in (0, 1)
        if index == 0:
            return self.guy
        elif index == 1:
            return self.girl

    @property
    def idx(self):
        """Tuple of the numerical indices of the guy and
        girl match."""
        return (self.guy.idx, self.girl.idx)


class Path:
    """A single set of matchups for all contestants."""
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


class Matrix:
    """
    Numpy array of all possible matchups. Guys are represented by the
    column index and their corresponding match is represented by the value.
    """
    def __init__(self, guys: set[Guy], girls: set[Girl]):
        n_guys = len(guys)
        n_girls = len(girls)
        if n_guys != n_girls:
            raise NotImplementedError(f"Number of guys ({n_guys}) must equal "
                                      f"number of girls ({n_girls}).")
        self._guys = {getattr(guy, 'idx'): guy for guy in guys}
        self._girls = {getattr(girl, 'idx'): girl for girl in girls}
        self.N_matchups = n_girls
        self._matrix = self._create_matrix()

    def _create_matrix(self, permutation_fcn=it.permutations):
        """Create a matrix of all possible matchups."""
        perm_it = permutation_fcn(np.arange(self.N_matchups))
        return np.array(tuple(perm_it), dtype=np.int8)

    def drop_path(self, path: Union[Path, np.ndarray, list, tuple]):
        """Drop path (row) from the matrix."""
        mask = np.equal(self._matrix, path).all(axis=1)
        if mask.sum() > 0:
            self._matrix = self._matrix[~mask]

    def drop_paths_containing_match(self, match: Union[Match, tuple]):
        """
        Drop paths containing a given match.

        After a truth booth tells us that a match is not correct, we
        can drop all paths containing that match.
        """
        mask = self._matrix[:, match[0]] == match[1]
        if mask.sum() > 0:
            self._matrix = self._matrix[~mask]
            print(f"Dropped {mask.sum():,.0f} paths.")

    def drop_paths_not_containing_match(self, match: tuple[int, int]):
        """
        Drop paths that do not contain a given match.

        After a truth booth tells us that a match is correct, we
        can drop all paths that do not contain that match.
        """
        mask = self._matrix[:, match[0]] == match[1]
        if mask.sum() > 0:
            self._matrix = self._matrix[mask]
            print(f"Dropped {mask.sum():,.0f} paths.")

    def drop_paths_not_containing_n_matches(self,
                                            path: Union[Path, np.ndarray,
                                                        tuple, list],
                                            n: int):
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

    def __repr__(self):
        return f"Matrix([{self._matrix.shape}]{self._matrix})"

    @property
    def shape(self):
        return self._matrix.shape


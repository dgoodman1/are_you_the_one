import itertools as it
from dataclasses import dataclass
from math import factorial
from typing import Any
from collections import Counter
import numpy as np
from typing import Union
from data_reader import Reader

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
    def __init__(self, matches: set[Match]):
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

    def _check_unique(self, matches: set[Match]):
        """Check that all matches in a path are unique."""
        pass

    @property
    def matches(self):
        return self._matches

    def to_array(self):
        """Convert the path to an array of matches."""
        data = [m[1] for m in sorted(self._matches, key=lambda x: x[0])]
        return np.array(data, dtype=np.int8)


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

    @property
    def feasible_paths(self):
        return self._matrix.shape[0]

    def _count_match_in_matrix(self, match: tuple[int]):
        """Count the number of times a given match occurs."""
        mask = np.equal(self._matrix[:, match[0]] == match[1])
        return mask.sum()

    def prob_match(self, match: Match):
        """Calculate the probability of a given match."""
        guy_idx, girl_idx = match.idx

        return self._count_match_in_matrix((guy_idx, girl_idx)) / \
            self.feasible_paths


class Season:
    """
    A single season of Are You The One?.  This class is used to keep track
    of all the contestants and their matches.
    """
    def __init__(self, season: int):
        self._reader = Reader(season)
        for sex in ('Male', 'Female',):
            self._init_contestants(sex)
        self._matrix = Matrix(self._guys, self._girls)
        self._n_ceremonies = 0
        self._n_truth_booths = 0

    def __repr__(self):
        return f"Season({self._guys}, {self._girls})"

    @property
    def guys(self):
        return self._guys

    @property
    def girls(self):
        return self._girls

    @property
    def n_ceremonies(self):
        """Number of ceremonies held."""
        return self._n_ceremonies

    @property
    def n_truth_booths(self):
        """Number of truth booths held."""
        return self._n_truth_booths

    def _init_contestants(self, sex: str):
        """Initialize the guys for the season."""
        assert sex in ('Male', 'Female',)
        mask = self._reader.cast.sex == sex
        names = self._reader.cast.loc[mask, 'nickname'].tolist()
        if sex == 'Male':
            self._guys = {Guy(i, name) for i, name in enumerate(names)}
        else:
            self._girls = {Girl(i, name) for i, name in enumerate(names)}
        return

    def ceremony(self, matchups: Path, n_perfect_matches: int):
        """Apply results from a ceremony."""
        matchups_array = matchups.to_array()
        (self
         ._matrix
         .drop_paths_not_containing_n_matches(matchups_array,
                                              n_perfect_matches))
        self._n_ceremonies += 1
        print(f"Feasible paths: {self._matrix.feasible_paths:,.0f}")
        return

    def truth_booth(self, match: Match, is_correct: bool):
        """Apply results from a truth booth."""
        if is_correct:
            (self
             ._matrix
             .drop_paths_not_containing_match(match))
        else:
            (self
             ._matrix
             .drop_paths_containing_match(match))
        self._n_truth_booths += 1
        print(f"Feasible paths: {self._matrix.feasible_paths:,.0f}")
        return

# Description: This module is used to read in saved results data
# from the data folder and shape it in a way that facilitates
# rerunning the simulation and testing alternatives.

import os
import pandas as pd


DATA_PATH = 'data/'


class Reader:
    """Read in a parsed results dataset from a csv file."""
    def __init__(self, season: int = None, file_path: str = None):
        self.file_path = file_path or DATA_PATH
        self._files = {'cast': 'cast_season_{}.csv',
                       'correct_matches':
                       'correct_matches_season_{}.csv',
                       'progress': 'progress_season_{}.csv',
                       'truth_booth': 'truth_booth_season_{}.csv'}
        if season:
            for handle, filename in self._files.items():
                path = os.path.join(self.file_path, filename.format(season))
                setattr(self, handle, self.read_data(path))

    def read_data(self, file_path: str, errors='ignore',
                  **kwargs) -> pd.DataFrame:
        """
        Read in the data from the given file path.

        Parameters
        ----------
        file_path : str
            The full file path to the data file.
        errors : str, optional
            How to handle errors. Default is 'ignore', which returns an empty
            DataFrame. Any other value raises a FileNotFoundError when the
            file is not found.
        **kwargs: dict
            Additional keyword arguments to pass to pd.read_csv.
        """
        if os.path.exists(file_path):
            return pd.read_csv(file_path, **kwargs)
        else:
            if errors == 'ignore':
                print(f"File not found: {file_path}")
                return pd.DataFrame()
            else:
                raise FileNotFoundError(f"File not found: {file_path}")

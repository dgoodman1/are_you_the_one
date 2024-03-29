# pull data from Wikipedia
import re
from collections import defaultdict
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Only implemented for these seasons due to differences in structure
# or type of data available. Will need more development to parse
# the interstitial seasons.
AVAILABLE_SEASONS = [1, 2, 3, 4, 6, 7, 9]


def remove_square_brackets(text):
    cleaned_text = re.sub('\[.*?\]', '', text)
    return cleaned_text


def parse_cell_value(element):
    """
    Parse table cell value (text) and correct match status (if available)
    from html element.
    """
    text_value = remove_square_brackets(element.text.strip())
    style = element.attrs.get('style', '')
    if len(style):
        styles = dict([v.strip().split(":")
                       for v in style.split(";") if len(v)])
        bg_color = styles.get('background', '')

        if bg_color in ('salmon', 'lightgreen'):
            if bg_color == 'salmon':
                status = 'Unconfirmed Perfect Match'
            else:
                status = 'Confirmed Perfect Match'

            return text_value, status

    return text_value


def listify_table(table):
    """Parse html table into list of lists."""
    data = []
    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all(['th', 'td'])
        cols = [parse_cell_value(ele) for ele in cols]
        data.append(cols)

    return data


def parse_cast_table(table):
    """Build Cast table from a list of lists."""
    headers = ['cast_member', 'age', 'hometown']
    sex = table[0][0].split()[0].title()
    body = table[1:]
    df = (pd.DataFrame(body, columns=headers)
            .assign(sex=sex)
            .astype({'age': 'int'}))

    return df


def parse_progress_table(table):
    """
    Parse Progress table from a list of lists. Returns a normalized
    DataFrame with the matchups and results of each ceremony and a Series
    with the number of lights at the end of each ceremony (correct
    matches).
    """
    ceremony_idx = pd.Index([int(i) for i in table[1]], name='ceremony')
    correct_matches = pd.Series(table[-1][1:], index=ceremony_idx,
                                name='n_correct').astype('int')

    sex = table[0][0][:-1].lower()
    other_sex = 'girl' if sex == 'guy' else 'guy'
    header = pd.Index([sex] + ceremony_idx.tolist(), name='ceremony')
    match_data, status_data = [], []
    for row in table[2:-1]:
        match_row, status_row = [], []
        for i, val in enumerate(row):
            if isinstance(val, tuple):
                match_row.append(val[0])
                status_row.append(val[1])
            else:
                if val == '—':
                    val = None
                match_row.append(val)
                if i == 0:
                    status_row.append(val)
                else:
                    status_row.append('Not A Match')
        match_data.append(match_row)
        status_data.append(status_row)

    match_df = (pd.DataFrame(match_data, columns=header)
                .set_index(sex)
                .stack()
                .rename(other_sex))
    status_df = (pd.DataFrame(status_data, columns=header)
                 .set_index(sex)
                 .stack()
                 .rename('status'))

    df = pd.concat([match_df, status_df],
                   keys=[other_sex, 'status'], axis=1)

    return df, correct_matches


def parse_truth_booth_table(table):
    """Parse Truth Booth results from list of lists."""
    headers = [col.lower() for col in table[0]]
    body = table[1:]
    df = pd.DataFrame(body, columns=headers)
    df[['guy', 'girl']] = df.couple.str.split(' & ', expand=True)
    df = df.drop('couple', axis=1)
    # TODO: parse episode number
    # df.episode = df.episode.astype('int')
    df = df.rename(columns={'result': 'tb_result'})

    return df


def build_cast_frame(cast_tables):
    """Build Cast DataFrame from a list of the two [list of list]
    Cast tables."""
    return (pd.concat([parse_cast_table(tbl) for tbl in cast_tables],
                      ignore_index=True))


def add_nickname_to_cast(cast, progress):
    """
    Add nickname to cast DataFrame so it matches with progress DataFrame.

    Return `cast` DataFrame with `nickname` column added.
    """
    for sex in ("Male", "Female",):
        sex_type = 'guy' if sex == "Male" else 'girl'
        prog_nicknames = progress.query("ceremony < 10")[sex_type].unique()
        cast_names = cast.query("sex==@sex").cast_member.unique()

        names = defaultdict(list)
        for nickname in prog_nicknames:
            i = 0
            for full_name in cast_names:
                if nickname.replace('.', '') in full_name:
                    names[full_name].append(nickname)
                    i += 1

                if i > 1:
                    for nn in names[full_name]:
                        if nn == full_name.split()[0]:
                            names[full_name] = [nickname]
                            i = 1
                            break
                        else:
                            names[full_name].remove(nn)
                            i -= 1

            if i != 1:
                raise ValueError(f"Multiple matches for {nickname} in cast.")

        if len(names) != len(cast_names):
            missing = set(cast_names) - set(names)
            raise ValueError(f"Missing nicknames for {','.join(missing)} "
                             "from progress table.")
        else:
            mask = cast.sex == sex
            cast.loc[mask, 'nickname'] = (cast[mask]
                                          .cast_member
                                          .map(lambda x: names[x][0]))

    return cast


def main(season):
    """Parse data from Wikipedia."""
    if season not in AVAILABLE_SEASONS:
        raise NotImplementedError(f"Season {season} not available.")

    base_url = f'https://en.wikipedia.org/wiki/Are_You_the_One%3F_(season_{season})'
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = soup.find_all('table', attrs={'class': 'wikitable'}, limit=5)

    # convert html tables to lists of lists
    list_data = [listify_table(table) for table in tables]

    cast = build_cast_frame(list_data[:2])
    cast['season'] = season

    progress, correct_matches = parse_progress_table(list_data[2])
    progress['season'] = season
    progress = progress.reset_index()
    correct_matches = (correct_matches
                       .reset_index()
                       .assign(season=season))

    # add nickname to cast DataFrame so it matches with progress DataFrame
    cast = add_nickname_to_cast(cast, progress)

    # skipping Table 3 since it's the same data as Table 2

    truth_booth = parse_truth_booth_table(list_data[4])
    truth_booth['season'] = season

    return cast, progress, correct_matches, truth_booth


if __name__ == '__main__':
    # download data for all available seasons
    for season in AVAILABLE_SEASONS:
        cast, progress, correct_matches, truth_booth = main(season)
        season_results = {'cast': cast,
                          'progress': progress,
                          'correct_matches': correct_matches,
                          'truth_booth': truth_booth}

        # save data
        for name, df in season_results.items():
            df.to_csv(f'data/{name}_season_{season}.csv', index=False)

        print(f"Saved data to 'data' directory for Season {season}.")

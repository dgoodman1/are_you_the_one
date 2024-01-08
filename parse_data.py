# pull data from Wikipedia
import pandas as pd
import requests
from bs4 import BeautifulSoup

SEASON = 1
base_url = f'https://en.wikipedia.org/wiki/Are_You_the_One%3F_(season_{SEASON})'


def parse_cell_value(element):
    """
    Parse table cell value (text) and correct match status (if available)
    from html element.
    """
    style = element.attrs.get('style', '')
    if 'background' in style:
        color = style.replace('background:', '')
        if color == 'salmon':
            status = 'Unconfirmed Perfect Match'
        elif color == 'lightgreen':
            status = 'Confirmed Perfect Match'
        else:
            raise ValueError(f'Unknown color: {color}')

        return element.text.strip(), status
    else:
        return element.text.strip()


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
    sex = table[0][0].split()[0].lower()
    body = table[1:]
    return (pd.DataFrame(body, columns=headers)
            .assign(sex=sex)
            .astype({'age': 'int'}))


def parse_progress_table(table):
    """
    Parse Progress table from a list of lists. Returns a normalized
    DataFrame with the matchups and results of each ceremony and a Series
    with the number of lights at the end of each ceremony (correct
    matches).
    """
    ceremony_idx = pd.Index([int(i) for i in table[1]], name='Ceremony')
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
                match_row.append(val)
                if i == 0:
                    status_row.append(val)
                else:
                    status_row.append('Not a Match')
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
                   keys=['match', 'status'], axis=1)

    return df, correct_matches


def parse_truth_booth_table(table):
    """Parse Truth Booth results from list of lists."""
    pass


def build_cast_frame(cast_tables):
    """Build Cast DataFrame from a list of the two [list of list]
    Cast tables."""
    return (pd.concat([parse_cast_table(tbl) for tbl in cast_tables],
                      ignore_index=True))


if __name__ == '__main__':
    # get the data
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    tables = soup.find_all('table', attrs={'class':'wikitable'}, limit=5)

    # convert html tables to lists of lists
    list_data = [listify_table(table) for table in tables]

    cast = build_cast_frame(list_data[:2])
    progress, correct_matches = parse_progress_table(list_data[2])

    print("Done.")

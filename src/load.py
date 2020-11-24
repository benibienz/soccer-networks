import pandas as pd
import networkx as nx
import re
from .util import TransferNetwork

# keep this table growing for overlapping names so that we can simplify it
club_name_mappings = {
    "leicester": "leicester city",
    "sheff": "sheffield",
    "west brom": "west bromwich albion",
    "wolves": "wolverhampton wanderers",
    "brighton": "brighton & hove albion",
    "norwich": "norwich city",
    "tottenham": "tottenham hotspur",
    "west ham": "west ham united",
}

# exclusions for club names
name_exclusions = [" fc", "fc ", "club ", " club"]

# re for extracting under age from name
u_age_re = re.compile(r"[uU][1-9]+")


# function to clean name
def name_cleaner(name: str) -> str:
    name = name.lower().strip()

    # Manchester
    name = name.replace("man ", "manchester ")

    # merge youth teams
    for substr in u_age_re.findall(name):
        name = name.replace(substr, "")

    # merge B team
    if name.endswith(" b"):
        name = name[:-2]

    # standardize "united" teams
    for substr in ["united", "utd.", " utd"]:
        if substr in name:
            name = name.replace(substr, "") + " united"

    # now look through the others
    for substr in name_exclusions:
        if substr in name:
            name = name.replace(substr, "")

    name = name.replace("  ", " ").strip()
    # finally, if the team has a mapping, look for the mapping
    if name in club_name_mappings:
        name = club_name_mappings[name]

    return name


def basic_transfer_network_from_df(df: pd.DataFrame) -> TransferNetwork:
    """
    Create a basic transfer network from a pandas dataframe. Directed
    edges are player from club x to club y.

    Inputs:
        table:  pandas dataframe with columns 'club_name', 'club_involved_name', 'transfer_movement'
    Outputs:
        nx.DiGraph
    """

    # get all the raw club names
    clubs = set(
        list(df["club_name"].unique()) + list(df["club_involved_name"].unique())
    )

    # create a mapping from the club names in the table to our standardized club names
    table_to_standard = {club: name_cleaner(club) for club in clubs}

    G = nx.DiGraph()

    league_clubs = set()
    for idx, row in df.iterrows():

        # get the standardized names
        club_name = table_to_standard[row["club_name"]]
        club_involved = table_to_standard[row["club_involved_name"]]

        if row["transfer_movement"] == "in":
            G.add_edge(club_involved, club_name)
        elif row["transfer_movement"] == "out":
            G.add_edge(club_name, club_involved)

        league_clubs.add(club_name)

    return TransferNetwork(G, list(league_clubs))


def load_prem_basic_transfer_networks(start_year=2000, end_year=2020) -> dict:
    """Loads premier league TransferNetwork objects for given year range"""
    basic_transfer_networks = {}
    for year in range(start_year, end_year + 1):
        df = pd.read_csv(f"data/{year}/english_premier_league.csv")
        basic_transfer_networks[year] = basic_transfer_network_from_df(df)
    return basic_transfer_networks

import pandas as pd
import networkx as nx

import re

# keep this table growing for overlapping names so that we can simplify it
club_name_mappings = {
    'man': 'manchester', 
    'man city': 'manchester city', 
    'leicester': 'leicester city', 
    'sheff': 'sheffield', 
    'west brom': 'west bromwich albion', 
    'wolves': 'wolverhampton wanderers'
}

# exclusions for club names
name_exclusions = [
    'united', 'utd.', ' utd',
    ' fc', 'fc ', 
    'club ', ' club'
]

# re for extracting under age from name
u_age_re = re.compile(r'[uU][1-9]+')

# function to clean name
def name_cleaner(name: str) -> str:
    name = name.lower()
    
    # first look for re
    for substr in u_age_re.findall(name):
        name = name.replace(substr, '')
    
    # now look through the others
    for substr in name_exclusions:
        if substr in name:
            name = name.replace(substr, '')
            
    # remove left and right white space
    stripped_name = name.strip()
    
    # finally, if the team has a mapping, look for the mapping
    if stripped_name in club_name_mappings:
        stripped_name = club_name_mappings[stripped_name]
        
    return stripped_name

def basic_from_pandas(df: pd.DataFrame) -> nx.Graph:
    '''
    Create a basic transfer network from a pandas dataframe. Directed 
    edges are player from club x to club y. 

    Inputs:
        table:  pandas dataframe with columns 'club_name', 'club_involved_name', 'transfer_movement'
    Outputs:
        nx.DiGraph
    '''

    # get all the raw club names
    clubs = set(list(df['club_name'].unique()) + list(df['club_involved_name'].unique()))

    # create a mapping from the club names in the table to our standardized club names
    table_to_standard = {club: name_cleaner(club) for club in clubs}

    G = nx.DiGraph()

    for idx, row in df.iterrows():

        # get the standardized names
        club_name = table_to_standard[row['club_name']]
        club_involved = table_to_standard[row['club_involved_name']]
        
        if row['transfer_movement'] == 'in':
            # get the clean name 
            G.add_edge(club_involved, club_name)
            
        elif row['transfer_movement'] == 'out':
            G.add_edge(club_name, club_involved)

    return G
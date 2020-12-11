from collections import namedtuple

"""
Object for storing transfer table networks
G: nx Graph
league_clubs: list of clubs in the league that year
"""
TransferNetwork = namedtuple("TransferNetwork", ["G", "league_clubs"])

'''
Object for storing financial transfer network

G: nx MultiDiGraph
league_clubs: list clubs in the network
currency: str the national currency that the transfers are done in
denomination: float the denomination of currency. Ex: 1000000 means a value of 4 is 4 million
edge_key: str the key to use to access the financial data in an edge
'''
FinancialTransferNetwork = namedtuple(
    'FinancialTransferNetwork',
    ['G', 'league_clubs', 'currency', 'denomination', 'edge_key']
)

'''
Object for storing basic transfer information

direction:  (str) 'in' or 'out'. Direction of the player either out to club involved or in from club involved
club_involved:  (str) the other club involved
fee:    (float) the fee amount
'''
BasicTransfer = namedtuple(
    'BasicTransfer',
    ['direction', 'club_involved', 'fee']
)

'''
Object for storing a full transfer network. Includes keys for player name, fee amount, 
year of transfer, and transfer window as well as currency information

G:  (nx MultiDiGraph)
league_cliubs:  (list) clubs in the network
currency:   (str) the currency used
denomination:   (float) the factor by which the fee amounts are multiplied by
player_key: (str) the key to extract a player's name from an edge
fee_key:    (str) the key to extract the transfer fee from an edge
year_key:   (str) the key to extract the year of the transfer from an edge
window_key: (str) the key to extract the transfer window fro an edge
'''
FullTransferNetwork = namedtuple(
    'FullTransferNetwork',
    ['G', 'league_clubs', 'currency', 'denomination', 'player_key', 'fee_key', 'year_key', 'window_key']
)

'''
Object for storing a full transfer network. Includes keys for player name, fee amount, 
year of transfer, and transfer window as well as currency information. Single graph
over many years

G:  (nx MultiDiGraph)
league_cliubs:  (list) clubs in the network
currency:   (str) the currency used
denomination:   (float) the factor by which the fee amounts are multiplied by
player_key: (str) the key to extract a player's name from an edge
fee_key:    (str) the key to extract the transfer fee from an edge
year_key:   (str) the key to extract the year of the transfer from an edge
window_key: (str) the key to extract the transfer window fro an edge
start_year: (int) the first year of transfers in the network
end_year:   (int) the last year of transfers in the network
'''
AggregateFullTransferNetwork = namedtuple(
    'AggregateFullTransferNetwork',
    ['G', 'league_clubs', 'currency', 'denomination', 'player_key', 'fee_key', 'year_key', 'window_key', 'start_year', 'end_year']
)

'''
Object for storing a team's name, ranking and transfer data

name:   (str) club name
rank:   (int) the end of season rank of the club
transfers:  (list) basic transfer objects for the season
currency:   (str) the national currency used for transfers
denomination:   (float) the denomination of the currency. Ex: 100 means a value of 4 is 400
'''
ClubSeasonInfo = namedtuple(
    'ClubSeasonInfo',
    ['name', 'rank', 'transfers', 'currency', 'denomination']
)
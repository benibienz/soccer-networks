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
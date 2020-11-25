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
Object for storing a team's name, ranking and transfer data

name: str club name
rank: int the end of season rank of the club
fee_in: float the amount of money paid to the club in a season
fee_out: float the amount of money paid to the club in a season
currency: str the national currency used for transfers
denomination: float the denomination of the currency. Ex: 100 means a value of 4 is 400
'''
ClubSeasonInfo = namedtuple(
    'ClubSeasonInfo',
    ['name', 'rank', 'fee_in', 'fee_out', 'currency', 'denomination']
)

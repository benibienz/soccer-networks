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
denomination: float the denominations of currency. Ex: 1000000 means a value of 4 is 4 million
edge_key: str the key to use to access the financial data in an edge
'''
FinancialTransferNetwork = namedtuple(
    'FinancialTransferNetwork',
    ['G', 'league_clubs', 'currency', 'denomination', 'edge_key']
)

from collections import namedtuple

"""
Object for storing transfer table networks
G: nx Graph
league_clubs: list of clubs in the league that year 
"""
TransferNetwork = namedtuple("TransferNetwork", ["G", "league_clubs"])

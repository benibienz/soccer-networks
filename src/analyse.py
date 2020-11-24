from .util import TransferNetwork


def highest_in_degree(transfer_nw: TransferNetwork) -> str:
    """Returns name of prem club with highest in-degree"""
    res, max_in_deg = None, 0
    for club in transfer_nw.league_clubs:
        in_deg = transfer_nw.G.in_degree(club)
        if in_deg > max_in_deg:
            res = club
            max_in_deg = in_deg
    return res

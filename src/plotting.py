import matplotlib.pyplot as plt

from .analyse import get_league_avg_degrees, get_league_degrees, get_league_avg_season_fee

def plot_english_league_season_fee(
    include_championship: bool = False, start_year: int = 2000, end_year: int = 2020
):
    '''
    Plots average and min max of season fee (excluding loans) into the 
    league and out of the league

    Inputs:
        include_championship: optionally include championship
        start_year: start year
        end_year: end year

    Outputs:
        Array of 2 pyplot ax objects
    '''
    prem_df = get_league_avg_season_fee(start_year=start_year, end_year=end_year)
    if include_championship:
        champ_df = get_league_avg_season_fee('english_championship', start_year=start_year, end_year=end_year)

    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    degs = ['in', 'out']

    for i, ax in enumerate(axes): 
        deg = degs[i]

        if include_championship:
            ax.plot(
                champ_df[f'avg {deg}'],
                label=f'Championship mean {deg}-degree',
                color=(0, 0, 0.8, 0.9),
            )
            ax.fill_between(
                champ_df.index,
                champ_df[f'min {deg}'],
                champ_df[f'max {deg}'],
                color=(0, 0, 0.8, 0.1),
                label=None,
            )

        ax.plot(
            prem_df[f'avg {deg}'],
            label=f'Premier Leauge mean {deg}-degree',
            color=(0.63, 0.16, 0.82, 0.9),
        )
        ax.fill_between(
            prem_df.index,
            prem_df[f'min {deg}'],
            prem_df[f'max {deg}'],
            color=(0.63, 0.16, 0.82, 0.1),
            label=None,
        )

        ax.set_xlim(start_year, end_year)
        ax.set_ylim(0)
        ax.set_ylabel('Fee (millions of pounds)')
        ax.set_xlabel('Transfer year')
        ax.set_xticks(range(start_year, end_year + 1))
        ax.tick_params(axis='x', rotation=40)

        if deg == 'in':
            ax.set_title(f'Average amount paid by another club for transfer')

        else:
            ax.set_title(f'Average amount paid to another club for transfer')
            
    return axes

def plot_english_league_avg_degrees(
    include_championship: bool = False, start_year: int = 2000, end_year: int = 2020
):
    """
    Plots avg and +/- 1 std of premier league in and out degrees
    Args:
        include_championship: optionally include championship
        start_year: start year
        end_year: end year

    Returns:
        Array of 2 pyplot ax objects
    """
    prem_df = get_league_avg_degrees("english_premier_league")
    if include_championship:
        champ_df = get_league_avg_degrees("english_championship")

    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    degs = ["in", "out"]

    for i, ax in enumerate(axes):
        deg = degs[i]
        if include_championship:
            ax.plot(
                champ_df[f"avg {deg}"],
                label=f"Championship mean {deg}-degree",
                color=(0, 0, 0.8, 0.9),
            )
            ax.fill_between(
                champ_df.index,
                champ_df[f"avg {deg}"] - champ_df[f"std {deg}"],
                champ_df[f"avg {deg}"] + champ_df[f"std {deg}"],
                color=(0, 0, 0.8, 0.1),
                label=None,
            )
        ax.plot(
            prem_df[f"avg {deg}"],
            label=f"Premier Leauge mean {deg}-degree",
            color=(0.63, 0.16, 0.82, 0.9),
        )
        ax.fill_between(
            prem_df.index,
            prem_df[f"avg {deg}"] - prem_df[f"std {deg}"],
            prem_df[f"avg {deg}"] + prem_df[f"std {deg}"],
            color=(0.63, 0.16, 0.82, 0.1),
            label=None,
        )

        ax.set_xlim(start_year, end_year)
        ax.set_ylim(0, 50)
        ax.set_xticks(range(start_year, end_year + 1))
        ax.tick_params(axis="x", rotation=40)
        ax.set_title(f"Average {deg}-degrees of transfers")
    return axes


def plot_prem_teams_against_avg_deg(
    teams: list, team_colors: list = None, start_year: int = 2000, end_year: int = 2020
):
    """
    Plot a team or teams against the average premier league in and out degrees
    Args:
        teams: list of cleaned team names
        team_colors: optional list of colors for plotting (same length as teams)
        start_year: start year
        end_year: end year

    Returns:
        array of pyplot axes
    """
    if team_colors is None:
        team_colors = [None]  # stupid Python best practices

    degrees_df = get_league_degrees(league="english_premier_league")
    axes = plot_english_league_avg_degrees(include_championship=False)

    for i, team in enumerate(teams):
        for j, deg in enumerate(["in", "out"]):
            axes[j].plot(
                degrees_df[f"{team} {deg}-degree"],
                label=f"{team} {deg}-degree",
                color=team_colors[i],
            )
    for ax in axes:
        ax.legend()

    return axes

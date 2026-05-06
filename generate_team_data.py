import requests
import pandas as pd

def get_bracket(year):
    url = "https://api-web.nhle.com/v1/playoff-bracket/" + str(year)
    response = requests.get(url)
    bracket = dict(response.json())
    topSeeds = [x['topSeedTeam']['abbrev'] for x in bracket['series'][:8]]
    bottomSeeds = [x['bottomSeedTeam']['abbrev'] for x in bracket['series'][:8]]
    teams = topSeeds + bottomSeeds
    return teams

def get_season_end_date(year, day = 15, last_day = 30, first_day = 1):
    day_str = str(day)
    if day < 10:
        day_str = "0" + day_str
    url = "https://api-web.nhle.com/v1/standings/" + str(year) + "-04-" + day_str
    if year == 1991 or year == 2020:
        url = "https://api-web.nhle.com/v1/standings/" + str(year) + "-03-" + day_str
    response = requests.get(url)
    team_stats = dict(response.json())
    if team_stats['standings'] == []:
        if day == first_day:
            return day - 1
        else:
            return get_season_end_date(year, day = int((day - first_day)/2) + first_day, last_day = day, 
                                       first_day = first_day)
    else:
        if day == last_day:
            return day
        else:
            return get_season_end_date(year, day = int((last_day - day)/2) + day + 1, last_day = last_day, 
                                       first_day = day + 1)    

def get_team_stats(year, teams):
    end_date = get_season_end_date(year)
    end_date_str = str(end_date)
    if end_date < 10:
        end_date_str = "0" + end_date_str
    team_stats = {}
    url = "https://api-web.nhle.com/v1/standings/" + str(year) + "-04-" + end_date_str
    if year == 1991 or year == 2020:
        url = "https://api-web.nhle.com/v1/standings/" + str(year) + "-03-" + end_date_str
    response = requests.get(url)
    stats = dict(response.json())
    for team in teams:
        stats_dic = {}
        t = 0
        while stats['standings'][t]['teamAbbrev']['default'] != team:
            t+=1
        stats_dic['goalsFor'] = stats['standings'][t]['goalFor']/stats['standings'][t]['gamesPlayed']
        stats_dic['goalsAgainst'] = stats['standings'][t]['goalAgainst']/stats['standings'][t]['gamesPlayed']
        stats_dic['wins'] = stats['standings'][t]['wins']/stats['standings'][t]['gamesPlayed']
        stats_dic['losses'] = stats['standings'][t]['losses']/stats['standings'][t]['gamesPlayed']
        stats_dic['otLosses'] = stats['standings'][t]['otLosses']/stats['standings'][t]['gamesPlayed']
        stats_dic['l10goalsFor'] = stats['standings'][t]['l10GoalsFor']
        stats_dic['l10goalsAgainst'] = stats['standings'][t]['l10GoalsAgainst']
        stats_dic['l10Wins'] = stats['standings'][t]['l10Wins']
        stats_dic['l10Losses'] = stats['standings'][t]['l10Losses']
        stats_dic['l10OTLosses'] = stats['standings'][t]['l10Points'] - 2*stats_dic['l10Wins']
        team_stats[team] = stats_dic
    for y in range(1,10):
        url = "https://api-web.nhle.com/v1/playoff-bracket/" + str(year - y)
        response = requests.get(url)
        bracket = str(response.json())
        for team in teams:
            team_stats[team]['ranking-' + str(y)] = bracket.count("\'" + team + "\'")
    return team_stats
        
def save_input_data(year):
    teams = get_bracket(year)
    team_stats = get_team_stats(year, teams)
    df_input_data = pd.DataFrame.from_dict(team_stats, orient='index')
    df_input_data.to_csv("team_stats/team_stats_year=" + str(year) + ".csv", index=True)

def generate_dataset():
    for year in range(1980, 2027):
        print(year)
        if year != 2005:
            save_input_data(year)
            
def get_results():
    results = {}
    for year in range(1980,2026):
        if year != 2005:
            results[str(year)] = {}
            url = "https://api-web.nhle.com/v1/playoff-bracket/" + str(year)
            response = requests.get(url)
            bracket = dict(response.json())
            topSeeds = [x['topSeedTeam']['abbrev'] for x in bracket['series'][:8]]
            bottomSeeds = [x['bottomSeedTeam']['abbrev'] for x in bracket['series'][:8]]
            bracket = str(response.json())
            teams = topSeeds + bottomSeeds
            for i, team in enumerate(teams):
                results[str(year)]['Team' + str(i)] = team
                results[str(year)]['Rank' + str(i)] = bracket.count("\'" + team + "\'")**2
    df_results_data = pd.DataFrame.from_dict(results, orient='index')
    df_results_data.to_csv("playoff_results.csv", index=True)

if __name__ == "__main__":
    generate_dataset()
    get_results()

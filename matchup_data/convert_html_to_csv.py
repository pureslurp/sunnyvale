from bs4 import BeautifulSoup
import pandas as pd
import os
from utils import team_abbrev
import argparse

class Player:
    '''Placeholder for a Player class to be used with the to be created Roster class
    
    This class is only representative of a Player during the week specified.
    '''
    def __init__(self, name_position_team:str, fan_pts:float, proj_pts:float):
        self.name = extract_player_name(name_position_team)
        self.position = extract_position(name_position_team)
        self.fan_pts = fan_pts
        self.proj_pts = proj_pts
        self.team = extract_team(name_position_team)

    @property
    def is_flex(self):
        match self.position:
            case "WR":
                return True
            case "TE":
                return True
            case "RB":
                return True
            case _:
                return False
    
    @property
    def net_points(self):
        return self.proj_pts - self.fan_pts
    
    def __str__(self):
        return f"{self.name}, {self.position}, {self.team}"

class Roster:
    '''A given teams Roster and their stats for a particular week, constructed from html'''
    def __init__(self, team_name: str, starting_df: pd.DataFrame, bench_df: pd.DataFrame):
        '''df's column must be in the following order:
        |Player|Proj|Fan Pts|
        '''
        roster_key = {
            "QB" : 0,
            "WR1" : 1,
            "WR2" : 2,
            "RB1" : 3,
            "RB2" : 4,
            "TE" : 5,
            "FLEX1" : 6,
            "FLEX2" : 7,
            "DEF" : 8,
            "BN1" : 0,
            "BN2" : 1,
            "BN3" : 2,
            "BN4" : 3,
            "BN5" : 4,
            "BN6" : 5,
            "BN7" : 6,
            "BN8" : 7
        }
        self.roster: dict[str, Player] = dict.fromkeys(list(roster_key.keys()))
        for k, v in roster_key.items():
            # (TODO) This is sketchy, there has to be a better way to do this...
            try:
                self.roster[k] = Player(name_position_team=starting_df.iloc[v,0], fan_pts=starting_df.iloc[v,2], proj_pts=starting_df.iloc[v,1])
            except:
                self.roster[k] = Player(name_position_team=bench_df.iloc[v,0], fan_pts=bench_df.iloc[v,2], proj_pts=bench_df.iloc[v,1])
        self.team_name = team_name
    
    @property
    def starting_points(self):
        starting_lineup = ["QB", "WR1", "WR2", "RB1", "RB2", "TE", "FLEX1", "FLEX2", "DEF"]
        total = 0
        for pos in starting_lineup:
            total += self.roster[pos].fan_pts
        return total

    @property
    def bench_points(self):
        bench_lineup = ["BN1", "BN2", "BN3", "BN4", "BN5", "BN6", "BN7", "BN8"]
        total = 0
        for pos in bench_lineup:
            total += self.roster[pos].fan_pts
        return total
    
    def manager_eff(self):
        # NICK THIS IS WHERE YOU WORK YOUR MAGIC
        return

    def __str__(self):
        for key in self.roster:
            print(self.roster[key])
        return

class MatchUp:
    def __init__(self, team1_roster: Roster, team2_roster: Roster):
        self.team1_roster = team1_roster
        self.team2_roster = team2_roster
    
    @property
    def winner(self):
        return self.team1_roster.team_name if self.team1_roster.starting_points > self.team2_roster.starting_points else self.team2_roster.team_name
    
    @property
    def dataframe_for_csv(self):
        columns = [self.team1_roster.team_name, "Position", "Fan Pts", "Roster Position", "Fan Pts.1", "Position.1", self.team2_roster.team_name]
        starting_matchup_df = pd.DataFrame(columns=columns)
        bench_matchup_df = pd.DataFrame(columns=columns)
        roster_positions = ["QB", "WR", "WR", "RB", "RB", "W/R/T", "W/R/T", "TE", "DEF", "Total"]
        for pos in range(len(roster_positions)):
            if roster_positions[pos] == "Total":
                row = [None, None, self.team1_roster.starting_points, roster_positions[pos], self.team2_roster.starting_points, None, None]
            else:
                team_1_player = list(self.team1_roster.roster.values())[pos]
                team_2_player = list(self.team2_roster.roster.values())[pos]
                row = [team_1_player.name, team_1_player.position, team_1_player.fan_pts, roster_positions[pos], team_2_player.fan_pts, team_2_player.position, team_2_player.name]
            starting_matchup_df.loc[len(starting_matchup_df)] = row
        for i in range(8):
            team_1_player = list(self.team1_roster.roster.values())[i+9]
            team_2_player = list(self.team2_roster.roster.values())[i+9]
            row = [team_1_player.name, team_1_player.position, team_1_player.fan_pts, roster_positions[pos], team_2_player.fan_pts, team_2_player.position, team_2_player.name]
            bench_matchup_df.loc[len(bench_matchup_df)] = row
        bench_matchup_df.loc[len(bench_matchup_df)] = [None, None, self.team1_roster.bench_points, "Total", self.team2_roster.bench_points, None, None]
        combined_df = pd.concat([starting_matchup_df, bench_matchup_df], ignore_index=True)
        return combined_df

class Roster:
    '''A given teams Roster and their stats for a particular week, constructed from html'''
    def __init__(self, team_name: str, starting_df: pd.DataFrame, bench_df: pd.DataFrame):
        '''df's column must be in the following order:
        |Player|Proj|Fan Pts|
        '''
        roster_key = {
            "QB" : 0,
            "WR1" : 1,
            "WR2" : 2,
            "RB1" : 3,
            "RB2" : 4,
            "TE" : 5,
            "FLEX1" : 6,
            "FLEX2" : 7,
            "DEF" : 8,
            "BN1" : 0,
            "BN2" : 1,
            "BN3" : 2,
            "BN4" : 3,
            "BN5" : 4,
            "BN6" : 5,
            "BN7" : 6,
            "BN8" : 7
        }
        self.roster: dict[str, Player] = dict.fromkeys(list(roster_key.keys()))
        for k, v in roster_key.items():
            # (TODO) This is sketchy, there has to be a better way to do this...
            try:
                self.roster[k] = Player(name_position_team=starting_df.iloc[v,0], fan_pts=starting_df.iloc[v,2], proj_pts=starting_df.iloc[v,1])
            except:
                self.roster[k] = Player(name_position_team=bench_df.iloc[v,0], fan_pts=bench_df.iloc[v,2], proj_pts=bench_df.iloc[v,1])
        self.team_name = team_name
    
    @property
    def starting_points(self):
        starting_lineup = ["QB", "WR1", "WR2", "RB1", "RB2", "TE", "FLEX1", "FLEX2", "DEF"]
        total = 0
        for pos in starting_lineup:
            total += self.roster[pos].fan_pts
        return total

    @property
    def bench_points(self):
        bench_lineup = ["BN1", "BN2", "BN3", "BN4", "BN5", "BN6", "BN7", "BN8"]
        total = 0
        for pos in bench_lineup:
            total += self.roster[pos].fan_pts
        return total
    
    def manager_eff(self):
        # NICK THIS IS WHERE YOU WORK YOUR MAGIC
        return

    def __str__(self):
        for key in self.roster:
            print(self.roster[key])
        return

class MatchUp:
    def __init__(self, team1_roster: Roster, team2_roster: Roster):
        self.team1_roster = team1_roster
        self.team2_roster = team2_roster
    
    @property
    def winner(self):
        return self.team1_roster.team_name if self.team1_roster.starting_points > self.team2_roster.starting_points else self.team2_roster.team_name
    
    @property
    def dataframe_for_csv(self):
        columns = [self.team1_roster.team_name, "Position", "Fan Pts", "Roster Position", "Fan Pts.1", "Position.1", self.team2_roster.team_name]
        starting_matchup_df = pd.DataFrame(columns=columns)
        bench_matchup_df = pd.DataFrame(columns=columns)
        roster_positions = ["QB", "WR", "WR", "RB", "RB", "W/R/T", "W/R/T", "TE", "DEF", "Total"]
        for pos in range(len(roster_positions)):
            if roster_positions[pos] == "Total":
                row = [None, None, self.team1_roster.starting_points, roster_positions[pos], self.team2_roster.starting_points, None, None]
            else:
                team_1_player = list(self.team1_roster.roster.values())[pos]
                team_2_player = list(self.team2_roster.roster.values())[pos]
                row = [team_1_player.name, team_1_player.position, team_1_player.fan_pts, roster_positions[pos], team_2_player.fan_pts, team_2_player.position, team_2_player.name]
            starting_matchup_df.loc[len(starting_matchup_df)] = row
        for i in range(8):
            team_1_player = list(self.team1_roster.roster.values())[i+9]
            team_2_player = list(self.team2_roster.roster.values())[i+9]
            row = [team_1_player.name, team_1_player.position, team_1_player.fan_pts, roster_positions[pos], team_2_player.fan_pts, team_2_player.position, team_2_player.name]
            bench_matchup_df.loc[len(bench_matchup_df)] = row
        bench_matchup_df.loc[len(bench_matchup_df)] = [None, None, self.team1_roster.bench_points, "Total", self.team2_roster.bench_points, None, None]
        combined_df = pd.concat([starting_matchup_df, bench_matchup_df], ignore_index=True)
        return combined_df

def convert_league_matchup_table_to_csv(week):
    '''convert week{WEEK}_matchups.html to a user friendly csv that shows all the league matchups as a summary'''
    if os.path.exists(f"matchup_data/week{week}/matchups.csv"):
            print(f"csv for matchups already exists")
    else:
        try:
            with open(F'matchup_data/week{week}/week{week}_matchups.html') as fp:
                soup = BeautifulSoup(fp, 'html.parser')

            matchup_df = pd.DataFrame(columns=["Team1", "Team1 Score", "Team2", "Team2 Score", "Winner"])

            for matchup in soup.find_all('li'):
                team1 = matchup.find_all('a')[1].text
                team1_score = float(matchup.find_all('div')[11].text)
                team2 = matchup.find_all('a')[4].text
                team2_score = float(matchup.find_all('div')[18].text)
                winner = team2 if team2_score > team1_score else team1
                row = [team1, team1_score, team2, team2_score, winner]
                matchup_df.loc[len(matchup_df)] = row
            matchup_df.to_csv(f"matchup_data/week{week}/matchup.csv")
            print("created matchups csv")
        except:
            print(f"Week {week} matchups html not available")
        

def extract_position(text):
    '''function that extracts the position from Yahoo player html'''
    try:
        text = text.split(" - ")[1].split(" ")[0]
    except:
        pass
    return text

def extract_player_name(text):
    text = str(text).split("-")[0].strip()
    if text[-2:].upper() in team_abbrev:
        player = text[:-2]
    elif text[-3:].upper() in team_abbrev:
        player = text[:-3]
    else:
        player = text
    return player

def extract_team(text):
    text = str(text).split("-")[0].strip()
    if text[-2:].upper() in team_abbrev:
        return text[-2:].upper()
    elif text[-3:].upper() in team_abbrev:
        return text[-3:].upper()
    else:
        return None


def clean_matchup_df(df):
    '''cleans up the Yahoo html table by removing unneeded columns and linting player data'''
    df.drop(['Stats', 'Stats.1'], axis=1, inplace=True)
    df["Position"] = df["Player"].apply(lambda x: extract_position(x))
    df["Player"] = df["Player"].apply(lambda x: extract_player_name(x))
    df["Position.1"] = df["Player.1"].apply(lambda x: extract_position(x))
    df["Player.1"] = df["Player.1"].apply(lambda x: extract_player_name(x))
    return df

def convert_detailed_matchup_to_csv(week):
    '''covert each matchup (matchup_{i}.html) to a user friendly csv table'''
    for i in range(1,7):
        if os.path.exists(f"matchup_data/week{week}/matchup_{i}.csv"):
            print(f"csv for week {week} matchup {i} already exists")
            continue
        else:
            try:
                with open(F'matchup_data/week{week}/matchup_{i}.html') as fp:
                    soup = BeautifulSoup(fp, 'html.parser')

                matchup_header = soup.find("section", {"id": "matchup-header"})
                team1 = matchup_header.find_all('div')[6].text
                team2 = matchup_header.find_all('div')[19].text
                matchup_df = pd.read_html(f'matchup_data/week{WEEK}/matchup_{i}.html')
                team_1_roster = Roster(team1, matchup_df[1].iloc[:,1:4], matchup_df[2].iloc[:,1:4])
                team_2_cols = ["Player.1", "Fan Pts.1", "Proj.1"]
                team_2_roster = Roster(team2, matchup_df[1][team_2_cols], matchup_df[2][team_2_cols])
                matchup = MatchUp(team_1_roster, team_2_roster)
                combined_df = matchup.dataframe_for_csv
                combined_df.to_csv(f"matchup_data/week{week}/matchup_{i}.csv")
                print(f"created csv for matchup {i}")
            except:
                print(f"Week {week} matchup {i} html not available")

def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("week", type=int, help="NFL Week")
    args = argParser.parse_args()
    convert_league_matchup_table_to_csv(args.week)
    convert_detailed_matchup_to_csv(args.week)

if __name__ == "__main__":
    main()
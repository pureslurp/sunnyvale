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
    def is_flex(self) -> bool:
        '''Check if a Player is an eligible flex position'''
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
        "Calculate the Players net points"
        return self.fan_pts - self.proj_pts
    
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
        self.pf_rank = None
        self.h2h_record: list[int] = [0,0]
    
    def position_points(self, position) -> float:
        '''Return the rosters starting position points based on a position'''
        starting_lineup = ["QB", "WR1", "WR2", "RB1", "RB2", "TE", "FLEX1", "FLEX2", "DEF"]
        total = 0
        if position == "All":
            for pos in starting_lineup:
                total += self.roster[pos].fan_pts
        else:
            for pos in starting_lineup:
                if pos[:2] == position or pos[:-1] == position:
                    total += self.roster[pos].fan_pts
        return total

    
    @property
    def starting_points(self) -> float:
        '''Return the rosters starting points for scored'''
        starting_lineup = ["QB", "WR1", "WR2", "RB1", "RB2", "TE", "FLEX1", "FLEX2", "DEF"]
        total = 0
        for pos in starting_lineup:
            total += self.roster[pos].fan_pts
        return total

    @property
    def bench_points(self) -> float:
        '''Return the rosters bench points for scored'''
        bench_lineup = ["BN1", "BN2", "BN3", "BN4", "BN5", "BN6", "BN7", "BN8"]
        total = 0
        for pos in bench_lineup:
            total += self.roster[pos].fan_pts
        return total
    
    @property
    def net_points(self):
        '''Returns the net points your starting lineup scores above (or below) projected'''
        starting_lineup = ["QB", "WR1", "WR2", "RB1", "RB2", "TE", "FLEX1", "FLEX2", "DEF"]
        net = 0
        for pos in starting_lineup:
            net += self.roster[pos].net_points
        return net


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
    def winner(self) -> str:
        '''Return the winner of the Matchup'''
        return self.team1_roster.team_name if self.team1_roster.starting_points > self.team2_roster.starting_points else self.team2_roster.team_name
    
    @property
    def teams(self) -> list[str]:
        '''Return the teams involved in the matchup'''
        return [self.team1_roster.team_name, self.team2_roster.team_name]
    
    def points_against(self, team) -> float:
        '''Returns a teams points for'''
        if team == self.team1_roster.team_name:
            return self.team2_roster.starting_points
        else:
            return self.team1_roster.starting_points
        
    def points_for(self, team) -> float:
        '''Returns a teams points against'''
        if team == self.team1_roster.team_name:
            return self.team1_roster.starting_points
        else:
            return self.team2_roster.starting_points
    
    def point_above_projected(self, team) -> float:
        '''Returns the points scored above projected for a team in a matchup'''
        if team == self.team1_roster.team_name:
            return self.team1_roster.net_points
        else:
            return self.team2_roster.net_points
        
    def h2h_record(self, team) -> list[int]:
        '''Returns a team's head-to-head record against all Rosters'''
        if team == self.team1_roster.team_name:
            return self.team1_roster.h2h_record
        else:
            return self.team2_roster.h2h_record

    @property
    def dataframe_for_csv(self) -> pd.DataFrame:
        '''Returns a dataframe that is easily exported to a csv'''
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
    
class Week:
    '''A class that stores league matchups for a given week'''
    def __init__(self, league_matchups:list[MatchUp], week: int):
        self.league_matchups: list[MatchUp] = league_matchups
        self.league_rosters: list[Roster] = self.flatten_matchups
    
    @property
    def flatten_matchups(self) -> list[Roster]:
        '''Return all the Rosters flattened into a list'''
        roster_list = []
        for matchup in self.league_matchups:
            roster_list.append(matchup.team1_roster)
            roster_list.append(matchup.team2_roster)
        return roster_list

    @property
    def league_teams(self) -> list[str]:
        '''Returns a list of teams in the league'''
        teams = []
        for roster in self.league_rosters:
            teams.append(roster.team_name)
        return teams

    @property
    def get_pf_rankings(self):
        '''Populates the current object with points for rankings'''
        def _get_score(roster: Roster):
            return roster.starting_points
        self.league_rosters.sort(key=_get_score, reverse=True)
        for i in range(len(self.league_rosters)):
            self.league_rosters[i].pf_rank = i + 1
        return self
    
    @property
    def get_h2h_record(self):
        '''Populates the current object with h2h record'''
        self.get_pf_rankings
        for i in range(len(self.league_rosters)):
            self.league_rosters[i].h2h_record = [11-i, i]
        return self
    
    @property
    def advanced_df(self) -> pd.DataFrame:
        '''Returns a dataframe with head-to-head and manager efficiency data'''
        self.get_h2h_record
        advanced_df = pd.DataFrame(columns=["Team", "H2H", "Manager Eff"])
        for roster in self.league_rosters:
            row = [roster.team_name, roster.h2h_record, "Nick"]
            advanced_df.loc[len(advanced_df)] = row
        return advanced_df
    
    @property
    def winners(self) -> list[str]:
        '''Returns the winners of the Week'''
        winners = []
        for matchup in self.league_matchups:
            winners.append(matchup.winner)
        return winners

class Season:
    def __init__(self, season_summary: list[Week]):
        '''Season long stats for every Roster for every Week'''
        self.season_summary = season_summary
        self.teams = self.season_summary[0].league_teams

    def get_pf_data_for_boxplot_df(self, position:str="All") -> pd.DataFrame:
        '''Returns a dataframe that is easily compatible with a boxplot'''
        team_list = []
        pf_list = []
        for team in self.teams:
            for i in range(len(self.season_summary)):
                for roster in self.season_summary[i].league_rosters:
                    if team == roster.team_name:
                        team_list.append(team)
                        if position == "All":
                            pf_list.append(roster.starting_points)
                        else:
                            pf_list.append(roster.position_points(position))
        df = pd.DataFrame({"Team" : team_list,
                          "Points For" : pf_list})
        return df
            
    def get_power_rankings(self, df) -> pd.DataFrame:
        '''
        attributes
        - PF = 1st (4pts * 11)
        - H2H Wins = (2nd 3pts * 11)
        - Floor = 4th (1pt * 11)
        - Ceiling = 3rd (2pts * 11)
        '''
        def _extract_h2h_wl(wl_str):
            return wl_str.split("-")
        df_c_f = self.get_pf_ceiling_and_floor
        df["PF PR"] = df["PF"].rank(ascending=True) * 4
        df_c_f["Ceiling PR"] = df_c_f["Ceiling"].rank(ascending=True) * 2
        df_c_f["Floor PR"] = df_c_f["Floor"].rank(ascending=True)
        df["H2H Wins"] = df["H2H"].apply(lambda x: _extract_h2h_wl(x)[0])
        df["H2H Wins PR"] = df["H2H Wins"].rank(ascending=True) * 3
        df = pd.merge(df, df_c_f, how="left", on="Team")
        df = df[["Team", "PF PR", "Ceiling PR", "Floor PR", "H2H Wins PR"]]
        df["PR Total"] = df["PF PR"] + df["Ceiling PR"] + df["Floor PR"] + df["H2H Wins PR"]
        df["Power Ranking"] = df["PR Total"].rank(ascending=False)
        return df[["Team", "Power Ranking"]]

    def get_position_rank(self, position) -> pd.DataFrame:
        '''Returns the rank a team is for a given position in the entire season'''
        df = self.get_pf_data_for_boxplot_df(position)
        df = df.groupby("Team").mean()
        df = df.reset_index()
        df[f"{position} Rank"] = df["Points For"].rank(ascending=False)
        return df[["Team", f"{position} Rank"]]
    
    @property
    def get_pf_ceiling_and_floor(self) -> pd.DataFrame:
        '''Returns the ceiling and floor of a team for the given season'''
        df = self.get_pf_data_for_boxplot_df()
        df = df.groupby('Team')['Points For'].apply(list).reset_index(name='Points For')
        df["Ceiling"] = df["Points For"].apply(lambda x: max(x))
        df["Floor"] = df["Points For"].apply(lambda x: min(x))
        return df[["Team", "Ceiling", "Floor"]]

    @property
    def position_ranking_df(self) -> pd.DataFrame:
        '''Returns a dataframe of postiion rankings'''
        # CLEAN THIS UP
        qb_rank_df = self.get_position_rank("QB")
        rb_rank_df = self.get_position_rank("RB")
        wr_rank_df = self.get_position_rank("WR")
        te_rank_df = self.get_position_rank("TE")
        flex_rank_df = self.get_position_rank("FLEX")
        df = pd.merge(qb_rank_df, rb_rank_df, how="left", on="Team")
        df = pd.merge(df, wr_rank_df, how="left", on="Team")
        df = pd.merge(df, te_rank_df, how="left", on="Team")
        df = pd.merge(df, flex_rank_df, how="left", on="Team")
        df["Avg Rank"] = round(df[["RB Rank", "WR Rank", "TE Rank", "FLEX Rank"]].mean(axis=1),2)
        return df


    @property
    def season_summary_df(self) -> pd.DataFrame:
        # (TODO) There has to be a better way to do this...
        df = pd.DataFrame(columns=["Team", "Record", "PF", "PA", "H2H", "PaP", "Manager Eff"])
        for team in self.teams:
            w = 0
            l = 0
            pf = 0
            pa = 0
            h2hw = 0
            h2hl = 0
            pap = 0
            manager_eff = "Nick"
            
            for i in range(len(self.season_summary)):
                self.season_summary[i].get_h2h_record
                for matchup in self.season_summary[i].league_matchups:
                    if team in matchup.teams:
                        pa += matchup.points_against(team)
                        pf += matchup.points_for(team)
                        pap += matchup.point_above_projected(team)
                        if matchup.winner == team:
                            w += 1 
                        else:
                            l += 1
                        h2h = matchup.h2h_record(team)
                        h2hw += h2h[0]
                        h2hl += h2h[1]
            pap = round(pap / len(self.season_summary), 2)
            row = [team, f"{w}-{l}", pf, pa, f"{h2hw}-{h2hl}", pap, manager_eff]
            df.loc[len(df)] = row
        pr_df = self.get_power_rankings(df.copy())
        df = pd.merge(pr_df, df, how="left", on="Team")
        return df.sort_values(by=["Power Ranking"], ascending=True)       

def get_weeks(week) -> list[Week]:
    '''Returns all the week data up to a given week'''
    weeks: list[Week] = []
    for i in range(1,week):
        matchups = []
        for j in range(1,7):
            matchups.append(convert_detailed_matchup_to_df(i, j))
        weeks.append(Week(matchups, i))
    return weeks

def convert_league_matchup_table_to_df(week) -> None | pd.DataFrame:
    '''convert week{WEEK}_matchups.html to a user friendly csv that shows all the league matchups as a summary'''
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
        #matchup_df.to_csv(f"matchup_data/week{week}/matchup.csv")
        return matchup_df
    except:
        print("issue creating df for week ", week)
        return
        

def extract_position(text) -> str:
    '''function that extracts the position from Yahoo player html'''
    try:
        text = text.split(" - ")[1].split(" ")[0]
    except:
        pass
    return text

def extract_player_name(text) -> str:
    '''function that extracts the player name from the Yahoo player html'''
    text = str(text).split("-")[0].strip()
    if text[-2:].upper() in team_abbrev:
        player = text[:-2]
    elif text[-3:].upper() in team_abbrev:
        player = text[:-3]
    else:
        player = text
    return player

def extract_team(text) -> None | str:
    '''function that extracts the team name from the Yahoo player html'''
    text = str(text).split("-")[0].strip()
    if text[-2:].upper() in team_abbrev:
        return text[-2:].upper()
    elif text[-3:].upper() in team_abbrev:
        return text[-3:].upper()
    else:
        return None

def convert_detailed_matchup_to_df(week, i) -> None | pd.DataFrame:
    '''covert each matchup (matchup_{i}.html) to a user friendly csv table'''
    try:
        with open(F'matchup_data/week{week}/matchup_{i}.html') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        matchup_header = soup.find("section", {"id": "matchup-header"})
        team1 = matchup_header.find_all('div')[6].text
        team2 = matchup_header.find_all('div')[19].text
        matchup_df = pd.read_html(f'matchup_data/week{week}/matchup_{i}.html')
        team_1_roster = Roster(team1, matchup_df[1].iloc[:,1:4], matchup_df[2].iloc[:,1:4])
        team_2_cols = ["Player.1", "Proj.1", "Fan Pts.1"]
        team_2_roster = Roster(team2, matchup_df[1][team_2_cols], matchup_df[2][team_2_cols])
        matchup = MatchUp(team_1_roster, team_2_roster)
        return matchup
    except:
        print("issue creating df for week", week, " matchup", i)
        return

def main():
    argParser = argparse.ArgumentParser()
    argParser.add_argument("week", type=int, help="NFL Week")
    args = argParser.parse_args()
    if os.path.exists(f"matchup_data/week{args.week}/matchups.csv"):
        print(f"csv for matchups already exists")
    else:
        matchup_df = convert_league_matchup_table_to_df(args.week)
        matchup_df.to_csv(f"matchup_data/week{args.week}/matchup.csv")

    for i in range(1,7):
        if os.path.exists(f"matchup_data/week{args.week}/matchup_{i}.csv"):
            print(f"csv for week {args.week} matchup {i} already exists")
        else:
            try:
                matchup = convert_detailed_matchup_to_df(args.week, i)
                combined_df = matchup.dataframe_for_csv
                combined_df.to_csv(f"matchup_data/week{args.week}/matchup_{i}.csv")
            except:
                print(f"Week {args.week} matchup {i} html not available")
    
if __name__ == "__main__":
    main()
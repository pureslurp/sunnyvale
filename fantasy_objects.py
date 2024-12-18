from utils import extract_player_name, extract_position, extract_team, manager_eff, schedule
import pandas as pd

'''
This file contains all the objects used, the nesting structure is as follows:

Season contains a list of Week's -> Season = list[Week]
Week contains a list of Roster's -> Week = list[Roster]
Roster contains a list of Player's -> Roster = list[Player]
'''

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
        '''Return the rosters starting position points based on a position
        
        position options: QB, WR, RB, TE, FLEX
        '''
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
    def get_positions_pf(self):
        keys = ["QB", "RB", "WR", "TE", "FLEX"]
        pos_dict = dict.fromkeys(keys)
        columns = ["Team"] + keys
        df = pd.DataFrame(columns=columns)
        for roster in self.league_rosters:
            team = roster.team_name
            for pos in keys:
                pts = roster.position_points(pos)
                pos_dict[pos] = pts
            row = [team, pos_dict["QB"], pos_dict["RB"], pos_dict["WR"], pos_dict["TE"], pos_dict["FLEX"]]
            df.loc[len(df)] = row
        return df
    
    @property
    def get_position_ranks(self):
        df = self.get_positions_pf
        positions = df.columns.tolist()[1:]
        for pos in positions:
            df[pos] = df[pos].rank(ascending=False)
        df["Avg Rank"] = round(df[["QB", "RB", "WR", "TE", "FLEX"]].mean(axis=1),2)
        return df


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
        advanced_df = pd.DataFrame(columns=["Team", "PF", "H2H", "Manager Eff"])
        for roster in self.league_rosters:
            row = [roster.team_name, roster.starting_points, roster.h2h_record, "Nick"]
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
    
    def get_points_for_df(self, last_n=None):
        '''Returns a df that has the columns of Team and a list of points for'''
        def _last_n_sum(list, l_n):
            return list[-l_n:]
        df = self.get_pf_data_for_boxplot_df()
        df = df.groupby('Team')['Points For'].apply(list).reset_index(name='Points For')
        if last_n is None:
            return df
        else:
            df["Points For"] = df["Points For"].apply(lambda x: _last_n_sum(x, last_n))
            return df
        
    def get_trending_team(self, fire=True):
        '''Returns the top 3 teams that have the highest PF the last 3 weeks if fire is True, else returns lowest 3 teams'''
        def _extract_last_three(pf_list):
            return sum(pf_list[-3:])
        df = self.get_points_for_df()
        df["L3"] = df["Points For"].apply(lambda x: _extract_last_three(x))
        df = df.sort_values(by=["L3"], ascending=False)
        team_list = df["Team"].tolist()
        if fire:
            return team_list[:3]
        else:
            return team_list[-3:]

            
    def get_power_rankings(self, df) -> pd.DataFrame:
        '''
        attributes
        - PF = 1st (4pts * 11)
        - H2H Wins = (2nd 3pts * 11)
        - Floor = 4th (1pt * 11)
        - Ceiling = 3rd (2pts * 11)
        '''
        def _remove_emoji(team):
            if team[-1] == "🔥" or team[-1] == "❄️":
                return team[:-1]
            else:
                return team
        def _extract_h2h_wl(wl_str):
            return int(wl_str.split("-")[0])
        df_c_f = self.get_pf_ceiling_and_floor(last_n=5)
        df["Team"] = df["Team"].apply(lambda x: _remove_emoji(x))
        pf = self.get_points_for_df(last_n=5)
        df["PF"] = pf["Points For"].apply(lambda x: sum(x))
        df["PF PR"] = df["PF"] / max(df["PF"]) * 12 * 4
        df_c_f["Ceiling PR"] = df_c_f["Ceiling"] / max(df_c_f["Ceiling"]) * 12 * 2
        df_c_f["Floor PR"] = df_c_f["Floor"] / max(df_c_f["Floor"]) * 12
        df["H2H Wins"] = df["H2H"].apply(lambda x: _extract_h2h_wl(x))
        df["H2H Wins PR"] = df["H2H Wins"] / max(df["H2H Wins"]) * 12 * 3
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
    
    def get_pf_ceiling_and_floor(self, last_n=None) -> pd.DataFrame:
        '''Returns the ceiling and floor of a team for the given season'''
        df = self.get_points_for_df(last_n=last_n)
        df["Ceiling"] = df["Points For"].apply(lambda x: max(x))
        df["Floor"] = df["Points For"].apply(lambda x: min(x))
        return df[["Team", "Ceiling", "Floor"]]

    def playoff_teams(self, summary: pd.DataFrame):
        '''returns a list of current playoff teams'''
        def _split(value, by, pos):
            return value.split(by)[pos]
        df = summary[["Team", "Record", "PF"]]
        df["w"] = df["Record"].apply(lambda x: _split(x, "-", 0))
        df["l"] = df["Record"].apply(lambda x: _split(x, "-", 1))
        df = df.sort_values(by="w", ascending=False)
        # check for ties
        if df.iloc[3]['w'] == df.iloc[4]['w']:
            if df.iloc[4]['w'] == df.iloc[5]['w']:
                if df.iloc[5]['w'] == df.iloc[6]['w']:
                    df = df.head(7)
                else:
                    df = df.head(6)
            else:
                df = df.head(5)
        else:
            df = df.head(4)

        tie_teams_low = df[df["w"] == df['w'].min()]
        other = df[df["w"] != df['w'].min()]
        remaining_spots = 4 - len(other)
        tie_teams_low = tie_teams_low.sort_values(by="PF", ascending=False)
        tie_teams_low = tie_teams_low.head(remaining_spots)
        df = pd.concat([other, tie_teams_low])

        return df['Team'].tolist()

    
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

    def get_projected_record(self, df: pd.DataFrame, remaining_games = 3):
        def _extract_wins(wl_string):
            return int(wl_string.split("-")[0])
        def _extract_losses(wl_string):
            return int(wl_string.split("-")[1])
        df["proj w"] = df["Record"].apply(lambda x: _extract_wins(x))
        df["proj l"] = df["Record"].apply(lambda x: _extract_losses(x))
        for week in schedule.values():
            for matchup in week:
                if int(df[df['Team'] == matchup[0]]["Power Ranking"]) > int(df[df['Team'] == matchup[1]]["Power Ranking"]):
                    df.loc[df["Team"] == matchup[0], "proj l"] += 1
                    df.loc[df["Team"] == matchup[1], "proj w"] += 1
                else:
                    df.loc[df["Team"] == matchup[0], "proj w"] += 1
                    df.loc[df["Team"] == matchup[1], "proj l"] += 1
        df['Proj Record'] = [f"{a}-{b}" for a, b in zip(df["proj w"], df["proj l"])]
        df.drop(["proj w", "proj l"], axis=1, inplace=True)
        return df
    
    @property
    def season_summary_df(self) -> pd.DataFrame:
        # (TODO) There has to be a better way to do this...
        def _add_fire(team_str, on_fire_list):
            if team_str in on_fire_list:
                return f"{team_str}🔥"
            else:
                return team_str
        def _add_snowflake(team_str, snowflake_list):
            if team_str in snowflake_list:
                return f"{team_str}❄️"
            else:
                return team_str
        def _playoffs(team_str, playoff_list):
            if team_str in playoff_list:
                return f"{team_str} -p"
            else:
                return team_str
        df = pd.DataFrame(columns=["Team", "Record", "PF", "PA", "H2H", "PaP", "Manager Eff"])
        on_fire_teams = self.get_trending_team(fire=True)
        snowflake_teams = self.get_trending_team(fire=False)
        for team in self.teams:
            w = 0
            l = 0
            pf = 0
            pa = 0
            h2hw = 0
            h2hl = 0
            pap = 0
            
            for i in range(len(self.season_summary)):
                self.season_summary[i].get_h2h_record
                for matchup in self.season_summary[i].league_matchups:
                    if team in matchup.teams:
                        man_eff = manager_eff[team]
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
            row = [team, f"{w}-{l}", pf, pa, f"{h2hw}-{h2hl}", pap, f"{round(man_eff * 100,2)}%"]
            df.loc[len(df)] = row
        pr_df = self.get_power_rankings(df.copy())
        df = pd.merge(pr_df, df, how="left", on="Team")
        df = self.get_projected_record(df)
        df["Team"] = df["Team"].apply(lambda x: _playoffs(x, ['Pitter Patter']))
        df["Team"] = df["Team"].apply(lambda x: _add_fire(x, on_fire_teams))
        df["Team"] = df["Team"].apply(lambda x: _add_snowflake(x, snowflake_teams))
        return df.sort_values(by=["Power Ranking"], ascending=True)       

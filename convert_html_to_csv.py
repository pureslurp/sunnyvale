from bs4 import BeautifulSoup
import pandas as pd
import os
import argparse
from fantasy_objects import Roster, MatchUp

def convert_league_matchup_table_to_df(week) -> None | pd.DataFrame:
    '''convert week{WEEK}_matchups.html to a user friendly csv that shows all the league matchups as a summary'''
    try:
        with open(F'matchup_data/week{week}/week{week}_matchups.html') as fp:
            soup = BeautifulSoup(fp, 'html.parser')

        matchup_df = pd.DataFrame(columns=["Team1", "Team1 Score", "Team2", "Team2 Score", "Winner"])
        matchup_data = soup.find_all('li')
        for i in range(6):
            team1 = matchup_data[i].find_all('a')[1].text
            team1_score = float(matchup_data[i].find_all('div')[11].text)
            team2 = matchup_data[i].find_all('a')[4].text
            team2_score = float(matchup_data[i].find_all('div')[18].text)
            winner = team2 if team2_score > team1_score else team1
            row = [team1, team1_score, team2, team2_score, winner]
            matchup_df.loc[len(matchup_df)] = row
        return matchup_df
    except:
        print("issue creating df for week ", week)
        return
        

def convert_detailed_matchup_to_df(week, i) -> None | pd.DataFrame:
    '''covert each matchup (matchup_{i}.html) to a user friendly csv table'''
    try:
        with open(F'matchup_data/week{week}/matchup_{i}.html') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        matchup_header = soup.find("section", {"id": "matchup-header"})
        # (TODO) This is fragile... fix!
        if week < 6:
            team1 = matchup_header.find_all('div')[6].text
            team2 = matchup_header.find_all('div')[19].text
        else:
            team1 = matchup_header.find_all('div')[5].text
            team2 = matchup_header.find_all('div')[17].text
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
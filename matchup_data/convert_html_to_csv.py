from bs4 import BeautifulSoup
import pandas as pd
import os

# User Input
WEEK = 1

class Player:
    '''Placeholder for a Player class to be used with the to be created Roster class'''
    def __init__(self, name, position, fan_pts):
        self.name = name
        self.position = position
        self.fan_pts = fan_pts

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

def convert_league_matchup_table_to_csv():
    '''convert week{WEEK}_matchups.html to a user friendly csv that shows all the league matchups as a summary'''
    if os.path.exists(f"matchup_data/week{WEEK}/matchups.csv"):
            print(f"csv for matchups already exists")
    else:
        try:
            with open(F'matchup_data/week{WEEK}/week{WEEK}_matchups.html') as fp:
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
            matchup_df.to_csv(f"matchup_data/week{WEEK}/matchup.csv")
            print("created matchups csv")
        except:
            print(f"Week {WEEK} matchups html not available")
        

def extract_position(text):
    '''function that extracts the position from Yahoo player html'''
    try:
        text = text.split("-")[1].split(" ")[1]
    except:
        pass
    return text

def clean_matchup_df(df):
    '''cleans up the Yahoo html table by removing unneeded columns and linting player data'''
    df.drop(['Stats', 'Stats.1'], axis=1, inplace=True)
    df["Position"] = df["Player"].apply(lambda x: extract_position(x))
    df["Player"] = df["Player"].apply(lambda x: str(x).split("-")[0])
    df["Position.1"] = df["Player.1"].apply(lambda x: extract_position(x))
    df["Player.1"] = df["Player.1"].apply(lambda x: str(x).split("-")[0])
    return df

def convert_detailed_matchup_to_csv():
    '''covert each matchup (matchup_{i}.html) to a user friendly csv table'''
    for i in range(1,7):
        if os.path.exists(f"matchup_data/week{WEEK}/matchup_{i}.csv"):
            print(f"csv for week {WEEK} matchup {i} already exists")
            continue
        else:
           try:
            with open(F'matchup_data/week{WEEK}/matchup_{i}.html') as fp:
                soup = BeautifulSoup(fp, 'html.parser')

            matchup_header = soup.find("section", {"id": "matchup-header"})
            team1 = matchup_header.find_all('div')[6].text
            team2 = matchup_header.find_all('div')[19].text
            
            matchup_df = pd.read_html(f'matchup_data/week{WEEK}/matchup_1.html')
            starter_matchup_df = clean_matchup_df(matchup_df[1])
            bench_matchup_df = clean_matchup_df(matchup_df[2])
            combined_df = pd.concat([starter_matchup_df, bench_matchup_df], ignore_index=True)
            combined_df = combined_df.rename(columns={"Player": team1, "Player.1": team2, "Pos": "Roster Pos"})
            combined_df[[team1, "Position", "Fan Pts", "Roster Pos", "Fan Pts.1", "Position.1", team2]].to_csv(f"matchup_data/week{WEEK}/matchup_{i}.csv")
            print(f"created csv for matchup {i}")
           except:
            print(f"Week {WEEK} matchup {i} html not available")

def main():
    convert_league_matchup_table_to_csv()
    convert_detailed_matchup_to_csv()

if __name__ == "__main__":
    main()
from bs4 import BeautifulSoup
import pandas as pd

# User Input
WEEK = 1

with open(F'matchup_data/week{WEEK}/week{WEEK}_matchup.html') as fp:
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
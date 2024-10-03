import streamlit as st
from convert_html_to_csv import convert_league_matchup_table_to_df, convert_detailed_matchup_to_df, League, Roster, MatchUp
from bs4 import BeautifulSoup
import pandas as pd

def convert_detailed_matchup_to_df_test(week, i):
    '''covert each matchup (matchup_{i}.html) to a user friendly csv table'''
    # try:
    with open(F'matchup_data/week{week}/matchup_{i}.html') as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    matchup_header = soup.find("section", {"id": "matchup-header"})
    team1 = matchup_header.find_all('div')[6].text
    team2 = matchup_header.find_all('div')[19].text
    print(team1, team2)
    print(f'matchup_data/week{week}/matchup_{i}.html')
    matchup_df = pd.read_html(f'matchup_data/week{week}/matchup_{i}.html')
    print(matchup_df[1].head())
    team_1_roster = Roster(team1, matchup_df[1].iloc[:,1:4], matchup_df[2].iloc[:,1:4])
    team_2_cols = ["Player.1", "Proj.1", "Fan Pts.1"]
    team_2_roster = Roster(team2, matchup_df[1][team_2_cols], matchup_df[2][team_2_cols])
    matchup = MatchUp(team_1_roster, team_2_roster)
    return matchup
    # except:
    #     print("issue creating df for week", week, " matchup", i)
    #     return
def get_teams_from_league_summary(league_summary):
    left_teams = league_summary["Team1"].tolist()
    right_teams = league_summary["Team2"].tolist()
    return left_teams + right_teams

def get_team_name(name):
    '''team members change names over the season causing mismatches in stats, this function returns the most commonly used name from a team

    Another idea is to move to managers instead of team names, but then we have a problem with Eric.
    
    (TODO) NICK
    '''

st.set_page_config(page_title="Sunnyvale Dashboard", page_icon=":football:", layout="wide")

st.title(":football: Sunnyvale Dashboard")
st.markdown('<style>div.block-container{padding-top:4rem;}</style>', unsafe_allow_html=True)
md = "Welcome to the Sunnyvale Dashboard, your home for all the advanced Sunnyvale Fantasy Football advanced analytics"
st.markdown(md)

# Create for Week
st.sidebar.header("Week")
week_list = ["All"] + [f"Week {x}" for x in range(1,5)]
week_str = st.sidebar.selectbox("Pick your Week", week_list, index=0)
try:    
    week = int(week_str[4:])
except:
    week = week_str

st.subheader("League Summary")

if week == "All":
    #stuff here
    pass
else:
    league_summary = convert_league_matchup_table_to_df(week)
    st.write(league_summary)

st.subheader("Advanced Analytics")
st.markdown("- PF Rank: Points scored compared to other teams \n - PA Rank: Points against compared to other teams \n - H2H: Record if you played every person this week \n - Manager Efficiency: TODO")

rosters = []

for i in range(1,7):
    # try:
    matchup = convert_detailed_matchup_to_df_test(week, i)
    print(matchup)
    rosters.append(matchup.team1_roster)
    rosters.append(matchup.team2_roster)
    # except:
    #     st.write("Issue grabbing matchup data, contact Nick Balavich")
    #     continue

league = League(rosters)
df = league.advanced_df
st.write(df)


    


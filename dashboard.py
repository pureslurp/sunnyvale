import streamlit as st
from convert_html_to_csv import convert_league_matchup_table_to_df, convert_detailed_matchup_to_df, Week, Season

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

weeks: list[Week] = []
for i in range(1,len(week_list)):
    matchups = []
    for j in range(1,7):
        matchups.append(convert_detailed_matchup_to_df(i, j))
    weeks.append(Week(matchups, week))

if week == "All":
    st.subheader("League Summary")
    st.write("Data for all weeks shown below, select a week from the left pane to dive deeper into a specific week")
    season = Season(weeks)
    st.write(season.season_summary_df)
else:
    st.subheader(f"Week {week}", divider=True)
    st.subheader("League Summary")
    league_summary = convert_league_matchup_table_to_df(week)
    st.write(league_summary)

    st.subheader("Advanced Analytics")
    st.markdown("- PF Rank: Points scored compared to other teams \n - PA Rank: Points against compared to other teams \n - H2H: Record if you played every person this week \n - Manager Efficiency: TODO")

    league = weeks[week-1]
    df = league.advanced_df
    st.write(df)


    


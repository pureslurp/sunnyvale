import streamlit as st
from convert_html_to_csv import convert_league_matchup_table_to_df, convert_detailed_matchup_to_df
from fantasy_objects import Season, Week
import plotly.express as px
import pandas as pd

WEEK = 14

def get_weeks(week) -> list[Week]:
    '''Returns all the week data up to a given week'''
    weeks: list[Week] = []
    for i in range(1,week):
        matchups = []
        for j in range(1,7):
            matchups.append(convert_detailed_matchup_to_df(i, j))
        weeks.append(Week(matchups, i))
    return weeks

def get_teams_from_league_summary(league_summary: pd.DataFrame):
    '''Returns all the teams from a league dataframe'''
    left_teams = league_summary["Team1"].tolist()
    right_teams = league_summary["Team2"].tolist()
    return left_teams + right_teams

def boxplot(position="All"):
    '''Writes a boxplot to streamlit app for a given position'''
    df = season.get_pf_data_for_boxplot_df(position)
    st.write(f"{position} 'Points For' Boxplot")
    fig = px.box(df, x='Team', y='Points For')
    st.plotly_chart(fig, key=f"{position} Points For")

@st.cache_data
def load_data(number_of_weeks):
    return get_weeks(number_of_weeks)

def get_team_name(name):
    '''team members change names over the season causing mismatches in stats, this function returns the most commonly used name from a team

    Another idea is to move to managers instead of team names, but then we have a problem with Eric.
    
    (TODO) NICK
    '''

st.set_page_config(page_title="Sunnyvale Dashboard", page_icon=":football:", layout="wide")

st.title(":football: Sunnyvale Dashboard")
st.markdown('<style>div.block-container{padding-top:4rem;}</style>', unsafe_allow_html=True)
md = "Welcome to the Sunnyvale Dashboard, your home for all the Sunnyvale Fantasy Football advanced analytics"
st.markdown(md)
# Create for Week
st.sidebar.header("Week")
week_list = ["All"] + [f"Week {x}" for x in range(1,WEEK+1)]
week_str = st.sidebar.selectbox("Pick your Week", week_list, index=0)
try:    
    week = int(week_str[4:])
except:
    week = week_str

weeks = load_data(len(week_list))

if week == "All":
    st.header("League Summary")
    st.write("Data for all weeks shown below, select a week from the left pane to dive deeper into a specific week")
    st.write("- **H2H**: Record if you played every person every week \n - **Power Rankings**: Team power rankings are based on a proprietary calculation that encompasses all the dynamics that make a great fantasy team \n - **PaP**: The average Points above Projected a team scores every week\n - **Manager Efficiency**: What you scored divided by the potential points you could have scored if you would have played the best players every week\n - **Proj Record**: Your record based on your power ranking and the remaining schedule")
    season = Season(weeks)
    st.dataframe(season.season_summary_df, hide_index=True)
    st.caption("- :fire: / :snowflake:: One of the three top/lowest scorers the last three weeks\n - -p: clinched playoffs")
    st.header("Position Rankings")
    st.write("Scoring of each position compared to other league members")
    st.dataframe(season.position_ranking_df, hide_index=True)
    st.subheader("Boxplots")
    st.write("A boxplot representation of the points scored per week for a given position")
    boxplot()
    boxplot("WR")
    boxplot("RB")
    boxplot("TE")
    boxplot("FLEX")
else:
    st.subheader(f"Week {week}", divider=True)
    st.subheader("League Summary")
    league_summary = convert_league_matchup_table_to_df(week)
    st.write(league_summary)

    st.subheader("Advanced Analytics")
    st.markdown("- H2H: Record if you played every person this week \n - Manager Efficiency: TODO")

    league = weeks[week-1]
    df = league.advanced_df
    st.dataframe(df, hide_index=True)
    st.subheader("Position Rankings")
    st.write("Scoring of each position compared to other league members")
    st.dataframe(league.get_position_ranks, hide_index=True)


    


import streamlit as st
from convert_html_to_csv import convert_league_matchup_table_to_df, get_weeks, Season
import plotly.express as px

def get_teams_from_league_summary(league_summary):
    left_teams = league_summary["Team1"].tolist()
    right_teams = league_summary["Team2"].tolist()
    return left_teams + right_teams

def boxplot(position="All"):
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
week_list = ["All"] + [f"Week {x}" for x in range(1,5)]
week_str = st.sidebar.selectbox("Pick your Week", week_list, index=0)
try:    
    week = int(week_str[4:])
except:
    week = week_str

weeks = load_data(len(week_list))

if week == "All":
    st.header("League Summary")
    st.write("Data for all weeks shown below, select a week from the left pane to dive deeper into a specific week")
    st.write("- H2H: Record if you played every person every week \n - Manager Efficiency: TODO\n - Power Rankings: Team power rankings are based on a proprietary calculation that encompasses all the dynamics that make a great fantasy team")
    season = Season(weeks)
    st.dataframe(season.season_summary_df)
    st.header("Position Rankings")
    st.write("- RB Rank: Average scoring of your RBs every week compared to other league members\n - WR Rank: Average scoring of your WRs every week compared to other league members\n  - TE Rank: Average scoring of your TEs every week compared to other league members\n - FLEX Rank: Average scoring of your FLEXs every week compared to other league members")
    st.dataframe(season.position_ranking_df)
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
    st.markdown("- PF Rank: Points scored compared to other teams \n - PA Rank: Points against compared to other teams \n - H2H: Record if you played every person this week \n - Manager Efficiency: TODO")

    league = weeks[week-1]
    df = league.advanced_df
    st.write(df)


    


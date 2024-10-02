import streamlit as st
# import pandas as pd
# import altair as alt
# from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode, ColumnsAutoSizeMode

st.set_page_config(page_title="Sunnyvale Dashboard", page_icon=":football:", layout="wide")

st.title(":football: Sunnyvale Dashboard")
st.markdown('<style>div.block-container{padding-top:4rem;}</style>', unsafe_allow_html=True)
md = "Welcome to the Sunnyvale Dashboard, your home for all the advanced Sunnyvale Fantasy Football advanced analytics"
st.markdown(md)

st.subheader(f"League Summary")

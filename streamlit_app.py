import numpy as np
import pandas as pd 
import altair as alt 
import streamlit as st


st.title("Github Actions Explorer")
st.write("This is the average number of hours that each project takes.")

df = pd.read_csv("all.csv").assign(time_taken = lambda d: d['time_taken']/60/60)

select_org = st.sidebar.multiselect(
    "Select Organisation",
    list(df['org'].unique())
)

select_repo = st.sidebar.multiselect(
    "Select Repository",
    list(df.loc[lambda d: d['org'].isin(select_org)]['repo'].unique()),
    default=list(df.loc[lambda d: d['org'].isin(select_org)]['repo'].unique())
)

select_flow = st.sidebar.multiselect(
    "Select Workflow",
    list(df.loc[lambda d: d['repo'].isin(select_repo)]['workflow'].unique()),
    default=list(df.loc[lambda d: d['repo'].isin(select_repo)]['workflow'].unique()),
)

if not select_org:
    y_col = 'org'
    source = (df
        .groupby(['org'])
        .agg({'time_taken': 'sum', 'date': 'nunique'})
        .assign(hrs_per_day=lambda d: d['time_taken']/d['date'])
        .reset_index()
        .sort_values("hrs_per_day"))

    bars_repo = alt.Chart(source).mark_bar().encode(
        x='hrs_per_day:Q',
        y=alt.Y(f"{y_col}:O", sort="-x")
    )

    st.write(bars_repo.properties(height=600, width=600))


if select_flow:
    source_repo = (df
            .loc[lambda d: d['org'].isin(select_org)]
            .groupby(['org', 'repo', 'workflow'])
            .agg({'time_taken': 'sum', 'date': 'nunique'})
            .reset_index()
            .assign(hrs_per_day=lambda d: d['time_taken']/d['date'],
                    workflow=lambda d: d['org'] + '-' + d['repo'] + '-' + d['workflow'])
            .sort_values("hrs_per_day"))
    
    bars_wkfl = alt.Chart(source_repo).mark_bar().encode(
        x='hrs_per_day:Q',
        y=alt.Y("workflow:O", sort="-x")
    )

    st.write(bars_wkfl.properties(height=300, width=600))

    source_wkfl = (df
            .loc[lambda d: d['org'].isin(select_org)]
            .loc[lambda d: d['repo'].isin(select_repo)]
            .groupby(['org', 'repo', 'date'])
            .agg({'time_taken': 'sum'})
            .reset_index()
            .assign(hrs_per_day=lambda d: d['time_taken'],
                    workflow=lambda d: d['org'] + '-' + d['repo'])
            .sort_values("hrs_per_day"))

    total_workflow_chart = alt.Chart(source_wkfl).mark_line(interpolate='step-after').encode(
        x='date:T',
        y='hrs_per_day',
        color='workflow',
    ).properties(title="Overview of Repo")

    source_wkfl = (df
            .loc[lambda d: d['org'].isin(select_org)]
            .loc[lambda d: d['repo'].isin(select_repo)]
            .loc[lambda d: d['workflow'].isin(select_flow)]
            .groupby(['org', 'repo', 'workflow', 'date'])
            .agg({'time_taken': 'sum'})
            .reset_index()
            .assign(hrs_per_day=lambda d: d['time_taken'],
                    workflow=lambda d: d['repo'] + '-' + d['workflow'])
            .sort_values("hrs_per_day"))

    bars_wkfl = alt.Chart(source_wkfl).mark_line(interpolate='step-after').encode(
        x='date:T',
        y='hrs_per_day',
        color='workflow',
    ).properties(title="Overview of Workflow")

    chart = (total_workflow_chart & bars_wkfl)
    st.write(chart)

import numpy as np
import pandas as pd 
import altair as alt 
import streamlit as st


st.title("Github Actions Explorer")

daymap = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}


df = (
    pd.read_csv("all.csv")
      .assign(time_taken = lambda d: d['time_taken_total']/60/60,
              day_of_week = lambda d: pd.to_datetime(d['date']).dt.day_of_week.map(daymap))
)

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

outlier_slider = st.sidebar.slider("Outlier Filter", min_value=95, max_value=100, value=99)

st.sidebar.markdown("**Like what you see?**")
st.sidebar.markdown("Find us on [Github](https://github.com/koaning/gitlit)! You can let us know if there are public repos missing by submitting an issue.")

if not select_org:
    st.write("We're keeping track of a few GitHub orgs. Below you can see how they compare in terms of how long their actions ran.")
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
    st.write("You can drill down by selecting an organisation on the sidebar.")


if select_flow:
    st.write("Here's a list of all the workflows that are running in the current org. Note that in the sidebar we've selected all known repositories. You can turn some off if you like.")
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

    st.write("The next chart shows the total Github actions time per date.")

    source_wkfl = (df
            .loc[lambda d: d['org'].isin(select_org)]
            .loc[lambda d: d['repo'].isin(select_repo)]
            .groupby(['org', 'repo', 'date', 'day_of_week'])
            .agg({'time_taken': 'sum'})
            .reset_index()
            .assign(hrs_per_day=lambda d: d['time_taken'],
                    workflow=lambda d: d['org'] + '-' + d['repo'])
            .sort_values("hrs_per_day"))

    total_workflow_chart = alt.Chart(source_wkfl).mark_line(interpolate='step-after').encode(
        x='date:T',
        y='hrs_per_day',
        color=alt.Color('workflow', legend=None),
        tooltip=['date', 'day_of_week', 'hrs_per_day']
    ).properties(title="Github actions time per date.")

    source_wkfl = (df
            .loc[lambda d: d['org'].isin(select_org)]
            .loc[lambda d: d['repo'].isin(select_repo)]
            .loc[lambda d: d['workflow'].isin(select_flow)]
            .groupby(['org', 'repo', 'workflow', 'date', 'day_of_week'])
            .agg({'time_taken': 'sum', 
                  'time_taken_q25': 'mean',
                  'time_taken_q50': 'mean',
                  'time_taken_q75': 'mean'})
            .reset_index()
            .assign(hrs_per_day=lambda d: d['time_taken'],
                    workflow=lambda d: d['repo'] + '-' + d['workflow'])
            .sort_values("hrs_per_day")
            .assign(date_str=lambda d: [str(t) for t in d['date']])
            .loc[lambda d: d['time_taken_q50'] <= np.percentile(d['time_taken_q50'], outlier_slider)])

    
    bars_wkfl = alt.Chart(source_wkfl).mark_line(interpolate='step-after').encode(
        x='date:T',
        y='time_taken_q50',
        color=alt.Color('workflow', legend=None),
        tooltip=['date_str', 'day_of_week', 'time_taken_q25', 'time_taken_q50', 'time_taken_q75', 'org', 'repo', 'workflow']
    ).properties(title="Average Time Taken per Day/Workflow").interactive()

    st.altair_chart(total_workflow_chart, use_container_width=True)
    
    st.write("This next chart shows the median time taken per workflow run. This can be useful to pinpoint when an expensive test was added.")
    
    st.altair_chart(bars_wkfl, use_container_width=True)


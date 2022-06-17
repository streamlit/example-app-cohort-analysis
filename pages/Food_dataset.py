import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly.graph_objs as go

# The code below is for the title and logo for this page.
st.set_page_config(page_title="Cohort for Food dataset", page_icon="🥡")

st.image(
    "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/325/takeout-box_1f961.png",
    width=160,
)

st.title("Cohort Analysis → `Food` dataset")

st.write("")

st.markdown(
    """

"""
)
st.markdown(
    """

    This demo is inspired by this [Cohort Analysis Tutorial](http://www.gregreda.com/2015/08/23/cohort-analysis-with-python/) 👉 [[Relay Food dataset]](https://github.com/springcoil/marsmodelling/blob/master/relay-foods.xlsx)

"""
)
st.markdown(
    """
    It calculates the `retention rate` (the percentage of active customers compared to the total number of customers, split by month). This `retention rate` is then visualized and interpreted through a heatmap.
"""
)

st.write("")

# loading dataset XLSX
df = pd.read_excel("datasets/relay-foods.xlsx", sheet_name=1)

df["OrderPeriod"] = df.OrderDate.apply(lambda x: x.strftime("%Y-%m"))
df.set_index("UserId", inplace=True)

df["CohortGroup"] = (
    df.groupby(level=0)["OrderDate"].min().apply(lambda x: x.strftime("%Y-%m"))
)
df.reset_index(inplace=True)
# df.head()

# loading dataset CSV
relay_foods_csv = pd.read_csv("datasets/relay-foods.csv")

with st.expander("Show the `Relay Food Transactions` dataframe"):
    st.write(relay_foods_csv)

grouped = df.groupby(["CohortGroup", "OrderPeriod"])

# count the unique users, orders, and total revenue per Group + Period
cohorts = grouped.agg(
    {"UserId": pd.Series.nunique, "OrderId": pd.Series.nunique, "TotalCharges": np.sum}
)

# make the column names more meaningful
cohorts.rename(columns={"UserId": "TotalUsers", "OrderId": "TotalOrders"}, inplace=True)
cohorts.head()


def cohort_period(df):
    """
    Creates a `CohortPeriod` column, which is the Nth period based on the user's first purchase.

    """
    df["CohortPeriod"] = np.arange(len(df)) + 1
    return df


with st.form("my_form"):
    # st.write("Inside the form")
    # slider_val = st.slider("Form slider")
    # checkbox_val = st.checkbox("Form checkbox")

    cole, col1, cole = st.columns([0.1, 1, 0.1])

    with col1:

        TotalCharges_slider = st.slider(
            "Total Charges (in $)", step=50, min_value=2, max_value=690
        )
        # Every form must have a submit button.

    submitted = st.form_submit_button("Refine results")

# st.write("slider", slider_val, "checkbox", checkbox_val)

cohorts = cohorts[cohorts["TotalCharges"] > TotalCharges_slider]

cohorts = cohorts.groupby(level=0).apply(cohort_period)
cohorts.head()

# reindex the DataFrame
cohorts.reset_index(inplace=True)
cohorts.set_index(["CohortGroup", "CohortPeriod"], inplace=True)

# create a Series holding the total size of each CohortGroup
cohort_group_size = cohorts["TotalUsers"].groupby(level=0).first()
cohort_group_size.head()

user_retention = cohorts["TotalUsers"].unstack(0).divide(cohort_group_size, axis=1)
user_retention.head(10)

user_retention[["2009-06", "2009-07", "2009-08"]].plot(figsize=(10, 5))
plt.title("Cohorts: User Retention")
plt.xticks(np.arange(1, 12.1, 1))
plt.xlim(1, 12)
plt.ylabel("% of Cohort Purchasing")
cohorts["TotalUsers"].head()

user_retention = cohorts["TotalUsers"].unstack(0).divide(cohort_group_size, axis=1)
user_retention.head(10)

user_retention[["2009-06", "2009-07", "2009-08"]].plot(figsize=(10, 5))
plt.title("Cohorts: User Retention")
plt.xticks(np.arange(1, 12.1, 1))
plt.xlim(1, 12)
plt.ylabel("% of Cohort Purchasing")

user_retention = user_retention.T

fig = go.Figure()

fig.add_heatmap(
    x=user_retention.columns,
    y=user_retention.index,
    z=user_retention,
    # colorscale="Reds",
    # colorscale="Sunsetdark",
    colorscale="Redor"
    # colorscale="Viridis",
)

fig.update_layout(title_text="Monthly cohorts showing retention rates", title_x=0.5)
fig.layout.xaxis.title = "Cohort Group"
fig.layout.yaxis.title = "Cohort Period"
fig["layout"]["title"]["font"] = dict(size=25)
fig.layout.plot_bgcolor = "#efefef"  # Set the background color to white
fig.layout.width = 750
fig.layout.height = 750
fig.layout.xaxis.tickvals = user_retention.columns
fig.layout.yaxis.tickvals = user_retention.index
fig.layout.margin.b = 100
fig

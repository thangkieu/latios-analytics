import json
import streamlit as st
import pandas as pd
import random
import numpy as np

st.set_page_config(layout="wide", page_title="LaunchPad Analytics")


uploaded_file = st.sidebar.file_uploader("Upload your Latios database")
if uploaded_file is None:
    st.stop()


def trans_date(d):
    try:
        date = json.loads(d)
        return pd.to_datetime(date[0]["S"])
    except Exception as e:
        print(f"Error str {d} {e}")
        return None


# columns
#   |__ hash_id
#   |__ activation_count
#   |__ activations
#   |__ application_name
#   |__ label
#   |__ label2
#   |__ label3
#   |__ label4
#   |__ original_url
ori_df = pd.read_csv(uploaded_file, encoding_errors="replace")

mult_count_df = ori_df.query("activation_count > 1")
new_row = 0
for idx, item in mult_count_df.iterrows():
    activations_str = item["activations"]
    activations = json.loads(activations_str) if activations_str else []

    new_list = []
    for date_obj in activations:
        item["activations"] = json.dumps([date_obj])
        item["activation_count"] = 1

        ori_df = ori_df.append(item.to_dict(), ignore_index=True)


# Add created_at because original database doesn"t store this value
# Will remove it later
ori_df = ori_df.loc[ori_df["activation_count"] == 1]
ori_df = ori_df.reset_index()
ori_df = ori_df.drop(columns=["index"])
ori_df["created_at"] = ori_df["activations"].transform(trans_date)

# Controls
control1, control2 = st.columns(2)
from_date = None
to_date = None

with control1:
    app = st.selectbox("Select Application",
                       ori_df["application_name"].unique().tolist())
with control2:
    dates = st.date_input("From Date", value=())
    from_date = dates[0] if len(dates) > 0 else None
    to_date = dates[1] if len(dates) > 1 else None


app_df = ori_df.query("application_name == @app")
mask = None
if from_date:
    mask = (app_df["created_at"] >= pd.Timestamp(from_date))
if to_date:
    mask = mask & (app_df["created_at"] <= pd.Timestamp(to_date))

if mask is not None:
    app_df = app_df.loc[mask]

# Main Page
tab1, tab2 = st.tabs(["Data", "Charts"])

with tab1:
    st.write(app_df)

with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.caption("All Events")
        df3 = app_df.groupby("label")['activation_count'].count()

        st.line_chart(df3, y="activation_count")
        st.write(df3)
    with col2:
        option = st.selectbox(
            "Select Event Type:", app_df["label"].unique().tolist())

        event_details = app_df.query("label == @option")

        event_details_group = event_details.groupby(
            "label2")['activation_count'].count()
        st.line_chart(event_details_group, y="activation_count")
        st.write(event_details_group)

lines = app_df['label'].unique()
dates = app_df['created_at'].map(lambda t: t.date()).unique()

chart_series = app_df.groupby([pd.Grouper(key='created_at', freq='2D'), 'label'])[
    "activation_count"].count()

series_data = []
sample_row = {'created_at': None}
sample_data = random.sample(range(0, 100), len(lines))


for grouped, count in chart_series.items():
    date, line = grouped
    data = {}
    data['created_at'] = date

    # for idx, line in enumerate(lines):
    #     data[line] = random.randint(0, 100)

    data[line] = count
    series_data.append(data)

print(series_data)

series_df = pd.DataFrame(series_data)

# st.line_chart(series_df, x="created_at")
# st.write(series_df)

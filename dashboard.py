"""
F1 Telemetry Dashboard (Streamlit)
------------------------------------
Interactive version of telemetry_analysis.py — pick any race/session/drivers
from the browser instead of editing the script.

Run:  streamlit run dashboard.py
"""

import streamlit as st
import fastf1
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

st.set_page_config(page_title="F1 Telemetry Dashboard", layout="wide")
st.title("🏎️ F1 Telemetry Analysis Dashboard")

# ---------------- Sidebar controls ----------------
with st.sidebar:
    st.header("Session")
    year = st.selectbox("Year", [2024, 2023, 2022, 2021], index=0)
    gp = st.text_input("Grand Prix", "Monza")
    session_type = st.selectbox("Session", ["Q", "R", "FP1", "FP2", "FP3"], index=0)
    load_btn = st.button("Load Session", type="primary")

if "session" not in st.session_state:
    st.session_state.session = None

if load_btn:
    with st.spinner(f"Loading {year} {gp} {session_type}..."):
        s = fastf1.get_session(year, gp, session_type)
        s.load()
        st.session_state.session = s

session = st.session_state.session

if session is None:
    st.info("Set your race in the sidebar and hit **Load Session** to begin.")
    st.stop()

drivers = session.laps["Driver"].unique().tolist()
col1, col2 = st.columns(2)
drv1 = col1.selectbox("Driver 1", drivers, index=0)
drv2 = col2.selectbox("Driver 2", drivers, index=1 if len(drivers) > 1 else 0)

lap1 = session.laps.pick_driver(drv1).pick_fastest()
lap2 = session.laps.pick_driver(drv2).pick_fastest()
tel1 = lap1.get_car_data().add_distance()
tel2 = lap2.get_car_data().add_distance()

tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Speed Trace", "Braking Points", "Gear/Throttle", "Micro-Sector Map", "Lap Times"]
)

with tab1:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(tel1["Distance"], tel1["Speed"], label=f"{drv1} ({lap1['LapTime']})")
    ax.plot(tel2["Distance"], tel2["Speed"], label=f"{drv2} ({lap2['LapTime']})")
    ax.set_xlabel("Distance (m)"); ax.set_ylabel("Speed (km/h)"); ax.legend()
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(tel1["Distance"], tel1["Brake"].astype(int), label=drv1, drawstyle="steps-post")
    ax.plot(tel2["Distance"], tel2["Brake"].astype(int), label=drv2, drawstyle="steps-post")
    ax.set_xlabel("Distance (m)"); ax.set_ylabel("Brake (0/1)"); ax.legend()
    st.pyplot(fig)

with tab3:
    fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True)
    axes[0].plot(tel1["Distance"], tel1["nGear"], color="darkorange")
    axes[0].set_ylabel("Gear")
    axes[1].plot(tel1["Distance"], tel1["Throttle"], color="green")
    axes[1].set_ylabel("Throttle (%)"); axes[1].set_xlabel("Distance (m)")
    st.pyplot(fig)

with tab4:
    n_sectors = st.slider("Number of micro-sectors", 10, 50, 25)
    max_dist = min(tel1["Distance"].max(), tel2["Distance"].max())
    bins = np.linspace(0, max_dist, n_sectors + 1)

    def avg_speed_per_bin(tel):
        t = tel.copy()
        t["bin"] = pd.cut(t["Distance"], bins)
        return t.groupby("bin", observed=True)["Speed"].mean()

    s1, s2 = avg_speed_per_bin(tel1), avg_speed_per_bin(tel2)
    faster = np.where(s1.values > s2.values, 1, 2)
    colors = ["#1f77b4" if f == 1 else "#d62728" for f in faster]
    fig, ax = plt.subplots(figsize=(11, 2))
    ax.bar(range(len(faster)), [1] * len(faster), color=colors, width=1.0)
    ax.set_yticks([]); ax.set_title(f"Blue: {drv1} | Red: {drv2}")
    st.pyplot(fig)

with tab5:
    fig, ax = plt.subplots(figsize=(11, 6))
    for drv in [drv1, drv2]:
        laps = session.laps.pick_driver(drv).pick_quicklaps()
        if not laps.empty:
            ax.plot(laps["LapNumber"], laps["LapTime"].dt.total_seconds(), marker="o", label=drv)
    ax.set_xlabel("Lap Number"); ax.set_ylabel("Lap Time (s)"); ax.legend()
    st.pyplot(fig)

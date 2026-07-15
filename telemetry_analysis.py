"""
F1 Telemetry Analysis
----------------------
Pulls real car telemetry (speed, throttle, brake, gear, RPM) from the
FastF1 API and produces 5 driver-performance visualizations.

Run:  python telemetry_analysis.py
"""

import fastf1
import fastf1.plotting
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

# ---------------------------------------------------------
# CONFIG — change these to analyze any race since ~2018
# ---------------------------------------------------------
YEAR = 2024
GP = "Monza"
SESSION_TYPE = "Q"          # 'FP1','FP2','FP3','Q','R'
DRIVER_1 = "VER"
DRIVER_2 = "NOR"

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)
fastf1.plotting.setup_mpl(misc_mpl_mods=False)


# ---------------------------------------------------------
# 1. LOAD SESSION
# ---------------------------------------------------------
def load_session():
    session = fastf1.get_session(YEAR, GP, SESSION_TYPE)
    session.load()
    return session


# ---------------------------------------------------------
# 2. SPEED TRACE COMPARISON
# ---------------------------------------------------------
def speed_trace_comparison(session, drv1, drv2):
    lap1 = session.laps.pick_driver(drv1).pick_fastest()
    lap2 = session.laps.pick_driver(drv2).pick_fastest()

    tel1 = lap1.get_car_data().add_distance()
    tel2 = lap2.get_car_data().add_distance()

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(tel1["Distance"], tel1["Speed"], label=f"{drv1} ({lap1['LapTime']})")
    ax.plot(tel2["Distance"], tel2["Speed"], label=f"{drv2} ({lap2['LapTime']})")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Speed (km/h)")
    ax.set_title(f"{drv1} vs {drv2} — Fastest Lap Speed Trace | {GP} {YEAR} {SESSION_TYPE}")
    ax.legend()
    fig.tight_layout()
    fig.savefig("1_speed_trace.png", dpi=150)
    plt.close(fig)
    return lap1, lap2, tel1, tel2


# ---------------------------------------------------------
# 3. BRAKING POINT DETECTION
# ---------------------------------------------------------
def braking_points(tel1, tel2, drv1, drv2):
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(tel1["Distance"], tel1["Brake"].astype(int), label=drv1, drawstyle="steps-post")
    ax.plot(tel2["Distance"], tel2["Brake"].astype(int), label=drv2, drawstyle="steps-post")
    ax.set_xlabel("Distance (m)")
    ax.set_ylabel("Brake (0=off, 1=on)")
    ax.set_title(f"Braking Points Comparison | {GP} {YEAR}")
    ax.legend()
    fig.tight_layout()
    fig.savefig("2_braking_points.png", dpi=150)
    plt.close(fig)

    # quantify: distance into lap where each first brakes for each detected zone
    def brake_zones(tel):
        braking = tel[tel["Brake"] == True]
        # group consecutive braking points into zones
        gaps = braking["Distance"].diff().fillna(999) > 50
        zone_id = gaps.cumsum()
        return braking.groupby(zone_id)["Distance"].min().reset_index(drop=True)

    zones1 = brake_zones(tel1)
    zones2 = brake_zones(tel2)
    print("\nBraking zone start distances (m):")
    print(f"  {drv1}: {list(zones1.round(0))}")
    print(f"  {drv2}: {list(zones2.round(0))}")


# ---------------------------------------------------------
# 4. GEAR & THROTTLE MAP
# ---------------------------------------------------------
def gear_throttle_map(tel1, drv1):
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    axes[0].plot(tel1["Distance"], tel1["nGear"], color="darkorange")
    axes[0].set_ylabel("Gear")
    axes[0].set_title(f"{drv1} — Gear & Throttle Map | {GP} {YEAR}")

    axes[1].plot(tel1["Distance"], tel1["Throttle"], color="green")
    axes[1].set_ylabel("Throttle (%)")
    axes[1].set_xlabel("Distance (m)")

    fig.tight_layout()
    fig.savefig("3_gear_throttle_map.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------
# 5. MICRO-SECTOR DOMINANCE MAP
# ---------------------------------------------------------
def microsector_dominance(tel1, tel2, drv1, drv2, n_sectors=25):
    max_dist = min(tel1["Distance"].max(), tel2["Distance"].max())
    bins = np.linspace(0, max_dist, n_sectors + 1)

    def avg_speed_per_bin(tel):
        tel = tel.copy()
        tel["bin"] = pd.cut(tel["Distance"], bins)
        return tel.groupby("bin", observed=True)["Speed"].mean()

    s1 = avg_speed_per_bin(tel1)
    s2 = avg_speed_per_bin(tel2)

    faster = np.where(s1.values > s2.values, 1, 2)  # 1 = drv1 faster, 2 = drv2 faster

    fig, ax = plt.subplots(figsize=(11, 2))
    colors = ["#1f77b4" if f == 1 else "#d62728" for f in faster]
    ax.bar(range(len(faster)), [1] * len(faster), color=colors, width=1.0)
    ax.set_yticks([])
    ax.set_xlabel("Micro-sector (track distance →)")
    ax.set_title(f"Micro-Sector Dominance — Blue: {drv1} | Red: {drv2}")
    fig.tight_layout()
    fig.savefig("4_microsector_dominance.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------
# 6. TIRE DEGRADATION & STRATEGY (needs a Race session)
# ---------------------------------------------------------
def tire_strategy(session, drivers):
    fig, ax = plt.subplots(figsize=(11, 6))
    for drv in drivers:
        laps = session.laps.pick_driver(drv).pick_quicklaps()
        if laps.empty:
            continue
        ax.plot(laps["LapNumber"], laps["LapTime"].dt.total_seconds(), marker="o", label=drv)
    ax.set_xlabel("Lap Number")
    ax.set_ylabel("Lap Time (s)")
    ax.set_title(f"Lap Time Evolution | {GP} {YEAR}")
    ax.legend()
    fig.tight_layout()
    fig.savefig("5_tire_strategy.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    print(f"Loading {YEAR} {GP} {SESSION_TYPE} session...")
    session = load_session()

    print("1/5 Speed trace comparison...")
    lap1, lap2, tel1, tel2 = speed_trace_comparison(session, DRIVER_1, DRIVER_2)

    print("2/5 Braking point detection...")
    braking_points(tel1, tel2, DRIVER_1, DRIVER_2)

    print("3/5 Gear & throttle map...")
    gear_throttle_map(tel1, DRIVER_1)

    print("4/5 Micro-sector dominance map...")
    microsector_dominance(tel1, tel2, DRIVER_1, DRIVER_2)

    if SESSION_TYPE == "R":
        print("5/5 Tire strategy / degradation...")
        tire_strategy(session, [DRIVER_1, DRIVER_2])
    else:
        print("5/5 Skipped tire strategy (needs SESSION_TYPE='R' — a race session)")

    print("\nDone! Check the .png files in this folder.")

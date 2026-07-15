# 🏎️ F1 Telemetry Analysis — Data Science Project

> Turning raw car telemetry (speed, throttle, brake, gear, RPM) into driver-performance insights using real Formula 1 timing data.

This is a **different beast** from your earlier F1 Race ML Dashboard — that one worked on race *results*. This one goes under the hood: **sensor-level telemetry**, the same data F1 engineers stare at on pit wall screens.

---

## 🎯 What This Project Proves (for your resume/portfolio)

| Skill | Where it shows up |
|---|---|
| API/data ingestion | Pulling live timing data via `FastF1` |
| Time-series analysis | Speed/throttle/brake traces over distance |
| Signal processing intuition | Braking point detection, corner analysis |
| Comparative analytics | Driver-vs-driver micro-sector dominance |
| Data storytelling | Visualizations that non-technical people instantly get |

**Resume bullet you can lift:**
> *"Built an F1 telemetry analysis pipeline using the FastF1 API to compare driver performance at sub-second resolution — identifying braking points, corner-speed deltas, and tire degradation patterns across a full Grand Prix weekend."*

---

## 🧰 Tech Stack

- **`fastf1`** — official-grade F1 timing/telemetry API wrapper (free)
- **Pandas / NumPy** — data wrangling
- **Matplotlib / Plotly** — visualization (Plotly if you want it interactive)
- **Streamlit** *(optional)* — turn it into a live dashboard like your last project

---

## 📂 Project Structure

```
f1-telemetry-analysis/
├── README.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── telemetry_analysis.py     # core analysis — generates 5 PNG charts
├── dashboard.py              # Streamlit interactive dashboard
├── animation.py              # generates lap_animation.gif
├── index.html                # project showcase webpage (deployable to GitHub Pages)
└── cache/                    # FastF1 auto-creates this — gitignored, don't delete locally
```

---

## 📤 Push to GitHub

```bash
cd f1-telemetry-analysis
git init
git add .
git commit -m "F1 telemetry analysis project"
git branch -M main
git remote add origin https://github.com/<your-username>/f1-telemetry-analysis.git
git push -u origin main
```

### Turn `index.html` into a live webpage (free, via GitHub Pages)
1. Push the repo (above)
2. On GitHub → **Settings → Pages**
3. Source: **Deploy from branch** → Branch: `main`, folder: `/ (root)` → Save
4. Your page goes live at `https://<your-username>.github.io/f1-telemetry-analysis/`

*(Takes ~1 minute to publish after the first push.)*

---

## 🪜 The 5 Analyses (in increasing difficulty)

### 1. Speed Trace Comparison
Overlay two drivers' fastest laps — speed vs. distance around the track. Instantly shows *where* one driver is faster.

### 2. Braking Point Detection
Find exact track distance where each driver hits the brakes into a corner. Late braking = aggressive/skilled driving. This is the single most "wow" chart in the project.

### 3. Gear & Throttle Map
Plot which gear + throttle % is used at every point on track — shows racing line and corner exit aggression.

### 4. Micro-Sector Dominance Map
Split the lap into ~25 mini-sectors, color the track by who was faster in each — this is literally what F1 broadcasts show live during quali.

### 5. Tire Degradation & Strategy
Lap time vs. lap number, colored by tire compound — shows stint length, degradation curve, undercut/overcut windows.

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python telemetry_analysis.py
```

First run downloads session data (~30–60s), then caches it locally — every run after that is instant.

Default config pulls **2024 Monza GP, Verstappen vs Norris, Qualifying**. Change `YEAR`, `GP`, `SESSION`, `DRIVER_1`, `DRIVER_2` at the top of the script to any race since ~2018.

---

## 💡 Ideas to Extend (great for "future work" section)

- Wrap it in **Streamlit** for an interactive dashboard (reuse your dashboard experience)
- Add a **corner-by-corner time-loss table** (quantify exactly how many ms lost per corner)
- Build a **"what-if" lap simulator**: splice sector 1 from Driver A with sector 3 from Driver B to estimate a theoretical best lap
- Compare **wet vs dry** sessions for the same driver

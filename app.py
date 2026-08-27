
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="Bird Species Observation Analysis Dashboard",
    page_icon="🐦",
    layout="wide"
)

FOREST_FILE = "Bird_Monitoring_Data_FOREST_CLEANED.xlsx"
GRASSLAND_FILE = "Bird_Monitoring_Data_GRASSLAND_CLEANED.xlsx"

@st.cache_data
def load_data():
    forest = pd.read_excel(FOREST_FILE)
    grassland = pd.read_excel(GRASSLAND_FILE)

    forest["Habitat"] = "Forest"
    grassland["Habitat"] = "Grassland"

    df = pd.concat([forest, grassland], ignore_index=True)

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Month"] = df["Date"].dt.month
        df["Month_Name"] = df["Date"].dt.strftime("%b")

    for col in ["Year", "Visit", "Temperature", "Humidity", "Distance"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

df = load_data()

st.title("🐦 Bird Species Observation Analysis Dashboard")
st.markdown(
    "Interactive EDA dashboard for **Forest and Grassland bird monitoring data**."
)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔎 Filters")

habitats = st.sidebar.multiselect(
    "Habitat",
    options=sorted(df["Habitat"].dropna().unique()),
    default=sorted(df["Habitat"].dropna().unique())
)

filtered = df[df["Habitat"].isin(habitats)].copy()

if "Year" in filtered.columns and filtered["Year"].notna().any():
    years = sorted(filtered["Year"].dropna().astype(int).unique())
    if len(years) > 1:
        year_range = st.sidebar.slider(
            "Year Range",
            min_value=min(years),
            max_value=max(years),
            value=(min(years), max(years))
        )
        filtered = filtered[
            filtered["Year"].between(year_range[0], year_range[1])
        ]

if "Common_Name" in filtered.columns:
    species_options = sorted(filtered["Common_Name"].dropna().unique())
    selected_species = st.sidebar.multiselect(
        "Bird Species",
        options=species_options,
        default=[]
    )
    if selected_species:
        filtered = filtered[
            filtered["Common_Name"].isin(selected_species)
        ]

# Numeric filters
if "Temperature" in filtered.columns and filtered["Temperature"].notna().any():
    tmin = float(filtered["Temperature"].min())
    tmax = float(filtered["Temperature"].max())
    if tmin < tmax:
        temp_range = st.sidebar.slider(
            "Temperature",
            min_value=tmin,
            max_value=tmax,
            value=(tmin, tmax)
        )
        filtered = filtered[
            filtered["Temperature"].between(*temp_range)
        ]

# ---------------- KPI CARDS ----------------
total_obs = len(filtered)
unique_species = filtered["Common_Name"].nunique() if "Common_Name" in filtered.columns else 0
unique_observers = filtered["Observer"].nunique() if "Observer" in filtered.columns else 0
avg_temp = filtered["Temperature"].mean() if "Temperature" in filtered.columns else np.nan
avg_humidity = filtered["Humidity"].mean() if "Humidity" in filtered.columns else np.nan

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Observations", f"{total_obs:,}")
c2.metric("Unique Species", f"{unique_species:,}")
c3.metric("Unique Observers", f"{unique_observers:,}")
c4.metric("Avg Temperature", f"{avg_temp:.1f}" if pd.notna(avg_temp) else "N/A")
c5.metric("Avg Humidity", f"{avg_humidity:.1f}" if pd.notna(avg_humidity) else "N/A")

st.divider()

# ---------------- DATA PREVIEW ----------------
with st.expander("📋 Dataset Preview"):
    st.write(f"Filtered records: **{len(filtered):,}**")
    st.dataframe(filtered.head(100), use_container_width=True)

# ---------------- CHART 1 ----------------
st.subheader("1. Observations by Habitat")
c = filtered["Habitat"].value_counts().reset_index()
c.columns = ["Habitat", "Observations"]
fig = px.bar(c, x="Habitat", y="Observations", title="Bird Observations by Habitat")
st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 2 ----------------
st.subheader("2. Observations by Year")
if "Year" in filtered.columns:
    c = filtered.dropna(subset=["Year"]).groupby("Year").size().reset_index(name="Observations")
    c["Year"] = c["Year"].astype(int)
    fig = px.bar(c, x="Year", y="Observations", title="Bird Observations by Year")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 3 ----------------
st.subheader("3. Top 15 Bird Species")
if "Common_Name" in filtered.columns:
    c = filtered["Common_Name"].value_counts().head(15).reset_index()
    c.columns = ["Common_Name", "Observations"]
    fig = px.bar(
        c.sort_values("Observations"),
        x="Observations",
        y="Common_Name",
        orientation="h",
        title="Top 15 Most Frequently Observed Bird Species"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 4 ----------------
st.subheader("4. Species Richness by Habitat")
c = filtered.groupby("Habitat")["Common_Name"].nunique().reset_index(name="Unique_Species")
fig = px.bar(c, x="Habitat", y="Unique_Species", title="Species Richness by Habitat")
st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 5 ----------------
st.subheader("5. Sex Distribution")
if "Sex" in filtered.columns:
    c = filtered["Sex"].value_counts().reset_index()
    c.columns = ["Sex", "Observations"]
    fig = px.pie(c, names="Sex", values="Observations", title="Bird Observations by Sex")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 6 ----------------
st.subheader("6. Identification Method")
if "ID_Method" in filtered.columns:
    c = filtered["ID_Method"].value_counts().reset_index()
    c.columns = ["ID_Method", "Observations"]
    fig = px.bar(c, x="ID_Method", y="Observations", title="Bird Identification Methods")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 7 ----------------
st.subheader("7. Temperature Distribution")
if "Temperature" in filtered.columns:
    fig = px.histogram(
        filtered.dropna(subset=["Temperature"]),
        x="Temperature",
        nbins=25,
        title="Temperature Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 8 ----------------
st.subheader("8. Humidity Distribution")
if "Humidity" in filtered.columns:
    fig = px.histogram(
        filtered.dropna(subset=["Humidity"]),
        x="Humidity",
        nbins=25,
        title="Humidity Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)



# ---------------- CHART 9 ----------------
st.subheader("9. Temperature by Habitat")
if "Temperature" in filtered.columns:
    fig = px.box(
        filtered.dropna(subset=["Temperature"]),
        x="Habitat",
        y="Temperature",
        title="Temperature Distribution by Habitat"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 10 ----------------
st.subheader("10. Humidity by Habitat")
if "Humidity" in filtered.columns:
    fig = px.box(
        filtered.dropna(subset=["Humidity"]),
        x="Habitat",
        y="Humidity",
        title="Humidity Distribution by Habitat"
    )
    st.plotly_chart(fig, use_container_width=True)



# ---------------- CHART 11 ----------------
st.subheader("11. Temperature vs Humidity")
if {"Temperature", "Humidity"}.issubset(filtered.columns):
    plot_df = filtered[["Temperature", "Humidity", "Habitat"]].dropna()
    fig = px.scatter(
        plot_df,
        x="Temperature",
        y="Humidity",
        color="Habitat",
        title="Temperature vs Humidity",
        opacity=0.55
    )
    st.plotly_chart(fig, use_container_width=True)





# ---------------- CHART 12 ----------------
st.subheader("12. Bird Observations by Year and Habitat")
if "Year" in filtered.columns:
    c = (
        filtered.dropna(subset=["Year"])
        .groupby(["Year", "Habitat"])
        .size()
        .reset_index(name="Observations")
    )
    c["Year"] = c["Year"].astype(int)
    fig = px.bar(
        c,
        x="Year",
        y="Observations",
        color="Habitat",
        barmode="group",
        title="Bird Observations by Year and Habitat"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 13 ----------------
st.subheader("13. Monthly Bird Observation Trend")
if "Month" in filtered.columns:
    c = filtered.dropna(subset=["Month"]).groupby("Month").size().reset_index(name="Observations")
    c["Month"] = c["Month"].astype(int)
    fig = px.line(
        c,
        x="Month",
        y="Observations",
        markers=True,
        title="Monthly Bird Observation Trend"
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 14 ----------------
st.subheader("14. Monthly Observations by Habitat")
if "Month" in filtered.columns:
    c = (
        filtered.dropna(subset=["Month"])
        .groupby(["Month", "Habitat"])
        .size()
        .reset_index(name="Observations")
    )
    c["Month"] = c["Month"].astype(int)
    fig = px.line(
        c,
        x="Month",
        y="Observations",
        color="Habitat",
        markers=True,
        title="Monthly Bird Observations by Habitat"
    )
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 15 ----------------
st.subheader("15. Sky Conditions")
if "Sky" in filtered.columns:
    c = filtered["Sky"].value_counts().head(10).reset_index()
    c.columns = ["Sky", "Observations"]
    fig = px.bar(c, x="Sky", y="Observations", title="Bird Observations by Sky Condition")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 16 ----------------
st.subheader("16. Wind Conditions")
if "Wind" in filtered.columns:
    c = filtered["Wind"].value_counts().head(10).reset_index()
    c.columns = ["Wind", "Observations"]
    fig = px.bar(c, x="Wind", y="Observations", title="Bird Observations by Wind Condition")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 17 ----------------
st.subheader("17. Disturbance Level")
if "Disturbance" in filtered.columns:
    c = filtered["Disturbance"].value_counts().head(10).reset_index()
    c.columns = ["Disturbance", "Observations"]
    fig = px.bar(c, x="Disturbance", y="Observations", title="Bird Observations by Disturbance Level")
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 18 ----------------
st.subheader("18. Flyover Observations by Habitat")
if "Flyover_Observed" in filtered.columns:
    c = (
        filtered.groupby(["Habitat", "Flyover_Observed"])
        .size()
        .reset_index(name="Observations")
    )
    c["Flyover_Observed"] = c["Flyover_Observed"].astype(str)
    fig = px.bar(
        c,
        x="Habitat",
        y="Observations",
        color="Flyover_Observed",
        barmode="group",
        title="Flyover Observations by Habitat"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 19 ----------------
st.subheader("19. Top 10 Species by Habitat")
if "Common_Name" in filtered.columns:
    top10 = filtered["Common_Name"].value_counts().head(10).index
    c = (
        filtered[filtered["Common_Name"].isin(top10)]
        .groupby(["Common_Name", "Habitat"])
        .size()
        .reset_index(name="Observations")
    )
    fig = px.bar(
        c,
        x="Common_Name",
        y="Observations",
        color="Habitat",
        barmode="group",
        title="Top 10 Bird Species by Habitat"
    )
    fig.update_xaxes(tickangle=45)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- CHART 20 ----------------
st.subheader("20. Correlation Heatmap")
numeric_cols = filtered.select_dtypes(include=np.number).columns
if len(numeric_cols) >= 2:
    corr = filtered[numeric_cols].corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        title="Correlation Matrix of Numerical Variables"
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------------- DOWNLOAD ----------------
st.divider()
st.subheader("⬇️ Download Filtered Data")

csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    label="Download Filtered Dataset as CSV",
    data=csv,
    file_name="bird_monitoring_filtered.csv",
    mime="text/csv"
)

st.caption("Bird Monitoring Analysis Dashboard | Forest + Grassland")

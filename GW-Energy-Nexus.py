#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import pandas as pd
import altair as alt
from altair import datum
import plotly.graph_objects as go


def main():

    ### Application Header
    st.title("Pakistan's Groundwater-Energy Nexus")
    st.markdown("## #RethinkingIndus")
    st.subheader("Impact of Subsidized Electric Tube-wells")

    st.markdown(
        """
        This is an interactive dashboard that allows users to understand the
        impact of groundwater extraction by subsidized private electric TubeWells (TW)
        on Pakistan’s water footprint.
        
        Annual electric GW extraction is estimated from agricultural electricity
        consumption. Users may change pump efficiency, extraction depth, and grid
        transmission losses to visualize impacts on groundwater pumping.
        """
    )

    ### Sidebar
    st.sidebar.title("Estimating Pumping")
    st.sidebar.markdown(
        """
        Pumping from electric tubewells is estimated using:
        
        **Volume = (Energy × eff × (1 − loss)) / (0.00273 × depth × 10⁶)**
        """
    )

    st.sidebar.markdown("## Parameters")

    depth = st.sidebar.slider("Depth to Water Table (m):", 30, 100, 45)
    eff = st.sidebar.slider("Pump Efficiency (%):", 25, 70, 45)
    t_loss = st.sidebar.slider("Electricity Transmission Losses (%):", 10, 25, 15)

    ### Load Data
    df_energy = pd.read_csv("tubewell_energy_punjab.csv")
    df_gw = pd.read_csv("tubewell_pumping_categories.csv")

    df_gw = df_gw[df_gw["Year"] >= 2005].reset_index(drop=True)

    df_final, df_gw = compute_electric_gw_extraction(
        df_energy, df_gw, depth, eff, t_loss
    )

    ### Sidebar Plot
    df_sidebar = df_final.copy()
    df_sidebar["Storage"] = 14
    df_sidebar["Pumped Volume (MAF)"] = df_sidebar["Electric"]
    df_sidebar["Label"] = (
        "Combined Storage of Surface Reservoirs:\nTarbela, Mangla & Chashma"
    )
    df_sidebar["Label_Short"] = "Surface Reservoir Storage"
    df_sidebar["Source"] = "NEPRA Electricity Consumption Reports"

    plot_gw_pumping_sidebar(df_sidebar)

    st.sidebar.image("logo.png", width=100)
    st.sidebar.markdown("**Developed by Weather and Climate Services (WCS)**")

    ### Main Plot Preparation
    df_final = pd.melt(
        df_final, id_vars=["Year"], value_vars=["Electric", "Diesel"]
    )
    df_final.columns = ["Year", "Tube-well Type", "Pumped_Volume(MAF)"]
    df_final["Storage"] = 14
    df_final["Label"] = (
        "Combined Storage of Surface Reservoirs:\nTarbela, Mangla & Chashma"
    )
    df_final["Label_Short"] = "Surface Reservoir Storage"

    df_gw = pd.melt(
        df_gw,
        id_vars=["Year"],
        value_vars=["Electric Private", "Diesel Private", "Public", "Scarp", "Other Pr."],
    )
    df_gw.columns = ["Year", "Tube-well Type", "Pumped_Volume(%)"]

    ### Main Charts
    st.subheader("Groundwater Extraction Sources")
    plot_gw_pumping_summary(df_final, df_gw)

    ### Key Insights (FIXED)
    elec_perc = int(
        df_gw.loc[
            (df_gw["Year"] == 2017)
            & (df_gw["Tube-well Type"] == "Electric Private"),
            "Pumped_Volume(%)",
        ].iloc[0]
    )

    elec_vol = int(
        df_final.loc[
            (df_final["Year"] == 2017)
            & (df_final["Tube-well Type"] == "Electric"),
            "Pumped_Volume(MAF)",
        ].iloc[0]
    )

    st.markdown(
        f"""
        **KEY INSIGHTS:**  
        In **2017**, electric tube-wells extracted approximately **{elec_vol} MAF**
        of groundwater, accounting for **{elec_perc}%** of total groundwater extraction.
        This volume is comparable to Pakistan’s total surface reservoir storage
        (~14 MAF).
        """
    )

    ### Tubewell Trends
    st.subheader("Increasing Trends in Tube-well Installations")

    df_tw = pd.read_csv("num_tubewells.csv")

    plot_num_tubewells(
        df_tw,
        "rgb(55, 83, 109)",
        "rgb(26, 118, 255)",
        "stack",
        "Number of Agricultural Tube-wells in Pakistan",
        "Number of Tube-wells",
    )

    df_pump = df_tw.copy()
    df_pump["Electric"] = df_sidebar["Electric"] / df_tw["Electric"] * 1_000_000
    df_pump["Diesel"] = df_sidebar["Diesel"] / df_tw["Diesel"] * 1_000_000

    plot_num_tubewells(
        df_pump,
        "indianred",
        "lightsalmon",
        "group",
        "Annual Groundwater Extraction per Tube-well",
        "Acre-Feet per Tube-well",
        xloc=0.8,
    )

    ### References
    st.subheader("Data References")
    st.markdown(
        """
        1. NEPRA State of Industry Reports – Electricity Consumption  
        2. Agricultural Statistics of Pakistan – Ministry of National Food Security
        """
    )

    st.markdown("---")
    st.markdown("**Developed by Weather and Climate Services (WCS)**")


def compute_electric_gw_extraction(df_energy, df_gw, depth, eff, t_loss):

    df_energy["Electric"] = (
        0.81071318210885
        * df_energy["energy(Kwh)"]
        * ((eff / 100) * (1 - (t_loss / 100)))
        / (0.00273 * depth * 1_000_000_000)
    )

    df_energy["Diesel"] = df_energy["Total_GW(MAF)"] - df_energy["Electric"]
    df_energy = df_energy.drop(columns=["energy(Kwh)", "Total_GW(MAF)"])

    df_gw = df_gw.fillna(0)
    df_gw.insert(1, "Electric Private", df_energy["Electric"])
    df_gw.insert(2, "Diesel Private", df_energy["Diesel"])
    df_gw = df_gw.drop(columns=["Private", "Year"])
    df_gw = df_gw.div(df_gw.sum(axis=1), axis=0) * 100
    df_gw["Year"] = df_energy["Year"]

    return df_energy, df_gw


def plot_gw_pumping_sidebar(df):

    base = alt.Chart(df, title="Electric Tube-well Pumping")
    bars = base.mark_bar(opacity=0.7).encode(
        x="Year:O", y="Pumped Volume (MAF):Q", tooltip="Source"
    )
    rule = base.mark_rule(color="red", size=3).encode(y="Storage", tooltip="Label")

    st.sidebar.altair_chart(bars + rule, use_container_width=True)


def plot_gw_pumping_summary(df_final, df_gw):

    left = (
        alt.Chart(df_final)
        .mark_bar(opacity=0.7)
        .encode(
            x="Year:O",
            y="Pumped_Volume(MAF):Q",
            color="Tube-well Type",
        )
    )

    right = (
        alt.Chart(df_gw)
        .mark_bar(opacity=0.7)
        .encode(
            x="Year:O",
            y="Pumped_Volume(%):Q",
            color="Tube-well Type",
        )
    )

    st.altair_chart(left | right, use_container_width=True)


def plot_num_tubewells(df, c1, c2, mode, title, ylabel, xloc=0):

    fig = go.Figure()
    fig.add_bar(x=df["Years"], y=df["Electric"], name="Electric", marker_color=c1)
    fig.add_bar(x=df["Years"], y=df["Diesel"], name="Diesel", marker_color=c2)

    fig.update_layout(
        title=title,
        barmode=mode,
        height=300,
        yaxis_title=ylabel,
        legend=dict(x=xloc, y=1),
        margin=dict(l=20, r=20, t=40, b=20),
    )

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()

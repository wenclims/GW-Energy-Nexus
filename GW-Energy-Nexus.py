#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import streamlit as st
import pandas as pd
import altair as alt
from altair import datum
import plotly.graph_objects as go

def main():

    ### Create Application Header and Intro Text
    st.title("Pakistan's Groundwater-Energy Nexus")
    st.markdown("## \#RethinkingIndus")
    st.subheader("Impact of Subsidized Electric Tube-wells")
    st.markdown(
    """
    This is an interactive dashboard that allows users to understand the
    impact of groundwater extraction by subsidized private electric TubeWells(TW)
    on the overall water footprint in Pakistan. Annual electric GW extraction is 
    estimated from annual agricultural electricty consumption. Users may change 
    TW efficiencies, extraction depth, and grid transmission losses to estimate 
    the volume of water pumped by electric TWs and visualize some resulting insights.
    """)

    ### Create application Side-bar menu
    st.sidebar.title("Estimating Pumping")
    st.sidebar.markdown(
        """
        Pumping from electric tubewells is estimatated via the following equation: \n
        Volume = $\\frac{\\text{Energy*eff*(1-loss)}}{\\text{0.00273*depth}*10^6}$ \n
        Where **Volume** denotes the volume of groundwater ($m^3$) extracted by electric tubewells,
        **Energy** is the electricity(Kwh) consumed* by electric tube-wells, **eff** is an estimate of 
        average efficiency of an electric tubewell pump, **loss** is average electricity
        transmission loss and **depth** is average depth to water table. Users may change **eff**,
        **loss** and **depth** to visualize the impact on electric tube-well pumping volume in Pakistan.   
        """
    )
    # Create side-bar panels for tweaking model parameters
    st.sidebar.markdown(
        "## Parameters"
    )
    depth = st.sidebar.slider("Depth to Water Table(m): ",
                              min_value=30, max_value=100, value=45, step=1)
    eff = st.sidebar.slider("Pump Efficiency (%): ",
                            min_value=25, max_value=70, value=45, step=1)
    t_loss = st.sidebar.slider(" Electriciy Transmission Losses(%): ",
                               min_value=10, max_value=25, value=15, step=1)
    st.sidebar.markdown("")
    
    ### Load groundwater energy use data and surface storage data
    df = pd.read_csv('tubewell_energy_punjab.csv')
    df_gw = pd.read_csv('tubewell_pumping_categories.csv')
    df_gw = df_gw[df_gw['Year'] >= 2005]
    df_gw = df_gw.reset_index(drop=True)
    df_final, df_gw = compute_electric_gw_extraction(df, df_gw, depth, eff, t_loss)
    df_sidebar = df_final
    df_sidebar['Storage'] = 14
    df_sidebar['Pumped Volume (MAF)'] = df_sidebar['Electric']
    df_sidebar['Label'] = 'Combined Storage of Surface Reservoirs in Pakistan: \n '                         'Tarbela, Mangla and Chashma'
    df_sidebar['Label_Short'] = 'Storage of Surface Reservoirs'
    df_sidebar['Source'] = "Annual electricty consumption data for tubewells was obtained from NEPRA reports"
    df_final = pd.melt(df_final, id_vars=['Year'], value_vars=['Electric', 'Diesel'])
    df_final.columns = ['Year', 'Tube-well Type', 'Pumped_Volume(MAF)']
    df_final['Storage'] = 14
    df_final['Label'] = 'Combined Storage of Surface Reservoirs in Pakistan: \n '                         'Tarbela, Mangla and Chashma'
    df_final['Label_Short'] = 'Storage of Surface Reservoirs'
    df_gw = pd.melt(df_gw, id_vars=['Year'], value_vars=['Electric Private',
                                                         'Diesel Private',
                                                         'Public', 'Scarp',
                                                         'Other Pr.'])
    df_gw.columns = ['Year', 'Tube-well Type', 'Pumped_Volume(%)']


    ### Draw Plot on Sidebar --- Electric TW extraction
    plot_gw_pumping_sidebar(df_sidebar)
    ###st.sidebar.markdown("Developed by Haris Mushtaq and Taimoor Akhtar")
    #url = 'https://www.rethinkingindus.com/'
    st.sidebar.image("logo.png", width=100)
    #st.sidebar.markdown("RethinkingIndus")
    #st.sidebar.markdown(url)

    ### Create Groundwater Extraction Summary including Altair plot
    st.subheader("Groundwater Extraction Sources")
    st.markdown(
        "Below you can see distribution of sources of groundwater"
        " extraction, including *Private Electric Tubwells (TWs)*,"
        " *Private Diesel TWs*, and *Public TWs*, etc."
    )
    st.text("")
    plot_gw_pumping_summary(df_final, df_gw)

    ## Summarize insights from tubewell pumping plots
    x = df_gw.loc[(df_gw['Year'] == 2017) & (df_gw['Tube-well Type'] == 'Electric Private'),
                  'Pumped_Volume(%)'].values
    elec_perc = int(x)
    x = df_final.loc[(df_final['Year'] == 2017) & (df_final['Tube-well Type'] == 'Electric'),
                     'Pumped_Volume(MAF)'].values
    elec_vol = int(x)

    st.markdown(
         "**KEY INSIGHTS:** In **2017**, groundwater extracted from "
         "electric TWs was **{} MAF**, which is **{}%** of total "
         "groundwater extraction in the country. Moreover, this "
         "volume is close to **14 MAF**, i.e., the total available "
         "storage in surface reservoirs of Pakistan".format(elec_vol, elec_perc)
    )
    st.text("")

    ## Create visualizations to analyze trend in Tubwewell installations
    st.subheader("Increasing Trends in TW Installations")
    st.markdown(
        "Below you can see the change in number of electric and diesel"
        " tubwewell installations, and resulting extraction per installation, "
        "from 2005 to 2017."
    )
    st.text("")
    # Plot bar chart of trend in tubewell installation
    df_tw = pd.read_csv('num_tubewells.csv')
    title = 'Number of Installed Agricultural Tube-wells in Pakistan'
    ylabel = 'No. of Tubewells'
    color_1 = 'rgb(55, 83, 109)'
    color_2 = 'rgb(26, 118, 255)'
    bar_type = 'stack'
    plot_num_tubewells(df_tw, color_1, color_2, bar_type, title, ylabel)
    # Plot Bar Chart of Extraction per Tube-Well
    title = 'Annual Groundwater Extraction per Tubewell'
    ylabel = 'Extracted water per TW (Acre-Feet)'
    color_1 = 'indianred'
    color_2 = 'lightsalmon'
    bar_type = 'group'
    df_pump = df_tw
    df_pump['Electric'] = df_sidebar['Electric'] / df_tw['Electric']*1000000
    df_pump['Diesel'] = df_sidebar['Diesel'] / df_tw['Diesel']*1000000
    plot_num_tubewells(df_pump, color_1, color_2, bar_type, title, ylabel, xloc=0.8)
    # Provide insights on tubewell installation trend
    st.markdown(
        "**KEY INSIGHTS:** The number of installed electric TWs have almost "
        "**doubled** from 2005 to 2017. Moreover groundwater extraction per "
        "installed electric TW is more that **2x** times diesel TW. Policy "
        "action is required to modulate electric TW extraction, and subsidies "
        "on agricultural electric subsidies should be revisited."
    )
    st.text("")
    # Provide references
    st.subheader("Data References")
    st.markdown(
        """
        1. Annual electricity consumption data of electric TWs was obtained from NEPRA
        State of Industry Reports: https://nepra.org.pk/publications/SOI_reports.php 
        (It is assumed that all agricultural electric consumption is for TW pumping).
        2. Annual total groundwater extraction and tubewell inventory (no.s) data
        was obtained from Agricultural Statistics of Pakistan - Ministry of National
        Food Security and Research: http://www.mnfsr.gov.pk/pubDetails.aspx.    
        """
    )
    st.text("")


#@st.cache(persist=True)
def compute_electric_gw_extraction(df_energy, df_gw, depth, eff, t_loss):
    """Compute GW extraction given energy consumption, and depth to GW"""

    df_energy['Electric'] = 0.81071318210885*df_energy['energy(Kwh)']                           *((eff/100)*(1-(t_loss/100)))                           /(0.00273*depth*1000000000)
    df_energy['Diesel'] = df_energy['Total_GW(MAF)'] - df_energy['Electric']
    df_energy = df_energy.drop(columns=['energy(Kwh)', 'Total_GW(MAF)'])
    df_gw = df_gw.fillna(0)
    df_gw.insert(1, 'Electric Private', df_energy['Electric'])
    df_gw.insert(2, 'Diesel Private', df_energy['Diesel'])
    df_gw = df_gw.drop(columns=['Private'])
    df_gw = df_gw.drop(columns=['Year'])
    df_gw = df_gw.div(df_gw.sum(axis=1), axis=0) * 100
    df_gw['Year'] = df_energy['Year']
    return df_energy, df_gw


def plot_gw_pumping_sidebar(df_final):
    """Function for plotting pumped groundwater volume for application sidebar
    Parameters
    ----------
    df_final : Dataframe
        Groundwater pumping derived data
    """
    left_base = alt.Chart(df_final,
                          title="Pumped Groundwater:"
                                " Electric"
                                " TWs")
    left_bars = left_base.mark_bar(opacity=0.7).encode(
        x='Year:O',
        y='Pumped Volume (MAF):Q',
        tooltip='Source'
    )
    left_rule = left_base.mark_rule(
        opacity=0.5,
        color='red'
    ).encode(
        y='Storage',
        size=alt.value(3),
        opacity=alt.value(0.5),
        tooltip='Label'
    )

    left_plot = left_bars + left_rule
    st.sidebar.altair_chart(left_plot)


def plot_gw_pumping_summary(df_final, df_gw):
    """Function for detailed plotting of GW pumping for main panel
    Parameters
    ----------
    df_final : Dataframe
        Final pumped volume of GW (derived)
    df_gw : Dataframe
        Pumped GW volume (percentage)
    """
    left_base = alt.Chart(df_final,
                          title="Pumped Groundwater:"
                                " Private"
                                " Tube-Wells")
    left_bars = left_base.mark_bar(opacity=0.7).encode(
        x='Year:O',
        y='Pumped_Volume(MAF):Q',
        color=alt.Color("Tube-well Type", legend=None)
    )
    left_rule = left_base.mark_rule(
        opacity=0.5,
        color='red'
    ).encode(
        y='Storage',
        size=alt.value(3),
        opacity=alt.value(0.5),
        tooltip='Label'
    )
    left_text = left_base.mark_text(
        color='black',
        fontSize=12,
        dy=-10
    ).encode(
        x='Year:O',
        y='Storage',
        text='Label_Short',
        tooltip='Label'
    ).transform_filter(
        datum.Year == 2011
    )
    left_plot = left_bars + left_rule + left_text

    right_plot = alt.Chart(df_gw,
                           title="Pumped GW:"
                                 " By Percentage"
                           ).mark_bar(opacity=0.7).encode(
        x='Year:O',
        y='Pumped_Volume(%):Q',
        color=alt.Color("Tube-well Type",legend=(
            alt.Legend(orient="right")
        )),
        order='order:N'
    )

    c = alt.hconcat(
        left_plot,
        right_plot
    ).resolve_scale(
        color='independent'
    ).configure_view(
        stroke=None
    )
    st.altair_chart(c)


def plot_num_tubewells(df_tw, color_1, color_2, bar_type, title, ylabel, xloc=0):
    """Plotly barchart for plotting number of tubewells / extraction per tubewell
    """
    years = df_tw['Years']

    fig = go.Figure()
    fig.add_trace(go.Bar(x=years,
                         y=df_tw['Electric'],
                         name='Electric',
                         marker_color= color_1
                         ))
    fig.add_trace(go.Bar(x=years,
                         y=df_tw['Diesel'],
                         name='Diesel',
                         marker_color=color_2
                         ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        height=300,
        xaxis_tickfont_size=14,
        yaxis=dict(
            title=ylabel,
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=xloc,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
            font=dict(
                size=14
            )
        ),
        barmode=bar_type,
        bargap=0.15  # gap between bars of adjacent location coordinates.
    )
    st.plotly_chart(fig)


if __name__ == '__main__':
    main()


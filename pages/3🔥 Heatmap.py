import streamlit as st
import leafmap.foliumap as leafmap
import pandas as pd

st.set_page_config(layout="wide")

st.sidebar.title("Resources:")
st.sidebar.info(
    """
    - GitHub repository: [streamlit_flood](https://github.com/keanteng/streamlit_flood)
    - Data sources: [Flood Data](https://www.water.gov.my/)
    """
)

st.sidebar.title("Created By:")
st.sidebar.info(
    """
  Khor Kean Teng | Intern, DGA, JPS, Bank Negara Malaysia | [GitHub](https://github.com/keanteng) | [LinkedIn](https://www.linkedin.com/in/khorkeanteng/)
    """
)

st.title("Heatmap")
st.markdown(
    """
    Heatmaps are a great way to visualize the density of data points on a map. It shows the density of flood incidents each state
    where red areas have particularly more flood incidents. 
    
    As a general rule of thumb, location near rivers and coastal areas are more prone to flooding.
    """
)

button = st.slider("Year", 2015,2022,2015)
data = pd.read_csv('analytics/data2/all_states_all_years_geocoded.csv')

if button == 2015:
    data = data[data['Year'] == 2015]
elif button == 2016:
    data = data[data['Year'] == 2016]
elif button == 2017:
    data = data[data['Year'] == 2017]
elif button == 2018:
    data = data[data['Year'] == 2018]
elif button == 2019:
    data = data[data['Year'] == 2019]
elif button == 2020:
    data = data[data['Year'] == 2020]
elif button == 2021:
    data = data[data['Year'] == 2021]
else:
    data = data[data['Year'] == 2022]

with st.expander("Source Code (Click to Expand)"):
    with st.echo():

        filepath = "analytics/data2/Flood Data Updated Geocoded.csv"
        m = leafmap.Map(center=[4, 108], zoom=5)
        regions = 'analytics/data2/countries.geojson'

        m.add_geojson(regions, layer_name="Malaysia")
        m.add_heatmap(
            data,
            latitude="Latitude",
            longitude="Longitude",
            name="Heat map",
            value = "Year", # becomes frequency: some place flood a few times in a year, but also affect by reporting duration (data collection part)
            radius=20,
        )


m.to_streamlit(height=700)

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

st.title("Marker Cluster Map")
st.markdown(
    """
    To reduce the amount of data we need to fit on the map, we'll use the marker cluster feature 
    so that each cluster corresponds to flood incidents in a particular area. You can click on the cluster to zoom in and see the individual markers.
    """
)

button = st.slider("Year", 2015,2022,2015)
data = pd.read_csv('analytics/data2/all_states_all_years_geocoded.csv')
data[['Year']] = data[['Year']].astype(int)
data = data[['Year', 'Date','State', 'Region', 'Place', 'Latitude','Longitude']]

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

        m = leafmap.Map(center=[4, 108], zoom=5)
        
        cities = data
        regions = 'analytics/data2/countries.geojson'

        m.add_geojson(regions, layer_name="Malaysia")
        m.add_points_from_xy(
            cities,
            x="Longitude",
            y="Latitude",
            icon_names=['gear', 'map', 'leaf', 'globe'],
        )


m.to_streamlit(height=700)

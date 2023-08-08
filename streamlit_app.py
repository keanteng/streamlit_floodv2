import streamlit as st
import leafmap.foliumap as leafmap
from PIL import Image

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

# Customize page title
st.title("👋Welcome")

st.markdown(
    """
    This is a multipage app that uses [Streamlit](https://streamlit.io) to visualize flood incidents in Malaysia from 2015 - 2022. In this app you can find different pages that visualize the data in different ways. 
    The data for the chart is obtained from the annual report published by the Department of Irrigation and Drainage Malaysia (JPS). The app is also powered by some feature develop by 
    [mapaction/flood mapping tool](https://github.com/mapaction/flood-mapping-tool) and [opengeos/streamlit-geospatial](https://github.com/opengeos/streamlit-geospatial) that make use of 
    Google Earth Engine funtionality. 
    """
)

st.info("Check out my Git repository for installation instruction. Read below for further documentation 📖")

st.header("Documentation")

st.markdown(
"""
###  A. Flood Mapping Tool - Methodology

Data set used:
- Sential-1 synthetic-aperture radar [SAR](https://developers.google.com/earth-engine/datasets/catalog/COPERNICUS_S1_GRD) data
- WWF HydroSHEDS Void Filled DEM, 3 Arc Seconds [dataset](https://developers.google.com/earth-engine/datasets/catalog/WWF_HydroSHEDS_03VFDEM)
    - Elevation data obaitned in 2000 by NASA's Shuttle Radar Topography Mission (SRTM) that mark out areas with more than 5% slope
- JRC Global Surface Water Mapping Layers, v1.4 [dataset](https://developers.google.com/earth-engine/datasets/catalog/JRC_GSW1_4_GlobalSurfaceWater)
    - Maps of the location and temporal distribution of surface water from 1984 to 2021. It masked areas with perennial water bodies like rivers and lakes.

#### Flood Detection with Radar Imagery

Sentinel-1 is one of the simplest way to perform change detections. Radar satellites produce active radiation directed to the land,
while images are formed as a function of time time taken for radiation ot reach back to the satellite. In fact, radar systems are side-looking 
as this prevent radiation from multiple areas reaching the satellite at the same time. For images to be produced, radiation needs to be scattered back
to the satellite. But not all surfacess are equally able to do so and this is also influenced by the radiation's wavelength. For example, shorter wavelengths
are better at detecting smaller objects while longer wavelengths are better at penetration which helps to detect area with forest canopies. 

Water has a mirror-like reflection machanism. Thus, either no or very little radiation will be scattered back to the satellite. Even if it does, the pixels on the image will
appear very dark. Therfore, the change detection will simply takes a "before image" and check for drop in intensity in the "after image". 

So how Sentinel-1 data is being collected? In fact, it is the measurement from a constellation of two satellites, assigning over the same areas following a 6-day cycle. On Google 
Earth Engine, the processing level is Ground Range Detected (GRD) which means that is has been detected, multi-looked and projected to ground range using an Earth ellipsoid model. 
GRD will report on intensity of radiation but it will lost the phase and amplitude information which could be needed for other applications. The two satellites will emit in different
polarazations and can acquire both single horizontal or vertical or even dual polzarizations. For flood water, it is best to detect using VH (vertical transmit and horizontal receive), although VV
(vertical transmit and vertical receive) can be effective for patially submerged features. In our case, we will use VH polarization. The figure below shows the overview of the Sentinel-1 observation plan,
where pass directions and coverage frequencies are highlighted.
""")

image1 = Image.open('images/image2.jpg')
st.image(image1)

st.markdown("""

### Limitations
Radar imagery is good for flood detection as it is good at picking up water and not affected by the time of the day or clouds. But it can perform poorly in areas of mountainous regions, notably in narrow valleys
and urban areas. This is due to the viewing angles which caused image distortion. Of course, radar imagery can also cause false positive for ther land cover changes with smooth surfaces like roads or sand. Rough
surface texture caused by wind or rainfall may also make it difficult for radar imagery to identify water bodies. 


### B. Workflow  - Malaysia Flood Statistics 
""")

image2 = Image.open('images/image1.png')
st.image(image2)

st.markdown(
"""
### C. Open Street Map

In this web app, all the maps make use of [OpenStreetMap](https://www.openstreetmap.org) data. OpenStreetMap is a free and open-source collaborative project to create a map of the world.
It is built by a community of mappers that contribute and maintain data about roads, trails, cafés, railway stations, and much more, all over the world. Check out the map below for a quick
overview of the map powered by OpenStreetMap.
""")

m = leafmap.Map(minimap_control=True)
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)

st.markdown(
    """
    ### D. References
    1. [Map Action, Flood Mapping Tool Documentation](https://mapaction-flood-map.streamlit.app/Documentation)
    2. [In Detail: Recommended Practice: Flood Mapping and Damage Assessment Using Sentinel-1 SAR Data in Google Earth Engine](https://un-spider.org/advisory-support/recommended-practices/recommended-practice-google-earth-engine-flood-mapping/in-detail)
    3. [Identifying floods and flood-affected paddy rice fields in Bangladesh based on Sentinel-1 imagery and Google Earth Engine](https://www.sciencedirect.com/science/article/pii/S0924271620301702)
    4. [Sentinel-1 Observation Scenario](https://sentinel.esa.int/web/sentinel/missions/sentinel-1/observation-scenario)
    5. [Multi-temporal synthetic aperture radar flood mapping using change detection](https://onlinelibrary.wiley.com/doi/full/10.1111/jfr3.12303)
    """
)
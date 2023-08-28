# Streamlit App For Flood Incidents in Malaysia

![Static Badge](https://img.shields.io/badge/license-MIT-blue)
![Static Badge](https://img.shields.io/badge/python-3.9-blue)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://floodmapv2-wnakuiqz4idj5pr4ugzemq.streamlit.app/)

An app powered by Streamlit to visualize the flood incidents in Malaysia from 2015 to 2022. 

## Flood Mapping Tool
The web app contains a feature to allow user to estimate flood extent using Sentinel-1 synthetic-aperture radar SAR data. 

## Using this repository
1. Make sure you have installed all the packages in `requirements.txt`
2. If you are running this repo on your local Windows machine, you will probably encounter `fcntl module not found ` error. But this repo can still do fine on the web app
    - Go to [Google Earth Engine ](https://earthengine.google.com/) and create an account
    - Go to Windows terminal:
    ```python
    py -m pip install ee
    import ee
    ee.Authenticate()
    ```
    - You will need to paste the authorization code back on the terminal. Once the step is complete, you can find the token on your local machine at `C:\\Users\\Username\\.congif\\earthengine\\credentials`
3. Now assuming you have created an empty repository on you GitHub account and put everything in this repository there
    - Go to [Streamlit](https://streamlit.io/) and create an account there. Remember to link to your GitHub account. 
    - Then you need to deploy your repository you created just now. 
    - Before you click deploy, select advanced option and fill up the secret using the information in `C:\\Users\\Username\\.congif\\earthengine\\credentials`. You need to copy everything there. 
    ```toml
    EARTHENGINE_TOKEN = 'PASTE WHAT YOU COPY HERE'
    ee_keys = 'PASTE WHAT YOU COPY HERE'
    ```

## Updates
1. 8/1/2023 
    - Perform second run for geocoding to check performance deviation
2. 8/2/2023 
    - Perform alternative run for geocoding using address format: Place, Region
    - Perform reverse geocode to check geocoding accuracy
    - Updates maps and app contents
3. 8/3/2023
    - Perform reverse geocoding to search location postal code
    - Explore on adding [flood mapping tool](https://github.com/mapaction/flood-mapping-tool) and some [geospatial application](https://github.com/opengeos/streamlit-geospatial)
4. 8/4/2023
    - Updates web app features based on previous exploration for tool
5. 8/7/2023
    - On Flood Mapping Tool pages, add an overlay for flood points
        - Include sizeable circle around each flood points

## References
1. [mapaction/flood mapping tool](https://github.com/mapaction/flood-mapping-tool)
2. [opengeos/streamlit-geospatial](https://github.com/opengeos/streamlit-geospatial)

Internship Project © 2023

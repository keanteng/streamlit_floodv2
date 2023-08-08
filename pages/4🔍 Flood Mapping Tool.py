"""Flood extent analysis page for Streamlit app."""
import datetime as dt

import ee
import folium
import geemap
import geemap.foliumap as geemap
import requests
import streamlit as st
import pandas as pd
import geopandas as gpd
from folium import GeoJson
# import streamlit_ext as ste
from folium.plugins import Draw, Geocoder, MiniMap
from streamlit_folium import st_folium

####################################################
params = {
    # Title browser tab
    "browser_title": "Flood mapping tool - MapAction",
    # Data scientists involved
    "data_scientists": {
        "Piet": "pgerrits@mapaction.org",
        "Daniele": "dcastellana@mapaction.org",
        "Cate": "cseale@mapaction.org",
    },
    # Urls
    "url_data_science_wiki": (
        "https://mapaction.atlassian.net/wiki/spaces/GAFO/overview"
    ),
    "url_gee": "https://earthengine.google.com/",
    "url_project_wiki": (
        "https://mapaction.atlassian.net/wiki/spaces/GAFO/pages/15920922751/"
        "Rapid+flood+mapping+from+satellite+imagery"
    ),
    "url_github_repo": "https://github.com/mapaction/flood-extent-tool",
    "url_sentinel_esa": (
        "https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar"
    ),
    "url_sentinel_dataset": (
        "https://developers.google.com/earth-engine/datasets/catalog/"
        "COPERNICUS_S1_GRD"
    ),
    "url_sentinel_img": (
        "https://sentinel.esa.int/documents/247904/4748961/Sentinel-1-Repeat-"
        "Coverage-Frequency-Geometry-2021.jpg"
    ),
    "url_sentinel_img_location": (
        "https://sentinel.esa.int/web/sentinel/missions/sentinel-1/"
        "observation-scenario"
    ),
    "url_unspider_tutorial": (
        "https://un-spider.org/advisory-support/recommended-practices/"
        "recommended-practice-google-earth-engine-flood-mapping"
    ),
    "url_unspider_tutorial_detail": (
        "https://un-spider.org/advisory-support/recommended-practices/"
        "recommended-practice-google-earth-engine-flood-mapping/in-detail"
    ),
    "url_elevation_dataset": (
        "https://developers.google.com/earth-engine/datasets/catalog/"
        "WWF_HydroSHEDS_03VFDEM"
    ),
    "url_surface_water_dataset": (
        "https://developers.google.com/earth-engine/datasets/catalog/"
        "JRC_GSW1_4_GlobalSurfaceWater"
    ),
    "url_publication_1": (
        "https://onlinelibrary.wiley.com/doi/full/10.1111/jfr3.12303"
    ),
    "url_publication_2": (
        "https://www.sciencedirect.com/science/article/abs/pii/"
        "S0924271620301702"
    ),
    # Layout and styles
    ## Sidebar
    "MA_logo_width": "60%",
    "MA_logo_background_position": "35% 10%",
    "sidebar_header": "Flood Mapping Tool",
    "sidebar_header_fontsize": "30px",
    "sidebar_header_fontweight": "bold",
    "about_box_background_color": "#dae7f4",
    ## Introduction and Documentation pages
    "docs_fontsize": "1.2rem",
    "docs_caption_fontsize": "1rem",
    ## Tool page
    "expander_header_fontsize": "23px",
    "widget_header_fontsize": "18px",
    "button_text_fontsize": "24px",
    "button_text_fontweight": "bold",
    "button_background_color": "#dae7f4",
}

import ee
import streamlit as st
from ee import oauth
from google.oauth2 import service_account

@st.experimental_memo
def ee_initialize(force_use_service_account: bool = False):
    """Initialise Google Earth Engine.

    Checks whether the app is deployed on Streamlit Cloud and, based on the
    result, initialises Google Earth Engine in different ways: if the app is
    run locally, the credentials are retrieved from the user's credentials
    stored in the local system (personal Google account is used). If the app
    is deployed on Streamlit Cloud, credentials are taken from the secrets
    field in the cloud (a dedicated service account is used).
    Inputs:
        force_use_service_account (bool): If True, the dedicated Google
            service account is used, regardless of whether the app is run
            locally or in the cloud. To be able to use a service account
            locally, a file called "secrets.toml" should be added to the
            folder ".streamlit", in the main project folder.

    Returns:
        None
    """
    if force_use_service_account or is_app_on_streamlit():
        service_account_keys = st.secrets["ee_keys"]
        ee.Initialize(service_account_keys)
    else:
        ee.Initialize()
    
    import time

import ee


def _check_task_completed(task_id, verbose=False):
    """
    Return True if a task export completes successfully, else returns false.

    Inputs:
        task_id (str): Google Earth Engine task id

    Returns:
        boolean

    """
    status = ee.data.getTaskStatus(task_id)[0]
    if status["state"] in (
        ee.batch.Task.State.CANCELLED,
        ee.batch.Task.State.FAILED,
    ):
        if "error_message" in status:
            if verbose:
                print(status["error_message"])
        return True
    elif status["state"] == ee.batch.Task.State.COMPLETED:
        return True
    return False


def wait_for_tasks(task_ids, timeout=3600, verbose=False):
    """
    Wait for tasks to complete, fail, or timeout.

    Wait for all active tasks if task_ids is not provided.
    Note: Tasks will not be canceled after timeout, and
    may continue to run.
    Inputs:
        task_ids (list):
        timeout (int):

    Returns:
        None
    """
    start = time.time()
    elapsed = 0
    while elapsed < timeout or timeout == 0:
        elapsed = time.time() - start
        finished = [_check_task_completed(task) for task in task_ids]
        if all(finished):
            if verbose:
                print(f"Tasks {task_ids} completed after {elapsed}s")
            return True
        time.sleep(5)
    if verbose:
        print(
            f"Stopped waiting for {len(task_ids)} tasks \
            after {timeout} seconds"
        )
    return False


def export_flood_data(
    flooded_area_vector,
    flooded_area_raster,
    image_before_flood,
    image_after_flood,
    region,
    filename="flood_extents",
    verbose=False,
):
    """
    Export the results of derive_flood_extents function to Google Drive.

    Inputs:
        flooded_area_vector (ee.FeatureCollection): Detected flood extents as
            vector geometries.
        flooded_area_raster (ee.Image): Detected flood extents as a binary
            raster.
        image_before_flood (ee.Image): The 'before' Sentinel-1 image.
        image_after_flood (ee.Image): The 'after' Sentinel-1 image containing
            view of the flood waters.
        region (ee.Geometry.Polygon): Geographic extent of analysis area.
        filename (str): Desired filename prefix for exported files

    Returns:
        None
    """
    if verbose:
        print(
            "Exporting detected flood extents to your Google Drive. \
            Please wait..."
        )
    s1_before_task = ee.batch.Export.image.toDrive(
        image=image_before_flood,
        description="export_before_s1_scene",
        scale=30,
        region=region,
        fileNamePrefix=filename + "_s1_before",
        crs="EPSG:4326",
        fileFormat="GeoTIFF",
    )

    s1_after_task = ee.batch.Export.image.toDrive(
        image=image_after_flood,
        description="export_flooded_s1_scene",
        scale=30,
        region=region,
        fileNamePrefix=filename + "_s1_after",
        crs="EPSG:4326",
        fileFormat="GeoTIFF",
    )

    raster_task = ee.batch.Export.image.toDrive(
        image=flooded_area_raster,
        description="export_flood_extents_raster",
        scale=30,
        region=region,
        fileNamePrefix=filename + "_raster",
        crs="EPSG:4326",
        fileFormat="GeoTIFF",
    )

    vector_task = ee.batch.Export.table.toDrive(
        collection=flooded_area_vector,
        description="export_flood_extents_polygons",
        fileFormat="shp",
        fileNamePrefix=filename + "_polygons",
    )

    s1_before_task.start()
    s1_after_task.start()
    raster_task.start()
    vector_task.start()

    if verbose:
        print("Exporting before Sentinel-1 scene: Task id ", s1_before_task.id)
        print("Exporting flooded Sentinel-1 scene: Task id ", s1_after_task.id)
        print("Exporting flood extent geotiff: Task id ", raster_task.id)
        print("Exporting flood extent shapefile:  Task id ", vector_task.id)

    wait_for_tasks(
        [s1_before_task.id, s1_after_task.id, raster_task.id, vector_task.id]
    )


def retrieve_image_collection(
    search_region,
    start_date,
    end_date,
    polarization="VH",
    pass_direction="Ascending",
):
    """
    Retrieve Sentinel-1 immage collection from Google Earth Engine.

    Inputs:
        search_region (ee.Geometry.Polygon): Geographic extent of image search.
        start_date (str): Date in format yyyy-mm-dd, e.g., '2020-10-01'.
        end_date (str): Date in format yyyy-mm-dd, e.g., '2020-10-01'.
        polarization (str): Synthetic aperture radar polarization mode, e.g.,
            'VH' or 'VV'. VH is mostly is the preferred polarization for
            flood mapping.
        pass_direction (str): Synthetic aperture radar pass direction, either
            'Ascending' or 'Descending'.

    Returns:
        collection (ee.ImageCollection): Sentinel-1 images matching the search
        criteria.
    """
    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filter(ee.Filter.eq("instrumentMode", "IW"))
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation", polarization
            )
        )
        .filter(ee.Filter.eq("orbitProperties_pass", pass_direction.upper()))
        .filter(ee.Filter.eq("resolution_meters", 10))
        .filterDate(start_date, end_date)
        .filterBounds(search_region)
        .select(polarization)
    )

    return collection


def smooth(image, smoothing_radius=50):
    """
    Reduce the radar speckle by smoothing.

    Inputs:
        image (ee.Image): Input image.
        smoothing_radius (int): The radius of the kernel to use for focal mean
            smoothing.

    Returns:
        smoothed_image (ee.Image): The resulting image after smoothing is
            applied.
    """
    smoothed_image = image.focal_mean(
        radius=smoothing_radius, kernelType="circle", units="meters"
    )

    return smoothed_image


def mask_permanent_water(image):
    """
    Query the JRC Global Surface Water Mapping Layers, v1.3.

    The goal is to determine where perennial water bodies (water > 10
    months/yr), and mask these areas.
    Inputs:
        image (ee.Image): Input image.

    Returns:
        masked_image (ee.Image): The resulting image after surface water
        masking is applied.
    """
    surface_water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select(
        "seasonality"
    )
    surface_water_mask = surface_water.gte(10).updateMask(
        surface_water.gte(10)
    )

    # Flooded layer where perennial water bodies(water > 10 mo / yr) is
    # assigned a 0 value
    where_surface_water = image.where(surface_water_mask, 0)

    masked_image = image.updateMask(where_surface_water)

    return masked_image


def reduce_noise(image):
    """
    Reduce noise in the image.

    Compute connectivity of pixels to eliminate those connected to 8 or fewer
    neighbours.
    Inputs:
        image (ee.Image): A binary image.

    Returns:
        reduced_noise_image (ee.Image): The resulting image after noise
            reduction is applied.
    """
    connections = image.connectedPixelCount()
    reduced_noise_image = image.updateMask(connections.gte(8))

    return reduced_noise_image


def mask_slopes(image):
    """
    Mask out areas with more than 5 % slope with a Digital Elevation Model.

    Inputs:
        image (ee.Image): Input image.
    Returns:
         slopes_masked (ee.Image): The resulting image after slope masking is
            applied.
    """
    dem = ee.Image("WWF/HydroSHEDS/03VFDEM")
    terrain = ee.Algorithms.Terrain(dem)
    slope = terrain.select("slope")
    slopes_masked = image.updateMask(slope.lt(5))

    return slopes_masked


def derive_flood_extents(
    aoi,
    before_start_date,
    before_end_date,
    after_start_date,
    after_end_date,
    difference_threshold=1.25,
    polarization="VH",
    pass_direction="Ascending",
    export=False,
    export_filename="flood_extents",
):
    """
    Set start and end dates of a period BEFORE and AFTER a flood.

    These periods need to be long enough for Sentinel-1 to acquire an image.

    Inputs:
        aoi (ee.Geometry.Polygon): Geographic extent of analysis area.
        before_start_date (str): Date in format yyyy-mm-dd, e.g., '2020-10-01'.
        before_end_date (str): Date in format yyyy-mm-dd, e.g., '2020-10-01'.
        after_start_date (str): Date in format yyyy-mm-dd, e.g., '2020-10-01'.
        after_end_date (str): Date in format yyyy-mm-dd, e.g., '2020-10-01'.
        difference_threshold (float): Threshold to be applied on the
            differenced image (after flood - before flood). It has been chosen
            by trial and error. In case your flood extent result shows many
            false-positive or negative signals, consider changing it.
        export (bool): Flag to export derived flood extents to Google Drive
        export_filename (str): Desired filename prefix for exported files. Only
            used if export=True.

    Returns:
        flood_vectors (ee.FeatureCollection): Detected flood extents as vector
            geometries.
        flood_rasters (ee.Image): Detected flood extents as a binary raster.
        before_filtered (ee.Image): The 'before' Sentinel-1 image.
        after_filtered (ee.Image): The 'after' Sentinel-1 image containing view
            of the flood waters.
    """
    before_flood_img_col = retrieve_image_collection(
        search_region=aoi,
        start_date=before_start_date,
        end_date=before_end_date,
        polarization=polarization,
        pass_direction=pass_direction,
    )
    after_flood_img_col = retrieve_image_collection(
        search_region=aoi,
        start_date=after_start_date,
        end_date=after_end_date,
        polarization=polarization,
        pass_direction=pass_direction,
    )

    # Create a mosaic of selected tiles and clip to study area
    before_mosaic = before_flood_img_col.mosaic().clip(aoi)
    after_mosaic = after_flood_img_col.mosaic().clip(aoi)

    before_filtered = smooth(before_mosaic)
    after_filtered = smooth(after_mosaic)

    # Calculate the difference between the before and after images
    difference = after_filtered.divide(before_filtered)

    # Apply the predefined difference - threshold and create the flood extent
    # mask
    difference_binary = difference.gt(difference_threshold)
    difference_binary_masked = mask_permanent_water(difference_binary)
    difference_binary_masked_reduced_noise = reduce_noise(
        difference_binary_masked
    )
    flood_rasters = mask_slopes(difference_binary_masked_reduced_noise)

    # Export the extent of detected flood in vector format
    flood_vectors = flood_rasters.reduceToVectors(
        scale=10,
        geometryType="polygon",
        geometry=aoi,
        eightConnected=False,
        bestEffort=True,
        tileScale=2,
    )

    if export:
        export_flood_data(
            flooded_area_vector=flood_vectors,
            flooded_area_raster=flood_rasters,
            image_before_flood=before_filtered,
            image_after_flood=after_filtered,
            region=aoi,
            filename=export_filename,
        )

    return flood_vectors, flood_rasters, before_filtered, after_filtered

import base64
import os
from datetime import date

import streamlit as st

# Check if app is deployed
def is_app_on_streamlit():
    """Check whether the app is on streamlit or runs locally."""
    return "HOSTNAME" in os.environ and os.environ["HOSTNAME"] == "streamlit"


# General layout
def toggle_menu_button():
    """If app is on streamlit, hide menu button."""
    if is_app_on_streamlit():
        st.markdown(
            """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
        </style>
        """,
            unsafe_allow_html=True,
        )


# Home page
def set_home_page_style():
    """Set style home page."""
    st.markdown(
        """
    <style> p { font-size: %s; } </style>
    """
        % params["docs_fontsize"],
        unsafe_allow_html=True,
    )


# Documentation page
def set_doc_page_style():
    """Set style documentation page."""
    st.markdown(
        """
    <style> p { font-size: %s; } </style>
    """
        % params["docs_fontsize"],
        unsafe_allow_html=True,
    )


# Tool page
def set_tool_page_style():
    """Set style tool page."""
    st.markdown(
        """
            <style>
                .streamlit-expanderHeader {
                    font-size: %s;
                    color: #000053;
                }
                .stDateInput > label {
                    font-size: %s;
                }
                .stSlider > label {
                    font-size: %s;
                }
                .stRadio > label {
                    font-size: %s;
                }
                .stButton > button {
                    font-size: %s;
                    font-weight: %s;
                    background-color: %s;
                }
            </style>
        """
        % (
            params["expander_header_fontsize"],
            params["widget_header_fontsize"],
            params["widget_header_fontsize"],
            params["widget_header_fontsize"],
            params["button_text_fontsize"],
            params["button_text_fontweight"],
            params["button_background_color"],
        ),
        unsafe_allow_html=True,
    )


# Sidebar
@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(png_file):
    """
    Get base64 from image file.

    Inputs:
        png_file (str): image filename

    Returns:
        str: encoded ASCII file
    """
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def build_markup_for_logo(
    png_file,
):
    """
    Create full string for navigation bar, including logo and title.

    Inputs:
        png_file (str): image filename
        background_position (str): position logo
        image_width (str): width logo
        image_height (str): height logo

    Returns
        str: full string with logo and title for sidebar
    """
    return """
            <style>
                [data-testid="stSidebarNav"] {
                    background-image: url("data:image/png;base64,%s");
                    background-repeat: no-repeat;
                    padding-top: 50px;
                    padding-bottom: 10px;
                    background-position: %s;
                    background-size: %s %s;
                }
                [data-testid="stSidebarNav"]::before {
                    content: "%s";
                    margin-left: 20px;
                    margin-top: 20px;
                    margin-bottom: 20px;
                    font-size: %s;
                    font-weight: %s;
                    position: relative;
                    text-align: center;
                    top: 85px;
                }
            </style>
            """ % (
        binary_string,
        params["MA_logo_background_position"],
        params["MA_logo_width"],
        "",
        params["sidebar_header"],
        params["sidebar_header_fontsize"],
        params["sidebar_header_fontweight"],
    )


def add_logo(png_file):
    """
    Add logo to sidebar.

    Inputs:
        png_file (str): image filename
    Returns:
        None
    """
    # st.sidebar.title("ciao")
    st.markdown(
        logo_markup,
        unsafe_allow_html=True,
    )


def add_about():
    """
    Add about and contacts to sidebar.

    Inputs:
        None
    Returns:
        None
    """
    today = date.today().strftime("%B %d, %Y")

    # About textbox
    st.sidebar.markdown("## About")
    st.sidebar.markdown(
        """
        <div class='warning' style='
            background-color: %s;
            margin: 0px;
            padding: 1em;'
        '>
            <p style='
                margin-left:1em;
                margin: 0px;
                font-size: 1rem;
                margin-bottom: 1em;
            '>
                    Last update: %s
            </p>
            <p style='
                margin-left:1em;
                font-size: 1rem;
                margin: 0px
            '>
                <a href='%s'>
                Wiki reference page</a><br>
                <a href='%s'>
                GitHub repository</a><br>
                <a href='%s'>
                Data Science Lab</a>
            </p>
        </div>
        """
        % (
            params["about_box_background_color"],
            today,
            params["url_project_wiki"],
            params["url_github_repo"],
            params["url_data_science_wiki"],
        ),
        unsafe_allow_html=True,
    )

    # Contacts textbox
    st.sidebar.markdown(" ")
    st.sidebar.markdown("## Contacts")

    # Add data scientists and emails
    contacts_text = ""
    for ds, email in params["data_scientists"].items():
        contacts_text += ds + (
            "<span style='float:right; margin-right: 3px;'>"
            "<a href='mailto:%s'>%s</a></span><br>" % (email, email)
        )

    # Add text box
    st.sidebar.markdown(
        """
        <div class='warning' style='
            background-color: %s;
            margin: 0px;
            padding: 1em;'
        '>
            <p style='
                margin-left:1em;
                font-size: 1rem;
                margin: 0px
            '>
                %s
            </p>
        </div>
        """
        % (params["about_box_background_color"], contacts_text),
        unsafe_allow_html=True,
    )
#####################################################

# Page configuration
st.set_page_config(layout="wide", page_title=params["browser_title"])

# If app is deployed hide menu button
toggle_menu_button()

# Create sidebar
# add_about()
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

# Page title
st.markdown("# Flood extent analysis")

# Set page style
set_tool_page_style()

# Initialise Google Earth Engine
# ee_initialize(force_use_service_account=True)


# Output_created is useful to decide whether the bottom panel with the
# output map should be visualised or not
if "output_created" not in st.session_state:
    st.session_state.output_created = False


# Function to be used to hide bottom panel (when setting parameters for a
# new analysis)
def callback():
    """Set output created to zero: reset tool."""
    st.session_state.output_created = False


# Create two rows: top and bottom panel
row1 = st.container()
row2 = st.container()
# Crate two columns in the top panel: input map and paramters
col1, col2 = row1.columns([2, 1])
with col1:
    # Add collapsable container for input map
    with st.expander("Input map", expanded=True):
        # Create folium map
        Map = folium.Map(
            location=[52.205276, 0.119167],
            zoom_start=3,
            control_scale=True,
            # crs='EPSG4326'
        )
        # Add drawing tools to map
        Draw(
            export=False,
            draw_options={
                "circle": False,
                "polyline": False,
                "polygon": True,
                "circle": False,
                "marker": False,
                "circlemarker": False,
            },
        ).add_to(Map)
        # Add search bar with geocoder to map
        Geocoder(add_marker=False).add_to(Map)
        # Add minimap to map
        MiniMap().add_to(Map)
        # Export map to Streamlit
        output = st_folium(Map, width=800, height=600)
with col2:
    # Add collapsable container for image dates
    with st.expander("Choose Image Dates"):
        # Callback is added, so that, every time a parameters is changed,
        # the bottom panel containing the output map is hidden
        before_start = st.date_input(
            "Start date for reference imagery",
            value=dt.date(year=2022, month=7, day=1),
            help="It needs to be prior to the flooding event",
            on_change=callback,
        )
        before_end = st.date_input(
            "End date for reference imagery",
            value=dt.date(year=2022, month=7, day=30),
            help=(
                "It needs to be prior to the flooding event, at least 15 "
                "days subsequent to the date selected above"
            ),
            on_change=callback,
        )
        after_start = st.date_input(
            "Start date for flooding imagery",
            value=dt.date(year=2022, month=9, day=1),
            help="It needs to be subsequent to the flooding event",
            on_change=callback,
        )
        after_end = st.date_input(
            "End date for flooding imagery",
            value=dt.date(year=2022, month=9, day=16),
            help=(
                "It needs to be subsequent to the flooding event and at "
                "least 10 days to the date selected above"
            ),
            on_change=callback,
        )
    # Add collapsable container for parameters
    with st.expander("Choose Parameters"):
        # Add slider for threshold
        add_slider = st.slider(
            label="Select a threshold",
            min_value=0.0,
            max_value=5.0,
            value=1.25,
            step=0.25,
            help="Higher values might reduce overall noise",
            on_change=callback,
        )
        # Add radio buttons for pass direction
        pass_direction = st.radio(
            "Set pass direction",
            ["Ascending", "Descending"],
            on_change=callback,
        )
    # Button for computation
    submitted = st.button("Compute flood extent")
    # Introduce date validation
    check_dates = before_start < before_end <= after_start < after_end
    # Introduce drawing validation (a polygon needs to exist)
    check_drawing = (
        output["all_drawings"] != [] and output["all_drawings"] is not None
    )
# What happens when button is clicked on?
if submitted:
    with col2:
        # Output error if dates are not valid
        if not check_dates:
            st.error("Make sure that the dates were inserted correctly")
        # Output error if no polygons were drawn
        elif not check_drawing:
            st.error("No region selected.")
        else:
            # Add output for computation
            with st.spinner("Computing... Please wait..."):
                # Extract coordinates from drawn polygon
                coords = output["all_drawings"][-1]["geometry"]["coordinates"][
                    0
                ]
                # Create geometry from coordinates
                ee_geom_region = ee.Geometry.Polygon(coords)
                # Crate flood raster and vector
                (
                    detected_flood_vector,
                    detected_flood_raster,
                    _,
                    _,
                ) = derive_flood_extents(
                    aoi=ee_geom_region,
                    before_start_date=str(before_start),
                    before_end_date=str(before_end),
                    after_start_date=str(after_start),
                    after_end_date=str(after_end),
                    difference_threshold=add_slider,
                    polarization="VH",
                    pass_direction=pass_direction,
                    export=False,
                )
                # Create output map
                Map2 = geemap.Map(
                    # basemap="HYBRID",
                    plugin_Draw=False,
                    Draw_export=False,
                    locate_control=False,
                    plugin_LatLngPopup=False,
                )
                try:
                    # Add flood vector layer to map
                    Map2.add_layer(
                        ee_object=detected_flood_raster,
                        name="Flood extent raster",
                    )
                    Map2.add_layer(
                        ee_object=detected_flood_vector,
                        name="Flood extent vector",
                    )
                    # Center map on flood raster
                    Map2.centerObject(detected_flood_raster)
                except ee.EEException:
                    # If error contains the sentence below, it means that
                    # an image could not be properly generated
                    st.error(
                        """
                        No satellite image found for the selected
                        dates.\n\n
                        Try changing the pass direction.\n\n
                        If this does not work, choose different
                        dates: it is likely that the satellite did not
                        cover the area of interest in the range of
                        dates specified (either before or after the
                        flooding event).
                        """
                    )
                else:
                    # If computation was succesfull, save outputs for
                    # output map
                    st.success("Computation complete")
                    st.session_state.output_created = True
                    st.session_state.Map2 = Map2
                    st.session_state.detected_flood_raster = (
                        detected_flood_raster
                    )
                    st.session_state.detected_flood_vector = (
                        detected_flood_vector
                    )
                    st.session_state.ee_geom_region = ee_geom_region
# If computation was successful, create output map in bottom panel
if st.session_state.output_created:
    with row2:
        # Add collapsable container for output map
        with st.expander("Output map", expanded=True):
            # Export Map2 to streamlit
            st.session_state.Map2.to_streamlit()
            # Create button to export to file
            submitted2 = st.button("Export to file")
            # What happens if button is clicked on?
            if submitted2:
                # Add output for computation
                with st.spinner("Computing... Please wait..."):
                    try:
                        # Get download url for raster data
                        raster = st.session_state.detected_flood_raster
                        url_r = raster.getDownloadUrl(
                            {
                                "region": st.session_state.ee_geom_region,
                                "scale": 30,
                                "format": "GEO_TIFF",
                            }
                        )
                    except Exception:
                        st.error(
                            """
                            The image size is too big for the image to
                            be exported to file. Select a smaller area
                            of interest (side <~ 150km) and repeat the
                            analysis.
                            """
                        )
                    else:
                        response_r = requests.get(url_r)
                        # Get download url for raster data
                        vector = st.session_state.detected_flood_vector
                        url_v = vector.getDownloadUrl("GEOJSON")
                        response_v = requests.get(url_v)
                        filename = "flood_extent"
                        timestamp = dt.datetime.now().strftime(
                            "%Y-%m-%d_%H-%M"
                        )
                        # with row2:
                            # Create download buttons for raster and vector
                            # data
                            # with open("flood_extent.tif", "wb"):
                                # ste.download_button(
                                    # label="Download Raster Extent",
                                    # data=response_r.content,
                                    # file_name=(
                                        # f"{filename}"
                                        # "_raster_"
                                        # f"{timestamp}"
                                       #  ".tif"
                                    # )# ,
                                    # mime="image/tif",
                                # )
                            # with open("flood_extent.geojson", "wb"):
                                # ste.download_button(
                                    # label="Download Vector Extent",
                                    # data=response_v.content,
                                    # file_name=(
                                        # f"{filename}"
                                        # "_vector_"
                                        # f"{timestamp}"
                                       #  ".geojson"
                                    # )# ,
                                    # mime="text/json",
                                # )
                        # Output for computation complete
                        st.success("Computation complete")

with st.expander("Further Analysis", expanded=False):
    if st.session_state.output_created:
        m = geemap.Map(center=(4, 108), zoom=4)
        cities = pd.read_csv("analytics/data2/all_states_all_years_geocoded.csv")
        cities = cities[['Name', 'Latitude', 'Longitude', 'Year']]
        
        button = st.slider("Year", 2015,2022,2015)
        
        if button == 2015:
            cities = cities[cities['Year'] == 2015]
        elif button == 2016:
            cities = cities[cities['Year'] == 2016]
        elif button == 2017:
            cities = cities[cities['Year'] == 2017]
        elif button == 2018:
            cities = cities[cities['Year'] == 2018]
        elif button == 2019:
            cities = cities[cities['Year'] == 2019]
        elif button == 2020:
            cities = cities[cities['Year'] == 2020]
        elif button == 2021:
            cities = cities[cities['Year'] == 2021]
        else:
            cities = cities[cities['Year'] == 2022]
        
        slider = st.slider(
            label="Select Radius Size: Deafult 0.001",
            min_value=0.001,
            max_value=0.01,
            value=0.001,
            step=0.001,
        ) # to run this need a new loop 
        
        def getData(slider):
            return slider
        
        data = gpd.GeoDataFrame(cities, geometry = gpd.points_from_xy(cities.Longitude, cities.Latitude), crs = "EPSG:4326")
        two_mile_buffer = data.geometry.buffer(getData(slider))
        st.write("Radius Size = ", getData(slider))
        
        m.add_points_from_xy(
            cities, 
            x="Longitude", 
            y="Latitude",
            icon_names=['gear', 'map', 'leaf', 'globe'],
        )
        
        # m.add_heatmap(
            # cities,
            # latitude="Latitude",
            # longitude="Longitude",
            # name="Heat map",
            # value = "Year", # becomes frequency: some place flood a few times in a year, but also affect by reporting duration (data collection part)
            # radius=20,
        # )
        
        # add layer code section
        m.add_geojson(GeoJson(two_mile_buffer.geometry.to_crs(epsg=4326)).data, fill_colors=['blue'], layer_name = "Asset At Risk")
        ############################
        
        detected_flood_raster = st.session_state.detected_flood_raster
        detected_flood_vector = st.session_state.detected_flood_vector
        m.add_layer(
            ee_object=detected_flood_raster,
            name="Flood extent raster",
        )
        m.add_layer(
            ee_object=detected_flood_vector,
            name="Flood extent vector",
        )
        m.to_streamlit(height = 700)
    else:
        st.error("Error: No output created yet.")
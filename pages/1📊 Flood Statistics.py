import streamlit as st
import pandas as pd
import plotly.express as px

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

st.title("Flood Incidents in Malaysia (2015 - 2021)")

st.markdown(
    """
    Here is a visualize flood incidents in Malaysia from the year 2015 - 2022. The data for the chart is obtained from the annual report published by the Department of Irrigation and Drainage Malaysia (JPS).
    The data is available on their website [here](https://www.water.gov.my/). The data is then geocoded using [Nominatim Geocoder](https://opencagedata.com/).
    """
)

st.info("Scroll down to see some flood statistics! 👇")

data = pd.read_csv("analytics/data2/all_states_all_years_geocoded.csv")

# get the total incidents per year
data1 = pd.DataFrame(data[['Year']])
data1 = data1.groupby(['Year']).value_counts().reset_index(name='Total Incidents')

# plotting
fig1 = px.bar(data1, x="Year", y="Total Incidents", color= "Year", title="Total Flood Incidents in Malaysia (2015- 2021)")

st.plotly_chart(fig1, use_container_width=True)

# get the total incidents per state
data2 = pd.DataFrame(data[['Year', 'State']])
data2 = data2.groupby(['Year', 'State']).value_counts().reset_index(name='Total Incidents')
data2.head()

button = st.slider("Year", 2015,2022,2015)

data2 = data2[data2['Year'] == button]
data2 = pd.DataFrame(data2[['State', 'Total Incidents']])
data2.head()

# plot
fig2 = px.bar(data2, x="State", y="Total Incidents", color = "State", title="Flood Incidents by State")
st.plotly_chart(fig2, use_container_width=True)

# indiana_roi_map.py
"""
Indiana County Rental ROI & Property-Tax Heatmap  🗺️🏡
────────────────────────────────────────────────────────────────────────────
Fetches live ACS data and overlays it on a public GeoJSON of US counties.
No shapefiles, no geopandas—runs on Python 3.12 in Streamlit Cloud.
"""
import json, requests, pandas as pd, streamlit as st, folium
from streamlit_folium import folium_static

# ────────────────────────────── ACS DATA ────────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_acs_indiana():
    url = (
        "https://api.census.gov/data/2022/acs/acs5"
        "?get=NAME,B25064_001E,B25077_001E,B25092_001E"
        "&for=county:*&in=state:18"
    )
    resp = requests.get(url, timeout=30).json()
    cols = resp[0]
    df = pd.DataFrame(resp[1:], columns=cols)
    df[["B25064_001E","B25077_001E","B25092_001E"]] = df[
        ["B25064_001E","B25077_001E","B25092_001E"]
    ].astype(float)
    df["fips"] = df["state"] + df["county"]
    df["rental_roi"] = (df["B25064_001E"] * 12) / df["B25077_001E"]
    df["property_tax_rate"] = df["B25092_001E"] / df["B25077_001E"]
    return df[["NAME","fips","rental_roi","property_tax_rate"]]

# ──────────────────── GEOJSON LOAD & FILTER ────────────────────────────
@st.cache_data(show_spinner=False)
def fetch_indiana_counties_geojson():
    url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
    gj = requests.get(url, timeout=30).json()
    # keep only features with fips starting with "18" (Indiana)
    feats = [f for f in gj["features"] if f["id"].startswith("18")]
    return {"type": "FeatureCollection", "features": feats}

# ──────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Indiana ROI & Tax Heatmap", layout="wide")
st.title("📍 Indiana County Rental ROI & Property-Tax Heatmap")

st.info(
    "🔔 **Demo Notice**  \n"
    "Live ACS data + public GeoJSON—no shapefiles or geopandas needed. "
    "For enterprise geospatial analytics, [contact me](https://drtomharty.com/bio).",
    icon="💡"
)

# load data
with st.spinner("Fetching data…"):
    df = fetch_acs_indiana()
    geojson = fetch_indiana_counties_geojson()

# choose metric
metric = st.radio(
    "Select metric",
    ["Rental ROI (%)", "Property Tax Rate (%)"],
    index=0,
    help="ROI = (median rent × 12) ÷ median home value"
)

if metric.startswith("Rental"):
    df["value"] = df["rental_roi"] * 100
    legend = "Rental ROI (%)"
else:
    df["value"] = df["property_tax_rate"] * 100
    legend = "Property Tax Rate (%)"

# build map
m = folium.Map(location=[40.27, -86.13], zoom_start=7, tiles="cartodbpositron")
folium.Choropleth(
    geo_data=geojson,
    data=df,
    columns=["fips", "value"],
    key_on="feature.id",
    fill_color="YlGnBu",
    fill_opacity=0.8,
    line_opacity=0.2,
    legend_name=legend,
).add_to(m)

# tooltip shows both county name and metric
tooltip = folium.features.GeoJsonTooltip(
    fields=["NAME"],
    aliases=["County"],
    labels=True,
    sticky=False
)
folium.GeoJson(
    geojson,
    name="labels",
    style_function=lambda _: {"fillOpacity": 0, "color": "transparent"},
    tooltip=tooltip
).add_to(m)

# add custom tooltips via JavaScript popup on hover
for _, row in df.iterrows():
    folium.features.GeoJson(
        {"type": "Feature", "geometry": next(f["geometry"] for f in geojson["features"] if f["id"] == row.fips)},
        tooltip=folium.Tooltip(f"{row.NAME}: {row.value:.2f}%")
    ).add_to(m)

folium_static(m, width=900, height=600)

# download CSV
st.download_button(
    "⬇️ Download data CSV",
    data=df[["NAME","rental_roi","property_tax_rate"]]
         .rename(columns={"NAME":"county"})
         .to_csv(index=False)
         .encode(),
    file_name="indiana_county_roi_tax.csv",
    mime="text/csv"
)



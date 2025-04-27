# Indiana-ROI-Map

📍 Indiana County Rental ROI & Property-Tax Heatmap
A Streamlit demo that visualizes county-level Rental ROI and Property Tax Rate across Indiana using live U.S. Census ACS data—no API keys required.

🔍 What it does
Fetches the latest ACS 5-year estimates (2022) for:

Median Gross Rent

Median Home Value

Median Property Taxes

Calculates for each Indiana county:

Rental ROI ≈ (Median Rent × 12) ÷ Median Home Value

Tax Rate ≈ Median Taxes ÷ Median Home Value

Joins these metrics to TIGER/Line county shapes (Census shapefile).

Renders an interactive Folium choropleth map—switch between ROI and Tax Rate.

Allows hover tooltips for exact percentages and CSV download of the data.

Proof-of-concept only: no caching layer, authentication, or multi-state support.
For enterprise geospatial analytics solutions, contact me.

✨ Features
Live ACS data (no key needed)

Pure Python & CPU-only: streamlit, geopandas, folium

Interactive map with hover labels and zoom controls

Toggle between Rental ROI (%) and Property Tax Rate (%)

Downloadable county-level CSV

🚀 Quick Start (Local)
bash
Copy
Edit
git clone https://github.com/THartyMBA/indiana-roi-map.git
cd indiana-roi-map
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run indiana_roi_map.py
Open http://localhost:8501 in your browser to explore the map.

☁️ Deploy on Streamlit Cloud (Free)
Push this repo to GitHub under THartyMBA.

Visit Streamlit Community Cloud → New app → select your repo/branch → Deploy.

Share the generated URL—no secrets or tokens needed.

🛠️ Requirements
shell
Copy
Edit
streamlit>=1.32
pandas
geopandas
folium
streamlit-folium
requests
🗂️ Repo Structure
arduino
Copy
Edit
indiana-roi-map/
├─ indiana_roi_map.py    ← single-file Streamlit app
├─ requirements.txt
└─ README.md             ← you’re reading it
📜 License
CC0 1.0 – public-domain dedication. Attribution appreciated but not required.

🙏 Acknowledgements
U.S. Census Bureau ACS API – free demographic data

GeoPandas & Folium – geospatial mapping in Python

Streamlit – rapid data app development

Visualize Indiana’s rental market ROI and tax landscape in seconds!

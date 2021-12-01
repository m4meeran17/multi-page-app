import streamlit as st
from dashboardapp import DashboardApp
from apps import home, data # import your app modules here
# , trends, validator 

app = DashboardApp()

st.markdown("""
# Dashboard - Edvoy Data Engineering Team

This is a dashboard to Export, Import and process data in a smoother way.

""")

# Add all your application here
app.add_app("Home", home.app)
app.add_app("Data", data.app)
# app.add_app("Trends", trends.app)
# app.add_app("QC Review", validator.app)
# The main app
app.run()

import streamlit as st

pg = st.navigation([
    st.Page("pages/1_Home.py"),
    st.Page("pages/2_File_Upload.py"),
    st.Page("pages/3_OMOP_Matching.py")
    ])
pg.run()

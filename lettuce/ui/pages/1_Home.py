import streamlit as st

st.set_page_config(page_title="Lettuce", page_icon="🥬", layout="wide")
st.title("Lettuce")
st.markdown("""
## Welcome to Lettuce!

This application helps you standardise source terms to OMOP's standard vocabularies by:

1. **Uploading** a list of medication names
2. **Matching** them against OMOP vocabularies
3. **Enhancing** unmatched terms with vector search and LLM capabilities
4. **Approving** matches and downloading results

### Getting Started

Go to `File Upload` and add a file!
""")


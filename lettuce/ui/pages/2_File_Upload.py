import streamlit as st
import pandas as pd

st.title("Upload Your Data")
st.markdown("""
Upload a CSV or Excel file containing your medication names. 
Then select which column contains the medication names you want to standardize.
""")

uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "xls"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.session_state.data = df
        st.success(f"Successfully loaded file with {len(df)} rows and {len(df.columns)} columns")
        
        st.dataframe(df.head())
        
        column = st.selectbox("Select the column containing medication names:", df.columns)
        
        if st.button("Confirm Selection", key="confirm_column"):
            # Ensure the column contains string data
            df[column] = df[column].astype(str)
            # Remove duplicates and empty strings
            medication_names = df[column].unique().tolist()
            medication_names = [name for name in medication_names if name and name.strip()]
            
            st.session_state.selected_column = column
            st.session_state.queries = medication_names
            st.success(f"Selected {len(medication_names)} unique medication names from column '{column}'")
            
            
    except Exception as e:
        st.error(f"Error loading file: {e}")


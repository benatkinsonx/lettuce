import streamlit as st
from omop import OMOP_match
from components.result import LettuceResult
from utils.logging_utils import logger

st.title("OMOP Database Matching")
st.markdown("""
Now we'll attempt to match your medication names against the OMOP database.
You can adjust the search threshold to control match strictness.
""")

# Display the queries
st.subheader("Medication Names to Match")
st.write(st.session_state.queries)

# OMOP matching options
col1, col2 = st.columns(2)

with col1:
    vocabulary_id = st.text_input(
        "Vocabulary IDs (comma-separated)",
        placeholder="RxNorm,SNOMED",
        help="Vocabulary IDs to be queried. Leave empty for all."
    )
    
    if vocabulary_id:
        vocabulary_id = vocabulary_id.split(",")

with col2:
    search_threshold = st.slider(
        "Search Threshold",
        min_value=50,
        max_value=100,
        value=80,
        help="Minimum similarity score (%) required for a match"
    )


if st.button("Run OMOP Matching", key="run_omop", type="primary"):
    with st.spinner("Querying OMOP database..."):
        db_results = OMOP_match.run(search_term=st.session_state.queries, logger=logger, vocabulary_id=vocabulary_id)
        results = []
        
        for i, (query, matches) in enumerate(zip(st.session_state.queries, db_results)):
            result = LettuceResult(query)
            result.add_matches(matches, search_threshold)
            results.append(result)
            
        
        st.session_state.db_results = results
st.session_state.approved_matches = {}
if st.session_state.db_results:
    st.subheader("OMOP Match Results")
    
    for i, result in enumerate(st.session_state.db_results):
        query = result.search_term
        if hasattr(result, "omop_matches") and result.omop_matches:
            if result.omop_matches["CONCEPT"]:
                n_matches = len(result.omop_matches["CONCEPT"])
            else:
                n_matches = 0
            with st.expander(f"Query: '{query}' - {n_matches} matches"):
                if n_matches != 0:
                    st.markdown("#### Matches:")

                    for j, match in enumerate(result.omop_matches["CONCEPT"]):
                        concept_name, vocabulary_id, concept_id, concept_name_similarity_score, approve_button = st.columns([5, 2, 2, 2, 3])
                        with concept_name:
                            st.write(match['concept_name'])
                        with vocabulary_id:
                            st.write(match["vocabulary_id"])
                        with concept_id:
                            st.write(match["concept_id"])
                        with concept_name_similarity_score:
                            st.write(f"Score: {match['concept_name_similarity_score']:.2f}%")
                        with approve_button:
                            match_key = f"{query}_{match['concept_id']}"
                            if st.button("Approve", key=f"approve_{i}_{j}"):
                                st.session_state.approved_matches[query] = match
                                st.success(f"Approved match for '{query}'")

    st.markdown("---")
    
    approved_count = len(st.session_state.approved_matches)
    remaining = len(st.session_state.queries) - approved_count
    
    st.write(f"Approved matches: {approved_count} / {len(st.session_state.queries)}")
    
    col1, col2 = st.columns(2)

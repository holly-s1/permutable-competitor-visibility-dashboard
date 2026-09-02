import streamlit as st
import pandas as pd

st.title("Permutable Competitor Dashboard")

uploaded_file = st.file_uploader("Upload Data", type=["csv", "txt"])

@st.cache_data
def load_data(file):
    return pd.read_csv(file)

if uploaded_file is not None:
    df = load_data(uploaded_file)

    #Clean competitor names
    all_competitors = (
        df["Competitors Mentioned"]
        .dropna()
        .str.split(";")
        .explode()
        .str.strip()
    )
    comp_counts = all_competitors.value_counts()

    #Show permutable count
    if "Mention?" in df.columns:
        #Count rows where Mention? is "Yes"
        permutable_count = (
            df["Mention?"]
               .astype(str)
               .str.strip()
               .str.lower()
               .eq("yes")
               .sum()
        )
    else:
        permutable_count = 0
    st.metric(
        label="Permutable Mentions", 
        value=f"{permutable_count} out of {len(df)}"
        )

    #Bar chart
    st.write("**Most Mentioned Companies**")
    st.bar_chart(comp_counts)

    #Filter by AI Tool
    if "AI Tool" in df.columns:
        st.write("**Companies mentioned by AI Tool**")
        tool = st.selectbox("Choose AI Tool:", df["AI Tool"].unique())
        filtered_df = df[df["AI Tool"] == tool]
        tool_comps = (
            filtered_df["Competitors Mentioned"]
            .dropna()
            .str.split(";")
            .explode()
            .str.strip()
        )
        st.bar_chart(tool_comps.value_counts())

    #Cited sources
    if "Citations" in df.columns:
        st.write("**Most Cited Sources (2+ Citations)**")
        citations = (
            df["Citations"].dropna().str.split(";").explode().str.strip()
        )
        citation_counts = citations.value_counts()

        #Keep only 2+ citations
        filtered_citations = citation_counts[citation_counts >= 2]

        st.bar_chart(filtered_citations)
    
    #Weekly Summary
    st.markdown("### Weekly Summary")

    top_company = comp_counts.index[0]

    #Filter rows where Permutable was mentioned
    if "Mention?" in df.columns:
        permutable_df = df[df["Mention?"].astype(str).str.strip().str.lower().eq("yes")]
        p_count = len(permutable_df)
    else:
        permutable_df = pd.DataFrame()
        p_count = 0
    
    #Count how many citations
    if "Citations" in df.columns:
        cited_count = (
            df["Citations"]
            .dropna()
            .astype(str)
            .str.lower()
            .str.contains("permutable")
            .sum()
        )
    else:
        cited_count = 0

    #Display
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Top Competitor", value=top_company)
    col2.metric(label="Permutable Visibility", value=f"{p_count} prompt(s)")
    col3.metric(label="Permutable Citations", value=f"{cited_count} citation(s)")

    #Detailed mention breakdown
    if not permutable_df.empty:
        with st.container(border=True):
            st.markdown("**Permutable Mentions Breakdown**")

            if "AI Tool" in permutable_df.columns:
                tools = ", ".join(permutable_df["AI Tool"].dropna().unique())
                st.write(f"**AI Tools:** {tools}")

            if "Prompt" in permutable_df.columns:
                st.write("**Prompts:**")
                for p in permutable_df["Prompt"].dropna().unique():
                    st.markdown(f"- *\"{p}\"*")

    #Raw DF
    with st.expander("View Raw Data Table"):
        st.dataframe(df)

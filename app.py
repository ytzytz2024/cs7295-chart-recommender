import os
import json
import streamlit as st
import pandas as pd
import altair as alt
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------
#  Setup
# ---------------------------
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="AI-Driven Chart Recommender",
    layout="wide"
)

st.title("📊 AI-Driven Chart Recommender (Auto-Intent Version)")
st.write("Upload a dataset and let the AI automatically infer analytical intents and generate a full visualization gallery.")

# ---------------------------
#  Utility: Analyze Data
# ---------------------------
def analyze_data(df: pd.DataFrame):
    """Return simple metadata about each column: type & unique count."""
    meta = {}
    for col in df.columns:
        series = df[col]

        # Basic type detection
        if pd.api.types.is_numeric_dtype(series):
            col_type = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(series):
            col_type = "datetime"
        else:
            # Try to coerce to datetime
            try:
                parsed = pd.to_datetime(series, errors="raise")
                df[col] = parsed
                col_type = "datetime"
            except Exception:
                col_type = "categorical"

        meta[col] = {
            "type": col_type,
            "n_unique": series.nunique()
        }

    return meta, df

# ---------------------------
#  Utility: Call LLM
# ---------------------------
def ask_llm_for_charts(metadata, x_col, y_col):
    """
    Let AI infer possible analytical intents and recommend charts accordingly.
    """
    system_prompt = """
You are a data visualization expert.
Given metadata about a dataset and selected variables, infer all reasonable analytical intents and
recommend MULTIPLE chart types.

For each recommended chart you MUST include:
- chart_type
- intent (the inferred analytical purpose)
- title
- strengths
- weaknesses
- when_to_use

Respond in STRICT JSON with this schema:

{
  "recommendations": [
    {
      "chart_type": "line" | "bar" | "scatter" | "area" | "histogram" | "boxplot",
      "intent": "string",
      "title": "string",
      "strengths": "string",
      "weaknesses": "string",
      "when_to_use": "string"
    }
  ]
}

No markdown. No commentary. Only valid JSON.
    """

    user_content = {
        "metadata": metadata,
        "x_column": x_col,
        "y_column": y_col
    }

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_content)}
        ]
    )

    text = response.output[0].content[0].text

    try:
        return json.loads(text)
    except:
        return {"recommendations": []}

def ask_llm_for_summary(df, metadata):
    """
    Let AI generate a short summary of the dataset.
    """
    system_prompt = """
You are a data visualization expert. 
Given a dataset and its inferred metadata, provide a concise and helpful analytical summary.
The summary should include:
- What the dataset appears to be about
- Key variables and their types
- Interesting patterns or expectations that could be explored later
- Potential high-level questions the dataset might answer

Your response MUST be plain text (no JSON, no markdown formatting).
"""

    # For safety, only send the first 20 rows to avoid huge prompts
    sample_df = df.head(20).to_dict(orient="records")

    user_content = {
        "metadata": metadata,
        "sample_rows": sample_df
    }

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(user_content)}
        ]
    )

    # plain text output
    try:
        summary = response.output[0].content[0].text
        return summary.strip()
    except:
        return "AI could not generate a summary for this dataset."


# ---------------------------
#  Utility: Create Altair Chart
# ---------------------------
def create_chart(df, x_col, y_col, chart_type, title):
    if chart_type == "line":
        chart = alt.Chart(df).mark_line().encode(
            x=x_col,
            y=y_col
        ).properties(title=title)

    elif chart_type == "bar":
        chart = alt.Chart(df).mark_bar().encode(
            x=x_col,
            y=y_col
        ).properties(title=title)

    elif chart_type == "scatter":
        chart = alt.Chart(df).mark_point().encode(
            x=x_col,
            y=y_col
        ).properties(title=title)

    elif chart_type == "area":
        chart = alt.Chart(df).mark_area().encode(
            x=x_col,
            y=y_col
        ).properties(title=title)

    elif chart_type == "histogram":
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X(f"{x_col}:Q", bin=True),
            y="count()"
        ).properties(title=title)

    elif chart_type == "boxplot":
        chart = alt.Chart(df).mark_boxplot().encode(
            x=f"{x_col}:N",
            y=f"{y_col}:Q"
        ).properties(title=title)

    else:
        chart = alt.Chart(df).mark_point().encode(
            x=x_col,
            y=y_col
        ).properties(title=title)

    return chart

# ---------------------------
#  Streamlit UI
# ---------------------------
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Data Preview")
    st.dataframe(df.head())

    metadata, df = analyze_data(df)

    st.subheader("Select X and Y Variables (AI will infer intents automatically)")

    cols = list(df.columns)
    x_col = st.selectbox("X-axis variable", cols)
    y_col = st.selectbox("Y-axis variable", cols, index=min(1, len(cols)-1))

    if st.button("🔍 Generate AI Visualization Gallery"):
        with st.spinner("AI is analyzing your dataset..."):
            summary = ask_llm_for_summary(df, metadata)
            rec = ask_llm_for_charts(metadata, x_col, y_col)

        # -----------------------------
        # SHOW SUMMARY FIRST
        # -----------------------------
        st.subheader("📘 Dataset Summary (Generated by AI)")
        st.write(summary)

        # -----------------------------
        # THEN SHOW GALLERY
        # -----------------------------
        st.subheader("📊 Visualization Gallery Generated by AI")

        if len(rec.get("recommendations", [])) == 0:
            st.warning("AI could not generate recommendations. Please try another X/Y combination.")
        else:
            for i, r in enumerate(rec["recommendations"], start=1):
                chart_type = r["chart_type"]
                title = r["title"]

                st.markdown(f"### {i}. {title} ({chart_type})")
                st.caption(f"**Intent:** {r['intent']}")
                st.caption(f"**Strengths:** {r['strengths']}")
                st.caption(f"**Weaknesses:** {r['weaknesses']}")
                st.caption(f"**When to use:** {r['when_to_use']}")

                try:
                    chart = create_chart(df, x_col, y_col, chart_type, title)
                    st.altair_chart(chart, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not render {chart_type} chart: {e}")

else:
    st.info("👆 Please upload a CSV file to get started.")


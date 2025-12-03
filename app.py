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

st.title("📊 AI-Driven Chart Recommender")
st.write("Upload a dataset, choose variables, and let the AI suggest suitable charts with explanations.")

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
            # Try to parse as datetime if many values look like dates
            try:
                parsed = pd.to_datetime(series, errors="raise")
                df[col] = parsed  # mutate df in place
                col_type = "datetime"
            except Exception:
                col_type = "categorical"
        meta[col] = {
            "type": col_type,
            "n_unique": series.nunique(),
        }
    return meta, df

# ---------------------------
#  Utility: Call LLM
# ---------------------------
def ask_llm_for_charts(metadata, x_col, y_col, intent):
    """
    Call GPT model to recommend chart types.
    Returns a Python dict with a list of chart suggestions.
    """
    system_prompt = """
You are a data visualization expert. 
Given metadata about a dataset, the selected X and Y variables, and the user's analysis intent, 
you recommend appropriate chart types.

You MUST respond in strict JSON with the following schema:

{
  "recommendations": [
    {
      "chart_type": "line" | "bar" | "scatter" | "area" | "histogram" | "boxplot",
      "title": "string",
      "reason": "string explaining why this chart fits"
    },
    ...
  ]
}
No extra text, no markdown, only valid JSON.
    """

    user_content = {
        "metadata": metadata,
        "x_column": x_col,
        "y_column": y_col,
        "intent": intent
    }

    response = client.responses.create(
    model="gpt-4.1-mini",   # or gpt-4o-mini
    input=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": json.dumps(user_content)
        }
    ]
)

    # Responses API returns content as a list of output items
    text = response.output[0].content[0].text

    try:
        data = json.loads(text)
        return data
    except json.JSONDecodeError:
        # Fallback: wrap text as plain reason with a default chart
        return {
            "recommendations": [
                {
                    "chart_type": "bar",
                    "title": "Bar chart (fallback)",
                    "reason": "Model response could not be parsed as JSON. Showing a fallback bar chart."
                }
            ]
        }

# ---------------------------
#  Utility: Create Altair Chart
# ---------------------------
def create_chart(df, x_col, y_col, chart_type, title):
    if chart_type == "line":
        chart = alt.Chart(df).mark_line().encode(
            x=f"{x_col}",
            y=f"{y_col}"
        ).properties(title=title)

    elif chart_type == "bar":
        chart = alt.Chart(df).mark_bar().encode(
            x=f"{x_col}",
            y=f"{y_col}"
        ).properties(title=title)

    elif chart_type == "scatter":
        chart = alt.Chart(df).mark_point().encode(
            x=f"{x_col}",
            y=f"{y_col}"
        ).properties(title=title)

    elif chart_type == "area":
        chart = alt.Chart(df).mark_area().encode(
            x=f"{x_col}",
            y=f"{y_col}"
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
            x=f"{x_col}",
            y=f"{y_col}"
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

    st.subheader("Select Variables & Intent")

    cols = list(df.columns)
    x_col = st.selectbox("X-axis variable", cols)
    y_col = st.selectbox("Y-axis variable", cols, index=min(1, len(cols)-1))

    intent = st.selectbox(
        "Analysis intent",
        [
            "Show trend over time",
            "Compare categories",
            "Show distribution",
            "Explore correlation between variables"
        ]
    )

    if st.button("🔍 Recommend Charts"):
        with st.spinner("Asking the AI for chart recommendations..."):
            rec = ask_llm_for_charts(metadata, x_col, y_col, intent)

        st.subheader("Recommendations")

        for i, r in enumerate(rec.get("recommendations", []), start=1):
            chart_type = r.get("chart_type", "bar")
            title = r.get("title", f"{chart_type.title()} Chart")
            reason = r.get("reason", "")

            st.markdown(f"### {i}. {title} ({chart_type})")
            st.markdown(f"**Why this chart?** {reason}")

            try:
                chart = create_chart(df, x_col, y_col, chart_type, title)
                st.altair_chart(chart, use_container_width=True)
            except Exception as e:
                st.error(f"Could not render {chart_type} chart: {e}")
else:
    st.info("👆 Please upload a CSV file to get started.")

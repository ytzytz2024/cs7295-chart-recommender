# 📊 AI-Driven Chart Recommender  
*A CS7295 VisGenAI Project*  

This project is an **AI-driven visualization assistant** that automatically analyzes a dataset, infers potential analytical intents, and generates a **gallery of recommended visualizations** — each accompanied by explanations, strengths, weaknesses, and suggestions for when to use each chart.

The system is built using **Streamlit**, **Altair**, **Pandas**, and the **OpenAI API**.

---

## ⭐ Features

### 🔍 Automatic Intent Inference  
No manual selection of analytical goals.  
The AI examines dataset metadata and infers meaningful analytical intents (trend, category comparison, distribution, correlation, etc.).

### 📊 Multi-Chart Recommendation Gallery  
For each inferred intent, the AI recommends multiple charts (line, bar, scatter, histogram, boxplot, area) with:

- chart title  
- inferred intent  
- strengths  
- weaknesses  
- when to use  

### 📘 Dataset Summary  
Before showing the chart gallery, AI produces a concise **dataset summary**, describing variable types, possible insights, and analytical angles.

### 🧩 Visualization Rendering  
All charts are rendered via Altair directly in Streamlit.

---

# 🚀 Setup Instructions

Follow these steps to run the project locally.

---

## 1. Clone the Repository

\`\`\`bash
git clone https://github.com/ytzytz2024/cs7295-chart-recommender.git
cd cs7295-chart-recommender
\`\`\`

---

## 2. Create a Virtual Environment (Recommended)

\`\`\`bash
python3 -m venv .venv
source .venv/bin/activate   # macOS / Linux

## 3. Install Dependencies

The project uses \`requirements.txt\`. Install everything with:

\`\`\`bash
pip install -r requirements.txt
\`\`\`

Dependencies include:

- streamlit  
- pandas  
- altair  
- python-dotenv  
- openai  

---

## 4. Set Up OpenAI API Key

This app uses the **OpenAI Responses API**.  
You must:

### Step 4.1 — Create an API Key  
Go to: https://platform.openai.com  
- Log in  
- Go to **API Keys**  
- Create a new key  

### Step 4.2 — Add key to \`.env\`  
In the project root, create a file named:

\`\`\`
.env
\`\`\`

Put your key inside:

\`\`\`
OPENAI_API_KEY=your_api_key_here
\`\`\`

⚠️ Do **not** commit \`.env\` to GitHub.

---

## 5. Run the App

Start Streamlit with:

\`\`\`bash
streamlit run app.py
\`\`\`

This will open the app in your browser at:

\`\`\`
http://localhost:8501
\`\`\`

---

# 📁 Usage

1. Upload any CSV file  
2. Select **X-axis** and **Y-axis** variables  
3. Click **Generate AI Visualization Gallery**  
4. The system will produce:  
   - 📘 AI-generated dataset summary  
   - 📊 Visualization gallery  
   - 📝 Explanations (intent, strengths, weaknesses, when to use)

---

# 🛠 Project Structure

\`\`\`
.
├── app.py               # Main Streamlit application
├── requirements.txt     # Dependencies
├── .env                 # (local only) API key
└── README.md            # Documentation
\`\`\`

---

# 🧠 Model Behavior

- AI is not given any preset analytical intents.  
- It infers intents automatically based on metadata (numeric/categorical/datetime).  
- AI chooses chart types **only** from the allowed schema defined in the prompt:
  - line  
  - bar  
  - scatter  
  - area  
  - histogram  
  - boxplot  

You can extend this schema anytime to add more chart types.

---

# 📌 Notes

- Recommended OpenAI model: **gpt-4.1-mini** (cheap and fast)  
- Only first 20 rows of data are sent to the AI for efficiency  
- If AI cannot parse or respond correctly, a safe fallback is used  

---

# 🏁 Future Enhancements (Optional)

- AI automatically selects X/Y variables  
- Support more chart types (heatmaps, stacked bar, scatter matrix, etc.)  
- Better layout (grid gallery, side-by-side display)  
- Add download buttons for charts  

---

# 🤝 Acknowledgements

CS7295 — Visualization & Generative AI  
Northeastern University  

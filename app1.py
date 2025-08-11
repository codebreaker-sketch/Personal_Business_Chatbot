import streamlit as st
import pandas as pd
import re
import json
import time
import asyncio
import google.generativeai as genai
import matplotlib.pyplot as plt  # For bar chart
from googletrans import Translator  # For translation
from matplotlib import ticker

# ---------------------------
# Configure Gemini + translator
# ---------------------------
genai.configure(api_key="AIzaSyCrD1cA9Ee2w2x-nAo-TV96j0XoqHbexz4")
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
translator = Translator()

# ---------------------------
# Utilities & data helpers
# ---------------------------
def summarize_data(df):
    """
    Build a human-readable summary_text and a structured country_sales_json (dict).
    """
    # Ensure invoice_date column is datetime
    df['invoice_month'] = df['invoice_date'].dt.to_period('M')
    monthly_sales = df.groupby('invoice_month')['invoice_amount_usd'].sum()
    df['invoice_year'] = df['invoice_date'].dt.year
    yearly_sales = df.groupby('invoice_year')['invoice_amount_usd'].sum()
    country_sales = df.groupby('country')['invoice_amount_usd'].sum()
    country_sales_json = country_sales.to_dict()

    total_disputed = int(df[df['disputed'] == True].shape[0]) if 'disputed' in df.columns else 0
    avg_days_late = float(df['days_late'].mean()) if 'days_late' in df.columns else 0.0
    total_invoices = int(df.shape[0])

    summary_text = f"""Invoice Data Summary:

🧾 Total Invoices: {total_invoices}
💰 Yearly Sales:
{yearly_sales.to_string()}

📆 Monthly Sales:
{monthly_sales.to_string()}

🌍 Country-wise Sales:
{country_sales.to_string()}

⚠️ Disputed Invoices: {total_disputed}
🐢 Average Days Late: {avg_days_late:.2f}
"""
    return summary_text, country_sales_json

def _maybe_parse_sales(sales):
    """
    Accept a dict or a JSON string and return a dict.
    """
    if isinstance(sales, dict):
        return sales
    if isinstance(sales, str):
        try:
            return json.loads(sales)
        except Exception:
            # Fallback: try eval (only if you trust the source) - avoid if untrusted
            try:
                return eval(sales)
            except Exception:
                return {}
    return {}

def _translate_answer_sync_safe(answer: str, target_lang: str):
    """
    Translate 'answer' to target_lang. Handles both sync and async translator implementations.
    """
    if target_lang == "en":
        return answer

    try:
        translated = translator.translate(answer, dest=target_lang)
        # If translator.translate returned a coroutine (async), handle it
        if asyncio.iscoroutine(translated):
            translated = asyncio.run(translated)  # run coroutine to completion
        return getattr(translated, "text", str(translated))
    except Exception:
        # As a fallback, return the original English answer
        return answer

# ---------------------------
# Core Q/A function (robust)
# ---------------------------
def ask_invoice_question(summary_text, user_query, country_sales_json, target_lang="en"):
    """
    Uses local numeric logic for 'highest' and 'lowest' style queries to guarantee correctness,
    otherwise falls back to the LLM. Returns translated text if target_lang != 'en'.
    """
    sales_data = _maybe_parse_sales(country_sales_json)
    lower_query = user_query.lower().strip()

    # ----- handle highest sales (with ties) -----
    if "highest sales" in lower_query or "which country had the highest" in lower_query:
        if sales_data:
            max_value = max(sales_data.values())
            winners = [c for c, v in sales_data.items() if v == max_value]
            if len(winners) == 1:
                answer = f"{winners[0]} with sales of {max_value:,}"
            else:
                winners_text = ", ".join(winners)
                answer = f"{winners_text} (tied) with sales of {max_value:,}"
        else:
            answer = "Not available."
        return _translate_answer_sync_safe(answer, target_lang)

    # ----- handle two lowest sales (or 'lowest') -----
    if "two lowest" in lower_query or ("lowest sales" in lower_query and "two" in lower_query) or lower_query.startswith("two countries"):
        if sales_data and len(sales_data) >= 1:
            sorted_sales = sorted(sales_data.items(), key=lambda x: x[1])
            lowest_two = sorted_sales[:2] if len(sorted_sales) >= 2 else sorted_sales
            parts = [f"{country} ({value:,})" for country, value in lowest_two]
            answer = " and ".join(parts)
        else:
            answer = "Not available."
        return _translate_answer_sync_safe(answer, target_lang)

    # ----- otherwise, call the LLM -----
    prompt = f"""
You are a smart financial assistant. Use the following invoice data summary and structured country sales data to answer the user question.

--- Invoice Summary ---
{summary_text}

--- Structured Country Sales ---
{json.dumps(sales_data)}

Now answer this user question: "{user_query}"

Be precise. If the answer is not in the data, respond with "Not available."
"""
    # Call Gemini
    try:
        response = model.generate_content(prompt)
        answer = getattr(response, "text", str(response))
    except Exception as e:
        answer = f"Error calling LLM: {e}"

    # Translate if requested (safe wrapper)
    return _translate_answer_sync_safe(answer, target_lang)

# ---------------------------
# Plotting: dynamic colors + highlight two lowest
# ---------------------------
def plot_country_sales(country_sales_json):
    sales = _maybe_parse_sales(country_sales_json)
    if not sales:
        st.info("No country sales to plot.")
        return

    countries = list(sales.keys())
    values = [sales[c] for c in countries]

    # Sort for nicer visuals (descending)
    sorted_pairs = sorted(zip(countries, values), key=lambda x: x[1], reverse=True)
    countries_sorted, values_sorted = zip(*sorted_pairs)

    # Colors: use matplotlib tab20 palette, recycle if needed
    cmap = plt.cm.get_cmap("tab20")
    base_colors = [cmap(i % cmap.N) for i in range(len(countries_sorted))]

    # Highlight the two lowest countries in a distinct color (e.g., 'tomato')
    lowest_two = sorted_pairs[-2:] if len(sorted_pairs) >= 2 else sorted_pairs[-len(sorted_pairs):]
    lowest_names = {name for name, _ in lowest_two}

    colors = []
    for name in countries_sorted:
        if name in lowest_names:
            colors.append("tomato")  # highlight color
        else:
            # pick a base color
            idx = countries_sorted.index(name)
            colors.append(base_colors[idx])

    # Plot
    fig, ax = plt.subplots(figsize=(8, 4))
    bars = ax.bar(countries_sorted, values_sorted, color=colors, edgecolor="black")

    # Format y-axis with commas
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x):,}"))

    ax.set_title("Country Sales")
    ax.set_ylabel("Sales (USD)")
    ax.set_xlabel("Country")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    st.pyplot(fig)

# ---------------------------
# UI: polished Streamlit layout
# ---------------------------
def main():
    st.set_page_config(page_title="Invoice Data Assistant", layout="wide")
    # Custom header
    st.markdown(
        """
        <style>
        .app-header {
            background: linear-gradient(90deg,#0f172a,#0ea5a6);
            padding: 18px;
            border-radius: 12px;
            color: white;
        }
        .app-title {
            font-size: 28px;
            font-weight: 700;
            margin: 0;
        }
        .app-sub {
            font-size: 13px;
            opacity: 0.9;
            margin: 0;
        }
        .card {
            background: #ffffff;
            border-radius: 10px;
            padding: 12px;
            box-shadow: 0 4px 12px rgba(15,23,42,.06);
        }
        </style>
        <div class="app-header">
            <div class="app-title">📊 Invoice Data Assistant</div>
            <div class="app-sub">Upload invoice CSV → get summaries, charts & ask questions (multilingual)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")  # spacer

    # Two-column layout for upload + controls vs summary/chart
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("### 🔁 Controls", unsafe_allow_html=True)

        # Language selection
        lang_map = {
            "English": "en",
            "French": "fr",
            "Spanish": "es",
            "German": "de",
            "Chinese (Simplified)": "zh-cn",
            "Arabic": "ar"
        }
        selected_lang_label = st.selectbox("Select response language:", list(lang_map.keys()))
        target_lang = lang_map[selected_lang_label]

        uploaded_file = st.file_uploader("📂 Upload your invoice CSV file", type=["csv"])
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file, parse_dates=['invoice_date', 'due_date', 'settled_date'])
            except Exception as e:
                st.error(f"Error loading CSV: {e}")
                return

            st.success("CSV loaded successfully!")

            if st.button("🧾 Generate Summary"):
                # small simulated wait for UX
                with st.spinner("Summarizing data..."):
                    time.sleep(0.6)
                    summary_text, country_sales_json = summarize_data(df)
                    st.session_state['summary_text'] = summary_text
                    st.session_state['country_sales_json'] = country_sales_json
                    st.session_state['conversation'] = []
                st.experimental_rerun()

        st.markdown("---")
        st.markdown("### 💡 Quick Examples")
        st.write(
            """
            • Which country had the highest sales?  
            • Two countries with the lowest sales?  
            • What are the total sales in 2021?
            """
        )

    with right_col:
        # Display summary + chart area
        if 'summary_text' in st.session_state and 'country_sales_json' in st.session_state:
            # Summary inside an expander
            with st.expander("📄 Invoice Summary (click to expand)"):
                st.text_area("", st.session_state['summary_text'], height=320, disabled=True)

            # Chart area card
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown("### 📈 Country Sales Chart")
            plot_country_sales(st.session_state['country_sales_json'])
            st.markdown("</div>", unsafe_allow_html=True)

            # Chat-style Q&A area
            st.markdown("### 💬 Ask the Assistant")
            # prefer chat_input if available (Streamlit >=1.18)
            try:
                # Streamlit chat components (if available)
                user_query = st.chat_input("Ask a question about the invoice data...", key="chat_input")
            except Exception:
                # fallback to text_input
                user_query = st.text_input("Ask a question about the invoice data:", key="text_input")

            # Prefill examples dropdown below input for convenience
            example_questions = [
                "What are the total sales in 2021?",
                "Which country had the highest sales?",
                "Two countries with the lowest sales?",
                "How many invoices are disputed?",
                "What is the average days late to settle?",
                "Show monthly sales for 2020",
                "How many invoices were settled late?"
            ]
            selected_example = st.selectbox("Or choose a sample question:", [""] + example_questions, key="examples")

            if selected_example:
                user_query = selected_example

            if user_query:
                # Add spinner and call QA
                with st.spinner("Processing your question..."):
                    # small UX delay
                    time.sleep(0.4)
                    answer = ask_invoice_question(
                        st.session_state['summary_text'],
                        user_query,
                        st.session_state['country_sales_json'],
                        target_lang
                    )

                # Save conversation
                if 'conversation' not in st.session_state:
                    st.session_state['conversation'] = []
                st.session_state['conversation'].append((user_query, answer))

            # Display conversation (chat bubbles if available)
            if 'conversation' in st.session_state and st.session_state['conversation']:
                st.markdown("### 🧾 Conversation History")
                for q, a in reversed(st.session_state['conversation']):  # newest first
                    # try chat_message if available
                    try:
                        st.chat_message("user").write(q)
                        st.chat_message("assistant").write(a)
                    except Exception:
                        st.markdown(f"**You:** {q}")
                        st.markdown(f"**Assistant:** {a}")
                        st.markdown("---")

        else:
            st.info("Upload a CSV and click 'Generate Summary' to begin.")

    # Footer / small help
    st.markdown("---")
    st.markdown(
        """
        **Tips:**  
        - Use the language selector to get answers in your preferred language.  
        - The two countries with the lowest sales are highlighted in the chart.  
        - For numeric comparisons (highest/lowest) the assistant uses exact numbers to avoid mistakes.
        """
    )

if __name__ == "__main__":
    main()

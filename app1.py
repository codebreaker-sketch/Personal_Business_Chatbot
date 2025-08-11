# import streamlit as st
# import pandas as pd
# import re
# import google.generativeai as genai

# # Configure Gemini with your API key
# genai.configure(api_key="AIzaSyCrD1cA9Ee2w2x-nAo-TV96j0XoqHbexz4")
# model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# def summarize_data(df):
#     df['invoice_month'] = df['invoice_date'].dt.to_period('M')
#     monthly_sales = df.groupby('invoice_month')['invoice_amount_usd'].sum()
#     df['invoice_year'] = df['invoice_date'].dt.year
#     yearly_sales = df.groupby('invoice_year')['invoice_amount_usd'].sum()
#     country_sales = df.groupby('country')['invoice_amount_usd'].sum()
#     country_sales_json = country_sales.to_dict()

#     total_disputed = df[df['disputed'] == True].shape[0]
#     avg_days_late = df['days_late'].mean()
#     total_invoices = df.shape[0]

#     summary_text = f"""Invoice Data Summary:

# 🧾 Total Invoices: {total_invoices}
# 💰 Yearly Sales:
# {yearly_sales.to_string()}

# 📆 Monthly Sales:
# {monthly_sales.to_string()}

# 🌍 Country-wise Sales:
# {country_sales.to_string()}

# ⚠️ Disputed Invoices: {total_disputed}
# 🐢 Average Days Late: {avg_days_late:.2f}
# """
#     return summary_text, country_sales_json


# def ask_invoice_question(summary_text, user_query, country_sales_json):
#     prompt = f"""
# You are a smart financial assistant. Use the following invoice data summary and structured country sales data to answer the user question.

# --- Invoice Summary ---
# {summary_text}

# --- Structured Country Sales ---
# {country_sales_json}

# Now answer this user question: "{user_query}"

# Be precise. If the answer is not in the data, respond with "Not available."
# """
#     response = model.generate_content(prompt)
#     return response.text



# def main():
#     st.set_page_config(page_title="Invoice Data Assistant", layout="centered")
#     st.title("Invoice Data Assistant 💼")

#     uploaded_file = st.file_uploader("Upload your invoice CSV file", type=["csv"])
#     if uploaded_file is not None:
#         try:
#             df = pd.read_csv(uploaded_file, parse_dates=['invoice_date', 'due_date', 'settled_date'])
#         except Exception as e:
#             st.error(f"Error loading CSV: {e}")
#             return

#         st.success("CSV loaded successfully!")

#         if st.button("Generate Summary"):
#             summary_text, country_sales_json = summarize_data(df)
#             st.session_state['summary_text'] = summary_text
#             st.session_state['country_sales_json'] = country_sales_json
#             st.session_state['conversation'] = []
#             st.experimental_rerun()

#     if 'summary_text' in st.session_state and 'country_sales_json' in st.session_state:
#         st.subheader("Invoice Summary")
#         st.text_area("", st.session_state['summary_text'], height=300, disabled=True)

#         example_questions = [
#             "What are the total sales in 2021?",
#             "Which country had the highest sales?",
#             "Two countries with the lowest sales?",
#             "How many invoices are disputed?",
#             "What is the average days late to settle?",
#             "Show monthly sales for 2020",
#             "How many invoices were settled late?"
#         ]
#         selected_example = st.selectbox("Or choose a sample question:", [""] + example_questions)

#         if 'user_input' not in st.session_state:
#             st.session_state['user_input'] = ""

#         if selected_example:
#             st.session_state['user_input'] = selected_example

#         user_query = st.text_input("Ask a question about the invoice data:", value=st.session_state['user_input'])

#         if st.button("Get Answer"):
#             if user_query:
#                 if 'conversation' not in st.session_state:
#                     st.session_state['conversation'] = []

#                 with st.spinner("Processing..."):
#                     answer = ask_invoice_question(
#                         st.session_state['summary_text'],
#                         user_query,
#                         st.session_state['country_sales_json']
#                     )

#                 st.session_state['conversation'].append((user_query, answer))
#                 st.session_state['user_input'] = ""

#                 st.markdown("### Conversation History")
#                 for q, a in st.session_state['conversation']:
#                     st.markdown(f"**You:** {q}")
#                     st.markdown(f"**Assistant:** {a}")
#                     st.markdown("---")
#             else:
#                 st.warning("Please enter a question.")

# if __name__ == "__main__":
#     main()


# import streamlit as st
# import pandas as pd
# import re
# import google.generativeai as genai

# # Configure Gemini with your API key
# genai.configure(api_key="AIzaSyCrD1cA9Ee2w2x-nAo-TV96j0XoqHbexz4")
# model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

# def summarize_data(df):
#     df['invoice_month'] = df['invoice_date'].dt.to_period('M')
#     monthly_sales = df.groupby('invoice_month')['invoice_amount_usd'].sum()
#     df['invoice_year'] = df['invoice_date'].dt.year
#     yearly_sales = df.groupby('invoice_year')['invoice_amount_usd'].sum()
#     country_sales = df.groupby('country')['invoice_amount_usd'].sum()
#     country_sales_json = country_sales.to_dict()

#     total_disputed = df[df['disputed'] == True].shape[0]
#     avg_days_late = df['days_late'].mean()
#     total_invoices = df.shape[0]

#     summary_text = f"""Invoice Data Summary:

# 🧾 Total Invoices: {total_invoices}
# 💰 Yearly Sales:
# {yearly_sales.to_string()}

# 📆 Monthly Sales:
# {monthly_sales.to_string()}

# 🌍 Country-wise Sales:
# {country_sales.to_string()}

# ⚠️ Disputed Invoices: {total_disputed}
# 🐢 Average Days Late: {avg_days_late:.2f}
# """
#     return summary_text, country_sales_json


# def ask_invoice_question(summary_text, user_query, country_sales_json):
#     prompt = f"""
# You are a smart financial assistant. Use the following invoice data summary and structured country sales data to answer the user question.

# --- Invoice Summary ---
# {summary_text}

# --- Structured Country Sales ---
# {country_sales_json}

# Now answer this user question: "{user_query}"

# Be precise. If the answer is not in the data, respond with "Not available."
# """
#     response = model.generate_content(prompt)
#     return response.text


# def main():
#     st.set_page_config(page_title="Invoice Data Assistant", layout="centered")
#     st.title("Invoice Data Assistant 💼")

#     uploaded_file = st.file_uploader("Upload your invoice CSV file", type=["csv"])
#     if uploaded_file is not None:
#         try:
#             df = pd.read_csv(uploaded_file, parse_dates=['invoice_date', 'due_date', 'settled_date'])
#         except Exception as e:
#             st.error(f"Error loading CSV: {e}")
#             return

#         st.success("CSV loaded successfully!")

#         if st.button("Generate Summary"):
#             summary_text, country_sales_json = summarize_data(df)
#             st.session_state['summary_text'] = summary_text
#             st.session_state['country_sales_json'] = country_sales_json
#             st.session_state['conversation'] = []
#             st.experimental_rerun()

#     if 'summary_text' in st.session_state and 'country_sales_json' in st.session_state:
#         st.subheader("Invoice Summary")
#         st.text_area("", st.session_state['summary_text'], height=300, disabled=True)

#         example_questions = [
#             "What are the total sales in 2021?",
#             "Which country had the highest sales?",
#             "Two countries with the lowest sales?",
#             "How many invoices are disputed?",
#             "What is the average days late to settle?",
#             "Show monthly sales for 2020",
#             "How many invoices were settled late?"
#         ]
#         selected_example = st.selectbox("Or choose a sample question:", [""] + example_questions)

#         if 'user_input' not in st.session_state:
#             st.session_state['user_input'] = ""

#         if selected_example:
#             st.session_state['user_input'] = selected_example

#         user_query = st.text_input("Ask a question about the invoice data:", value=st.session_state['user_input'])

#         if st.button("Get Answer"):
#             if user_query:
#                 if 'conversation' not in st.session_state:
#                     st.session_state['conversation'] = []

#                 with st.spinner("Processing..."):
#                     answer = ask_invoice_question(
#                         st.session_state['summary_text'],
#                         user_query,
#                         st.session_state['country_sales_json']
#                     )

#                 # Insert new question at the TOP
#                 st.session_state['conversation'].insert(0, (user_query, answer))
#                 st.session_state['user_input'] = ""

#                 st.markdown("### Conversation History")
#                 for q, a in st.session_state['conversation']:
#                     st.markdown(f"**You:** {q}")
#                     st.markdown(f"**Assistant:** {a}")
#                     st.markdown("---")
#             else:
#                 st.warning("Please enter a question.")

# if __name__ == "__main__":
#     main()



import streamlit as st
import pandas as pd
import re
import google.generativeai as genai
import matplotlib.pyplot as plt  # For bar chart
from googletrans import Translator  # For translation

# Configure Gemini with your API key
genai.configure(api_key="AIzaSyCrD1cA9Ee2w2x-nAo-TV96j0XoqHbexz4")
model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
translator = Translator()

def summarize_data(df):
    df['invoice_month'] = df['invoice_date'].dt.to_period('M')
    monthly_sales = df.groupby('invoice_month')['invoice_amount_usd'].sum()
    df['invoice_year'] = df['invoice_date'].dt.year
    yearly_sales = df.groupby('invoice_year')['invoice_amount_usd'].sum()
    country_sales = df.groupby('country')['invoice_amount_usd'].sum()
    country_sales_json = country_sales.to_dict()

    total_disputed = df[df['disputed'] == True].shape[0]
    avg_days_late = df['days_late'].mean()
    total_invoices = df.shape[0]

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

def ask_invoice_question(summary_text, user_query, country_sales_json, target_lang="en"):
    prompt = f"""
You are a smart financial assistant. Use the following invoice data summary and structured country sales data to answer the user question.

--- Invoice Summary ---
{summary_text}

--- Structured Country Sales ---
{country_sales_json}

Now answer this user question: "{user_query}"

Be precise. If the answer is not in the data, respond with "Not available."
"""
    response = model.generate_content(prompt)
    answer = response.text

    # Translate answer if language is not English
    if target_lang != "en":
        translated = translator.translate(answer, dest=target_lang)
        return translated.text
    return answer

def plot_country_sales(country_sales_json):
    countries = list(country_sales_json.keys())
    sales = list(country_sales_json.values())

    fig, ax = plt.subplots()
    ax.bar(countries, sales)
    ax.set_xlabel("Country")
    ax.set_ylabel("Sales (USD)")
    ax.set_title("Country Sales")
    plt.xticks(rotation=45)
    st.pyplot(fig)

def main():
    st.set_page_config(page_title="Invoice Data Assistant", layout="centered")
    st.title("Invoice Data Assistant 💼")

    # Language selection
    lang_map = {
        "English": "en",
        "French": "fr",
        "Spanish": "es",
        "German": "de",
        "Chinese (Simplified)": "zh-cn",
        "Arabic": "ar"
    }
    selected_lang = st.selectbox("Select response language:", list(lang_map.keys()))

    uploaded_file = st.file_uploader("Upload your invoice CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, parse_dates=['invoice_date', 'due_date', 'settled_date'])
        except Exception as e:
            st.error(f"Error loading CSV: {e}")
            return

        st.success("CSV loaded successfully!")

        if st.button("Generate Summary"):
            summary_text, country_sales_json = summarize_data(df)
            st.session_state['summary_text'] = summary_text
            st.session_state['country_sales_json'] = country_sales_json
            st.session_state['conversation'] = []
            st.experimental_rerun()

    if 'summary_text' in st.session_state and 'country_sales_json' in st.session_state:
        st.subheader("Invoice Summary")
        st.text_area("", st.session_state['summary_text'], height=300, disabled=True)

        # Show bar chart
        st.subheader("Country Sales Chart")
        plot_country_sales(st.session_state['country_sales_json'])

        example_questions = [
            "What are the total sales in 2021?",
            "Which country had the highest sales?",
            "Two countries with the lowest sales?",
            "How many invoices are disputed?",
            "What is the average days late to settle?",
            "Show monthly sales for 2020",
            "How many invoices were settled late?"
        ]
        selected_example = st.selectbox("Or choose a sample question:", [""] + example_questions)

        if 'user_input' not in st.session_state:
            st.session_state['user_input'] = ""

        if selected_example:
            st.session_state['user_input'] = selected_example

        user_query = st.text_input("Ask a question about the invoice data:", value=st.session_state['user_input'])

        if st.button("Get Answer"):
            if user_query:
                if 'conversation' not in st.session_state:
                    st.session_state['conversation'] = []

                with st.spinner("Processing..."):
                    answer = ask_invoice_question(
                        st.session_state['summary_text'],
                        user_query,
                        st.session_state['country_sales_json'],
                        lang_map[selected_lang]
                    )

                st.session_state['conversation'].append((user_query, answer))
                st.session_state['user_input'] = ""

                st.markdown("### Conversation History")
                for q, a in st.session_state['conversation']:
                    st.markdown(f"**You:** {q}")
                    st.markdown(f"**Assistant:** {a}")
                    st.markdown("---")
            else:
                st.warning("Please enter a question.")

if __name__ == "__main__":
    main()
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

hf_token = os.getenv("HF_API_TOKEN")

# Basic keyword-based category mapping
CATEGORY_KEYWORDS = {
    "groceries": ["walmart", "aldi", "grocery", "supermarket"],
    "utilities": ["electric", "water", "utility", "gas", "internet"],
    "rent": ["rent", "landlord"],
    "entertainment": ["netflix", "spotify", "movie", "theater", "cinema"],
    "transport": ["uber", "lyft", "taxi", "bus", "train", "gasoline", "fuel"],
    "dining": ["restaurant", "mcdonald", "starbucks", "coffee", "burger"],
    "shopping": ["amazon", "shop", "mall", "clothing"],
    "income": ["salary", "paycheck", "deposit", "refund"]
}

def categorize_transaction(description):
    desc = str(description).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in desc for keyword in keywords):
            return category
    return "other"

# Function to load and validate data
def load_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)

        # Check for required columns
        required_cols = {'Date', 'Description', 'Amount'}
        if not required_cols.issubset(df.columns):
            st.error(f"CSV must contain the columns: {', '.join(required_cols)}")
            return None

        # Clean and convert data
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
        df = df.dropna(subset=['Amount'])
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.date
        df = df.dropna(subset=['Date'])

        # Categorize
        df['Category'] = df['Description'].apply(categorize_transaction)

        return df
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

def main():
    st.title('💰 AI-Powered Personal Finance Advisor')

    uploaded_file = st.file_uploader("Upload your transaction history (CSV format)", type=["csv"])

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write(df.head())
        if df is not None:
            st.subheader("📄 Uploaded Transaction Data")
            st.dataframe(df)

            st.subheader("📊 Summary Statistics")
            st.write(f"Total Number of Transactions: {len(df)}")
            total_spent = abs(df[df['Amount'] < 0]['Amount'].sum())  # Only sum expenses
            st.write(f"Total Money Spent: ${total_spent:.2f}")

            # Spending Over Time
            st.subheader("📈 Spending Over Time")
            df_expenses = df[df['Amount'] < 0]
            df_by_date = df_expenses.groupby('Date')['Amount'].sum().sort_index()
            fig, ax = plt.subplots(figsize=(10, 5))
            df_by_date.plot(ax=ax, kind='line', marker='o', color='red')
            ax.set_ylabel("Amount Spent ($)")
            ax.set_title("Spending Over Time")
            st.pyplot(fig)

            # Spending by Category
            st.subheader("📂 Spending by Category")
            df_expenses = df[df['Amount'] < 0]
            df_expenses = df_expenses.dropna(subset=['Category'])
            df_expenses = df_expenses[df_expenses['Category'].notna()]
            df_by_category = df_expenses.groupby('Category')['Amount'].sum().sort_values(ascending=True)
            st.write(f"Data for Categories (top spending): {df_by_category.head()}")
            st.bar_chart(df_by_category)

            if not df_by_category.empty:
            	top_category = df_by_category.idxmin()
            	top_amount = abs(df_by_category.min())
            	st.write(f"Top Spending Category: *{top_category}* (${top_amount:.2f})")
            else:
            	st.write("No valid spending categories found.")

            # Future insights placeholder
            st.subheader("🤖 AI-Driven Insights (Coming Soon!)")

if __name__ == "__main__":
    main()
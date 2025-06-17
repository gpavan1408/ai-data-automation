import streamlit as st
import pandas as pd
import os
import time
import plotly.express as px # Import the new library

# --- Page Configuration ---
st.set_page_config(
    page_title="Fraud Detection Analysis",
    page_icon="💳",
    layout="wide"
)

# --- Data Loading ---
@st.cache_data
def load_data():
    """Loads the credit card fraud dataset."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    file_path = os.path.join(project_root, "data", "raw", "creditcard.csv")
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at {file_path}")
        st.write("Please ensure the `creditcard.csv` file is in the `data/raw` directory.")
        return None

# Load the data and show a progress bar
with st.spinner('Loading data...'):
    df = load_data()
    time.sleep(1)

# --- Main Dashboard ---
st.title("💳 Credit Card Fraud Analysis")
st.markdown("An interactive dashboard to explore the credit card fraud dataset.")

if df is not None:
    # --- Create a Tabbed Interface ---
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "📈 Time Analysis", "📄 Data Explorer"])

    # --- Tab 1: Overview ---
    with tab1:
        st.header("Overall Transaction Distribution")

        class_counts = df['Class'].value_counts()
        
        col1, col2 = st.columns(2)
        
        normal_transactions = class_counts.get(0, 0)
        col1.metric(label="Normal Transactions (Class 0)", value=f"{normal_transactions:,}")

        fraud_transactions = class_counts.get(1, 0)
        col2.metric(label="Fraudulent Transactions (Class 1)", value=f"{fraud_transactions:,}", delta=f"{(fraud_transactions / df.shape[0]) * 100:.2f}% of Total", delta_color="inverse")

        # --- THIS IS THE CORRECTED CODE BLOCK ---
        st.subheader("Transaction Proportions")
        # Create a DataFrame suitable for the pie chart
        pie_chart_data = class_counts.reset_index()
        pie_chart_data.columns = ['Class', 'Count']
        pie_chart_data['Class'] = pie_chart_data['Class'].map({0: 'Normal', 1: 'Fraud'})

        # Create the pie chart figure using Plotly Express
        fig = px.pie(
            pie_chart_data, 
            names='Class', 
            values='Count', 
            title='Proportion of Normal vs. Fraud Transactions',
            color_discrete_map={'Normal':'blue', 'Fraud':'red'}
        )
        
        # Display the Plotly figure in Streamlit
        st.plotly_chart(fig, use_container_width=True)
        # --- END OF CORRECTION ---

        st.write("""
        This pie chart clearly illustrates the severe class imbalance in the dataset. Fraudulent transactions represent a very small fraction of the total.
        """)

    # --- Tab 2: Time Analysis ---
    with tab2:
        st.header("Analysis of Transactions Over Time")
        
        df['Hour'] = (df['Time'] / 3600) % 24
        
        st.subheader("Transaction Volume by Hour")
        hist_values = pd.to_datetime(df['Hour'], unit='h').dt.hour.value_counts().sort_index()
        st.bar_chart(hist_values)
        st.write("This chart shows the distribution of all transactions over a 24-hour cycle.")

    # --- Tab 3: Data Explorer ---
    with tab3:
        st.header("Data Explorer")
        st.write("View the raw data and its statistical summary.")
        
        st.dataframe(df, key="full_data_explorer")

        st.markdown("---")
        
        st.subheader("Statistical Summary")
        st.write("Descriptive statistics for each feature in the dataset:")
        st.dataframe(df.describe(), key="summary_statistics")
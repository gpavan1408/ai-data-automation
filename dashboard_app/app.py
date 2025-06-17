import streamlit as st
import pandas as pd
import os

# --- Page Configuration ---
# This must be the first Streamlit command in your script.
st.set_page_config(
    page_title="AI Dashboard Automation Project",
    page_icon="🤖",
    layout="wide" # Use "wide" layout for a more professional look
)

# --- Data Loading ---
# We use st.cache_data to cache the data, so it doesn't have to be reloaded
# every time the user interacts with the app. This improves performance.
@st.cache_data
def load_data():
    """Loads the processed user data from the CSV file."""
    project_root = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(project_root, "data", "processed", "processed_users.csv")
    try:
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        # If the file is not found, show an error and stop the app.
        st.error(f"Data file not found at {file_path}")
        st.stop()

df = load_data()

# --- Main Dashboard Title ---
st.title("🤖 AI Dashboard Automation Project")

# --- Sidebar for Filters ---
st.sidebar.header("Filter Options")
# Allow filtering by company. We get a unique list of companies from the DataFrame.
companies = sorted(df['company_name'].unique())
selected_companies = st.sidebar.multiselect(
    "Select Companies:",
    options=companies,
    default=companies # By default, all companies are selected
)

# Filter the DataFrame based on the selection in the sidebar.
if selected_companies:
    df_filtered = df[df['company_name'].isin(selected_companies)]
else:
    # If no company is selected, show the full dataframe.
    df_filtered = df

# --- Key Metrics (KPIs) ---
st.header("Top-Level Metrics")
# Use st.columns to create a clean, multi-column layout for the KPIs.
col1, col2, col3 = st.columns(3)

# Metric 1: Total Users
total_users = df_filtered.shape[0]
col1.metric(label="Total Users", value=total_users)

# Metric 2: Number of Companies
num_companies = df_filtered['company_name'].nunique()
col2.metric(label="Number of Companies", value=num_companies)

# Metric 3: Average User ID (example metric)
average_id = int(df_filtered['id'].mean())
col3.metric(label="Average User ID", value=average_id)

st.markdown("---") # Adds a horizontal line

# --- Charts and Data Tables ---
st.header("Data Visualizations")

# Chart 1: Bar chart of users per company
st.subheader("Users per Company")
# Group data by company and count the number of users
company_user_counts = df_filtered['company_name'].value_counts()
st.bar_chart(company_user_counts)

# Data Table: Display the filtered data
st.subheader("User Data Table")
# Display the DataFrame as an interactive table.
st.dataframe(df_filtered)
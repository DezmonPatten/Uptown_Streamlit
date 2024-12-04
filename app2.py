import pandas as pd
import streamlit as st
import plotly.express as px

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"  # Default to home page


st.set_page_config(page_title="Store Sales Dashboard", layout="wide")

# File uploader
st.sidebar.title("Upload Sales Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload an Excel file (with required columns)", 
    type=["xlsx", "xls"]
)
sample_filepath_pc = '/Users/dezmon/Library/Mobile Documents/com~apple~CloudDocs/Visual Analytics/Final Project (Streamlit)/Items_Sold_Export_CLT.xlsx'

# Default dataset
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.sidebar.success("File uploaded successfully!")
else:
    st.sidebar.info("Using sample dataset. Upload a file to analyze your own data.")
    df = pd.read_excel(sample_filepath_pc)  # Replace with a local file path

# Ensure required columns exist
required_columns = ['Sold Date', 'Invoice No', 'Sold Cost Total', 
                    'Sold Price Total', 'Sub Category', 'Days on Hand', 
                    'Transaction Type', 'Employee Role', 'Employee']
if not set(required_columns).issubset(df.columns):
    st.error("The uploaded file must contain all the required columns.")
    st.stop()

# Preprocess data
df['Sold Date'] = pd.to_datetime(df['Sold Date'])  # Ensure datetime format
df['profit'] = df['Sold Price Total'] - df['Sold Cost Total']
df['Employee_First'] = df['Employee'].apply(lambda x: x.split()[0].capitalize())

# Navigation setup
st.sidebar.subheader("Navigation")
st.sidebar.button("Home", on_click=lambda: st.session_state.update({"current_page": "home"}))
st.sidebar.button("Overview", on_click=lambda: st.session_state.update({"current_page": "overview"}))
st.sidebar.button("Performance", on_click=lambda: st.session_state.update({"current_page": "performance"}))
st.sidebar.button("Sales", on_click=lambda: st.session_state.update({"current_page": "items"}))

def switch_page(page: str): 
    st.session_state.current_page = page

def home(): 
    st.title("Uptown Cheapskates Monthly Performance")
    st.markdown("""
    Welcome to **Uptown Cheapskate's Performance Dashboard**! 
    Explore detailed insights about the store's performance, employee contributions, and category analysis.
    Use the sidebar to navigate through the pages.
    """)
    # Company Logo
    st.image("UC_Logo.png", 
            caption="Monthly performance insights at your fingertips",
             use_column_width=True)

    # Add visually appealing sections
    st.subheader("What You Can Explore")
    st.markdown("""
    - 📊 **Overview**: Get a bird's-eye view of daily sales trends and peak days.
    - 🛒 **Performance**: Analyze high-traffic times and employee contributions.
    - 📈 **Category Insights**: Dive into the top-performing and least-performing product categories.
    """)

    st.markdown("""
    ---
    **💡 Pro Tip:** A sample dataset from **September 2024** has been preloaded for your convenience.  
    Want to analyze data for a different time frame? Simply upload a new sales export file to explore fresh insights.  

    **🔍 Ready to get started?**  
    Use the **sidebar** to select a page and dive into the data!
    """)

def overview(df): 
    total_profit = df['profit'].sum()
    total_items_sold = len(df)
    average_sale_price = df['Sold Price Total'].mean()

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Profit", value=f"${total_profit:,.2f}")
    col2.metric(label="Total Items Sold", value=f"{total_items_sold:,}")
    col3.metric(label="Average Sale Price", value=f"${average_sale_price:,.2f}")

    df['Date'] = df['Sold Date'].dt.date
    daily_sales = df.groupby('Date')['profit'].sum().reset_index()

    fig = px.line(daily_sales, x='Date', y='profit', title='Total Daily Profit Over Time')
    st.plotly_chart(fig)

def performance(df): 
    st.title("Store Performance")
    st.write("Analyze high-traffic times and employee contributions.")

    # Heatmap: Sales by Hour and Weekday
    df['Hour'] = df['Sold Date'].dt.hour
    df['Weekday'] = df['Sold Date'].dt.day_name()

    heatmap_data = df.groupby(['Weekday', 'Hour']).size().reset_index(name='Count')
    heatmap_pivot = heatmap_data.pivot(index='Weekday', columns='Hour', values='Count').fillna(0)

    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(ordered_days).fillna(0)

    heatmap_fig = px.imshow(
        heatmap_pivot,
        labels={'x': 'Hour of Day', 'y': 'Weekday', 'color': 'Count'},
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        title="Sales Count by Hour and Weekday",
        color_continuous_scale='Greens'
    )
    st.plotly_chart(heatmap_fig)

    # Employee Performance: Bar Chart
    employee_invoices = df.groupby('Employee_First')['Invoice No'].nunique().reset_index()
    employee_invoices.columns = ['Employee', 'Distinct Invoices']
    employee_invoices = employee_invoices.sort_values(by='Distinct Invoices', ascending=False)

    bar_fig = px.bar(
        employee_invoices,
        x='Employee',
        y='Distinct Invoices',
        title='Total Number of Distinct Invoices per Employee',
        labels={'Distinct Invoices': 'Number of Invoices', 'Employee': 'Employee Name'},
        text='Distinct Invoices'
    )
    bar_fig.update_traces(textposition='outside')
    st.plotly_chart(bar_fig)


def items(df):
    st.title("Category Analysis")
    st.write("Insights into the top and lowest-performing categories:")

    # Top 10 Selling Categories by Profit
    top_categories = df.groupby('Sub Category')['profit'].sum().round().sort_values(ascending=False).head(10).reset_index()
    top_categories_fig = px.bar(
        top_categories, x = 'Sub Category', y = 'profit',
        title='Top 10 Selling Categories by Profit',
        labels={'profit': 'Profit ($)', 'Sub Category': 'Category'},
        text='profit',
        orientation='v'
    )
    top_categories_fig.update_traces(textposition='outside')
    st.plotly_chart(top_categories_fig)

    # Bottom 10 Categories by Average Days on Hand
    bottom_categories = df.groupby('Sub Category')['Days on Hand'].mean().round().sort_values(ascending=False).head(10).reset_index()
    bottom_categories_fig = px.bar(
        bottom_categories,
        x='Sub Category',
        y='Days on Hand',
        title='Top 10 Lowest-Selling Categories by Days on Hand',
        labels={'Days on Hand': 'Average Days on Hand', 'Sub Category': 'Category'},
        text='Days on Hand',
        orientation='v'
    )
    bottom_categories_fig.update_traces(textposition='outside')
    st.plotly_chart(bottom_categories_fig)

       
# Main window
fn_map = {
    'home': home,
    'overview': lambda: overview(df),
    'performance': lambda: performance(df),
    'items': lambda: items(df)
}

# Render the selected page
main_workflow = fn_map.get(st.session_state.current_page, home)
main_workflow()
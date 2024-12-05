import altair as alt
import pandas as pd
import streamlit as st
import plotly.express as px
from matplotlib.dates import DateFormatter

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"  # Default to home page

st.set_page_config(page_title="Monthly Performance Tracker", layout="wide")
#st.title("Uptown Cheapskates Monthly Performance")

filepath_pc = 'Items_Sold_Export_Uptown_Cheapskate_Charlotte_20241007.xlsx'
df = pd.read_excel(filepath_pc, 
                   usecols=['Sold Date','Invoice No', 'Sold Cost Total','Sold Price Total','Sub Category','Days on Hand',
                            'Transaction Type','Employee Role','Employee_First', 'Sold Quantity'])
  
# Navigation
st.sidebar.subheader("Navigation")
home_button = st.sidebar.button("Home", on_click= lambda: st.session_state.update({"current_page": "home"}))
overview_button = st.sidebar.button("Overview", on_click=lambda: st.session_state.update({"current_page": "overview"}))
performance_button = st.sidebar.button("Performance", on_click=lambda: st.session_state.update({"current_page": "performance"}))
sales_button = st.sidebar.button("Sales", on_click=lambda: st.session_state.update({"current_page": "sales"}))

def switch_page(page: str): 
    st.session_state.current_page = page

def home(): 
    st.title("Uptown Cheapskates Monthly Performance")
    st.markdown("""
    Welcome to the **Uptown Cheapskates Monthly Performance Dashboard**! 
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

    # Add a call to action
    st.markdown("""
    ---
    Ready to get started? Select a page from the sidebar to begin your journey!
    """)

def overview(): 
    df1 = df.copy()
    df1['profit'] = df['Sold Price Total'] - df1['Sold Cost Total'] 
    total_profit = df1['profit'].sum()
    total_items_sold = df1['Sold Quantity'].sum() 
    average_sale_price = df1['Sold Price Total'].mean()

    # Display key metrics in columns
    st.title("Overview Page")
    st.write("Explore the key metrics and daily sales trends for the selected period.")

    col1, col2, col3 = st.columns(3)
    col1.metric(label="Total Profit", value=f"${total_profit:,.2f}")
    col2.metric(label="Total Items Sold", value=f"{total_items_sold:,}")
    col3.metric(label="Average Sale Price", value=f"${average_sale_price:,.2f}")


    df1['Date'] = df1['Sold Date'].dt.date
    daily_sales = df1.groupby('Date')['profit'].sum().reset_index()
    
    # Create a line plot
    fig = px.line(daily_sales, x='Date', y='profit', title='Total Daily Sales Over November 2024')

    # Highlight peak sales
    fig.add_annotation(
        x='2024-09-14', y=7000,  # Peak sales date and value
        text="Peak Sales", 
        showarrow=True, 
        arrowhead=2, 
        ax=0, 
        ay=-40
    )
    fig.add_annotation(
        x='2024-09-28', y=7000,  # Peak sales date and value
        text="Peak Sales", 
        showarrow=True, 
        arrowhead=2, 
        ax=0, 
        ay=-40
    )

    fig.update_layout(xaxis_title="Sold Date", yaxis_title="Total Sales ($)")
    st.plotly_chart(fig)

def performance(): 
    df2 = df.copy()
    # Add content for performance page
    st.title("Store Performance")
    st.write("This heatmap displays the store's high traffic times, helping you identify the busiest periods throughout the week.  Use this to **optimize staffing and **manage inventory** effectively.")   
    # Calculate profit and weekday for heatmap
    df2['profit'] = df2['Sold Price Total'] - df2['Sold Cost Total']
    df2['Date'] = df2['Sold Date'].dt.date  # Ensure 'Date' column exists   
    # Extract hour and weekday for heatmap
    df2['Hour'] = df2['Sold Date'].dt.hour
    df2['Weekday'] = df2['Sold Date'].dt.day_name()  # e.g., "Monday", "Tuesday"
    # Format hour to show 12-hour format with am/pm
    def format_hour(hour):
        if hour == 0:
            return "12am"
        elif hour == 12:
            return "12pm"
        elif hour > 12:
            return f"{hour - 12}pm"
        else:
            return f"{hour}am"
        
    df2['Formatted Hour'] = df2['Hour'].apply(format_hour)
    # Pivot table for heatmap data
    heatmap_data = df2.groupby(['Weekday', 'Formatted Hour']).size().reset_index(name='Count')

    # Matrix format for heatmap
    heatmap_pivot = heatmap_data.pivot(index='Weekday', columns='Formatted Hour', values='Count').fillna(0)

    # Reorder days of the week
    ordered_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_pivot.reindex(ordered_days)

    # Heatmap for sales by hour and weekday
    heatmap_fig = px.imshow(
        heatmap_pivot,
        labels={'x': 'Hour of Day', 'y': 'Weekday', 'color': 'Count'},
        x=heatmap_pivot.columns,
        y=heatmap_pivot.index,
        title="Sales Count by Hour and Weekday",
        color_continuous_scale='Greens'
    )
    st.plotly_chart(heatmap_fig)
    st.write("Below, the employee performance chart highlights **top preformers** based on the number of transactions processed.You can also view the average **inovice amount**, providing further insight into their preformance.")


    # Calculate distinct invoices per employee
    employee_invoices = df2.groupby('Employee_First')['Invoice No'].nunique().reset_index()
    employee_invoices.columns = ['Employee', 'Distinct Invoices']
    # Sort by distinct invoices in descending order
    employee_invoices = employee_invoices.sort_values(by='Distinct Invoices', ascending=False)

    # Create a bar chart
    bar_fig = px.bar(
        employee_invoices,
        x='Employee',
        y='Distinct Invoices',
        title='Total Number of Distinct Invoices per Employee',
        labels={'Distinct Invoices': 'Number of Invoices', 'Employee': 'Employee Name'},
        text='Distinct Invoices'
    )

    # Add bar chart customizations
    bar_fig.update_traces(textposition='outside')
    bar_fig.update_layout(xaxis_title='Employee', yaxis_title='Number of Distinct Invoices')
    st.plotly_chart(bar_fig)

def sales(): 
    #st.title("Store Performance")
    df3 = df.copy()
    # Calculate Profit 
    df3['profit'] = df3['Sold Price Total'] - df3['Sold Cost Total']

    # Top 10 selling categories by profit
    top_categoreies = (
        df3.groupby('Sub Category')['profit'].sum().sort_values(ascending = False).head(10).reset_index()
    )
    top_categories_fig = px.bar(
        top_categoreies, x = 'Sub Category', y = 'profit', 
        title = 'Top 10 Selling Categories', 
        labels={'profit': 'Profit ($)', 'Sub Category': 'Category'},
        text='profit',
    )
    top_categories_fig.update_traces(textposition='outside')
    top_categories_fig.update_layout(
        yaxis_title='Category',
        xaxis_title='Profit ($)',
        yaxis=dict(categoryorder='total ascending')
    )
    #st.subheader("Top 10 Selling Categories by Profit")
    st.plotly_chart(top_categories_fig)

    # Bottom 10 categories by average days on hand
    bottom_categories = (
        df3.groupby('Sub Category')['Days on Hand']
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    bottom_categories_fig = px.bar(
        bottom_categories,
        x='Sub Category',
        y='Days on Hand',
        title='Top 10 Lowest-Selling Categories by Days on Hand',
        labels={'Days on Hand': 'Average Days on Hand', 'Sub Category': 'Category'},
        text='Days on Hand',
    )
    bottom_categories_fig.update_traces(textposition='outside')
    bottom_categories_fig.update_layout(
        yaxis_title='Category',
        xaxis_title='Average Days on Hand',
        yaxis=dict(categoryorder='total ascending')
    )
    st.plotly_chart(bottom_categories_fig)

# Main window
fn_map = {
    'home': home,
    'overview': overview,
    'performance': performance,
    'sales': sales
}

# Call the function based on current page
main_workflow = fn_map.get(st.session_state.current_page, home)
main_workflow()
import altair as alt
import pandas as pd
import streamlit as st
import plotly.express as px

# Initialize session state
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"  # Default to home page

st.set_page_config(layout = "wide")
#st.title("Uptown Cheapskates Monthly Performance")

df = pd.read_excel('/Users/dmoney/Library/Mobile Documents/com~apple~CloudDocs/Visual Analytics/Final Project (Streamlit)/Items_Sold_Export_Uptown_Cheapskate_Charlotte_20241007.xlsx', 
                   usecols=['Sold Date','Invoice No', 'Sold Cost Total','Sold Price Total','Sub Category','Days on Hand',
                            'Transaction Type','Employee Role','Employee_First'])
  
# Navigation
st.sidebar.subheader("Navigation")
home_button = st.sidebar.button("Home", on_click= lambda: st.session_state.update({"current_page": "home"}))
overview_button = st.sidebar.button("Overview", lambda: st.session_state.update({"current_page": "overview"}))
performance_button = st.sidebar.button("Performance", on_click=lambda: st.session_state.update({"current_page": "performance"}))

def switch_page(page: str): 
    st.session_state.current_page = page

def home(): 
    st.title("Uptown Cheapskates Monthly Performance")
    st.write("Welcome to the performance tracker! Please select a page from the sidebar.")

def overview(): 
    df = pd.read_excel('/Users/dmoney/Library/Mobile Documents/com~apple~CloudDocs/Visual Analytics/Final Project (Streamlit)/Items_Sold_Export_Uptown_Cheapskate_Charlotte_20241007.xlsx', 
                   usecols=['Sold Date','Invoice No', 'Sold Cost Total','Sold Price Total','Sub Category','Days on Hand',
                            'Transaction Type','Employee Role','Employee_First'])
    df['profit'] = df['Sold Price Total'] - df['Sold Cost Total'] 
    df['Date'] = df['Sold Date'].dt.date
    daily_sales = df.groupby('Date')['profit'].sum().reset_index()
    
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
    # Add content for performance page
    st.title("Performance")
    st.write("Performance content goes here.")   


# Main window
fn_map = {
    'home': home,
    'overview': overview,
    'performance': performance
}

# Call the function based on current page
main_workflow = fn_map.get(st.session_state.current_page, home)
main_workflow()
import streamlit as st
import pandas as pd

def render_chart(df, chart_type):
    if chart_type == "bar":
        st.bar_chart(df)
    elif chart_type == "line":
        st.line_chart(df)
    elif chart_type == "area":
        st.area_chart(df)
    elif chart_type == "scatter":
        st.scatter_chart(df)
    else:
        st.bar_chart(df)



def render_single_chart(chart_data, chart_type):
    """
    Render a single chart from dictionary data
    
    Args:
        chart_data: Dictionary containing chart data
        chart_type: Type of chart (bar, line, area, scatter)
    """
    df = pd.DataFrame(chart_data)
    
    # Automatically detect and set index from first column if it contains non-numeric data
    if len(df.columns) > 1:
        first_col = df.columns[0]
        # Check if first column contains non-numeric data (suitable for x-axis labels)
        if df[first_col].dtype == 'object' or df[first_col].dtype == 'string':
            df = df.set_index(first_col)
    
    render_chart(df, chart_type)


#render charts dynamically based on chart type
def render_dynamic_chart(chart_data, chart_type):
    """
    Render chart(s) dynamically based on the chart type
    
    Args:
        chart_data: Dictionary or list of dictionaries containing chart data
        chart_type: Type of chart (bar, line, area, scatter)
    """
    # Handle multiple charts (list of chart data)
    if isinstance(chart_data, list):
        for single_chart in chart_data:
            render_single_chart(single_chart, chart_type)
    else:
        render_single_chart(chart_data, chart_type)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(layout="wide")

# Load synthetic data
partners_df = pd.read_csv('partners_data.csv')
disease_df = pd.read_csv('disease_data.csv')

# App Layout with Filtering Capabilities
st.sidebar.title('Filters')

# Country Filter
countries = partners_df['Country'].unique()
selected_countries = st.sidebar.multiselect('Select Countries', options=countries, default=countries)

# Disease Filter
diseases = disease_df['Disease'].unique()
selected_diseases = st.sidebar.multiselect('Select Diseases', options=diseases, default=diseases)

# Year Filter
min_year = int(disease_df['Year'].min())
max_year = int(disease_df['Year'].max())
selected_years = st.sidebar.slider('Select Year Range', min_value=min_year, max_value=max_year, value=(min_year, max_year))

# Filter partners data
filtered_partners = partners_df[partners_df['Country'].isin(selected_countries)]

# Filter disease data
filtered_disease = disease_df[
    (disease_df['Country'].isin(selected_countries)) &
    (disease_df['Disease'].isin(selected_diseases)) &
    (disease_df['Year'] >= selected_years[0]) &
    (disease_df['Year'] <= selected_years[1])
]

def main():
    #Visualizations
    st.title('NTD Partners and Disease Occurrence Dashboard')
    
    # Create columns for layout
    col1, col2 = st.columns((2, 1))
    
    with col1:
        st.subheader('Healthcare Partners Map')
    
        # Map of partners
        fig_partners_map = px.scatter_mapbox(
            filtered_partners,
            lat='Latitude',
            lon='Longitude',
            hover_name='Name',
            hover_data=['Specialization', 'Country', 'City'],
            color='Specialization',
            zoom=3,
            height=600
        )
        fig_partners_map.update_layout(mapbox_style='open-street-map')
        fig_partners_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_partners_map, use_container_width=True)
    
    with col2:
        st.subheader('Disease Occurrence Map')
    
        # Aggregate disease cases by location
        disease_locations = filtered_disease.groupby(['Latitude', 'Longitude', 'Disease']).agg({'Cases': 'sum'}).reset_index()
    
        # Map of disease occurrences
        fig_disease_map = px.density_mapbox(
            disease_locations,
            lat='Latitude',
            lon='Longitude',
            z='Cases',
            radius=10,
            center=dict(lat=20, lon=80),
            zoom=3,
            mapbox_style='open-street-map',
            height=600
        )
        st.plotly_chart(fig_disease_map, use_container_width=True)
    # Partners per Country
    st.subheader('Number of Partners per Country')
    
    partners_per_country = filtered_partners.groupby('Country').size().reset_index(name='Number of Partners')
    
    fig_bar = px.bar(
        partners_per_country,
        x='Country',
        y='Number of Partners',
        color='Country',
        text='Number of Partners'
    )
    fig_bar.update_layout(xaxis_title='Country', yaxis_title='Number of Partners', showlegend=False)
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # PieChart
    st.subheader('Partner Specializations Distribution')
    
    specialization_counts = filtered_partners['Specialization'].value_counts().reset_index()
    specialization_counts.columns = ['Specialization', 'Count']
    
    fig_pie = px.pie(
        specialization_counts,
        names='Specialization',
        values='Count',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    #Line Charts
    st.subheader('NTD Cases Over Time')
    
    cases_over_time = filtered_disease.groupby(['Year', 'Disease']).agg({'Cases': 'sum'}).reset_index()
    
    fig_line = px.line(
        cases_over_time,
        x='Year',
        y='Cases',
        color='Disease',
        markers=True
    )
    fig_line.update_layout(xaxis_title='Year', yaxis_title='Number of Cases')
    
    st.plotly_chart(fig_line, use_container_width=True)
    
    #stacked Bar
    st.subheader('Partner Involvement by Specialization')
    
    partners_by_specialization = filtered_partners.groupby(['Country', 'Specialization']).size().reset_index(name='Count')
    
    fig_stacked_bar = px.bar(
        partners_by_specialization,
        x='Country',
        y='Count',
        color='Specialization',
        text='Count'
    )
    fig_stacked_bar.update_layout(xaxis_title='Country', yaxis_title='Number of Partners')
    
    st.plotly_chart(fig_stacked_bar, use_container_width=True)
    
    # tables
    st.subheader('Partner Details')
    
    st.dataframe(filtered_partners[['Partner ID', 'Name', 'Country', 'City', 'Specialization']])


if __name__ == '__main__':
    main()

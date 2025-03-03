import streamlit as st
import plotly.graph_objects as go
import re
import pandas as pd

# Define locations of cellular components (x, y positions)
locations = {
    # Cell structures
    "Axon": (2, 1),
    "Dendrite": (1, 2),
    "Dendritic spine": (1.5, 2.2),
    "Cytoskeleton": (0, 0),
    "Cytoplasm": (0, 0.3),
    "Perinuclear region": (0, 1),
    "Cell projection": (1.5, -0.8),
    "Postsynaptic density": (2.3, 1.5),
    
    # Organelles
    "Endoplasmic reticulum": (-1, 0.5),
    "ER": (-1, 0.5),
    "Golgi apparatus": (-1.5, 0.8),
    "Golgi": (-1.5, 0.8),
    "Trans-Golgi": (-1.8, 0.9),
    "Mitochondrion": (-2, 0.3),
    "Nucleus": (0, 1.5),
    
    # Vesicles and endosomes
    "Endosome": (-1.2, -0.5),
    "Early endosome": (-1.0, -0.7),
    "Recycling endosome": (-1.4, -0.3),
    "Cytoplasmic vesicle": (-0.8, -0.7),
    
    # Membranes
    "Plasma membrane": (0.5, -1),
    "Cell membrane": (0.5, -1),
    "Membrane": (0.5, -1)
}

def parse_subcellular_location(location_text):
    """
    Parse subcellular location text from UniProt and return matching locations
    """
    if not location_text or pd.isna(location_text):
        return []
    
    # Split into separate location entries (separated by periods)
    entries = location_text.split('.')
    
    found_locations = []
    
    for entry in entries:
        if not entry.strip():
            continue
            
        # Remove evidence codes in curly braces
        clean_entry = re.sub(r'\{[^}]*\}', '', entry).strip()
        
        # Remove details after semicolons (like "Multi-pass membrane protein")
        if ';' in clean_entry:
            clean_entry = clean_entry.split(';')[0].strip()
        
        # Check for matches in our location dictionary
        for loc in locations.keys():
            pattern = r'\b' + re.escape(loc.lower()) + r'\b'
            if re.search(pattern, clean_entry.lower()):
                found_locations.append(loc)
                
        # Handle compound locations like "Cell projection, axon"
        parts = re.split(r',\s*', clean_entry)
        for part in parts:
            part = part.strip()
            for loc in locations.keys():
                if part.lower() == loc.lower():  # Exact match for parts
                    if loc not in found_locations:
                        found_locations.append(loc)
    
    return found_locations

def create_cell_visualization(location_matches):
    """
    Create a plotly figure for cellular component visualization
    highlighting the matched locations
    """
    # Create a figure
    fig = go.Figure()
    
    # Create a schematic cell outline
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=-3, y0=-2, x1=3, y1=2.5,
        line=dict(color="black", width=2),
        fillcolor="rgba(255, 255, 255, 0)"
    )
    
    # Add nuclear outline
    fig.add_shape(
        type="circle",
        xref="x", yref="y",
        x0=-1, y0=0.5, x1=1, y1=2.5,
        line=dict(color="black", width=1.5),
        fillcolor="rgba(230, 230, 255, 0.3)"
    )
    
    # Draw all cellular components
    for loc, (x, y) in locations.items():
        if loc in location_matches:
            # Highlight matched locations
            fig.add_trace(go.Scatter(
                x=[x], y=[y], 
                text=[loc], 
                mode="markers+text",
                marker=dict(size=15, color="red"),
                textfont=dict(color="black", size=12, family="Arial")
            ))
        else:
            # Gray out other locations
            fig.add_trace(go.Scatter(
                x=[x], y=[y], 
                text=[loc], 
                mode="markers+text",
                marker=dict(size=10, color="lightgray", opacity=0.6),
                textfont=dict(color="gray", size=10)
            ))
    
    # Set layout
    fig.update_layout(
        title="Subcellular Location Visualization",
        xaxis=dict(visible=False, range=[-3.5, 3.5]), 
        yaxis=dict(visible=False, range=[-2.5, 3]),
        width=700,
        height=500,
        showlegend=False,
        plot_bgcolor="white",
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    # Add a legend for the cell compartments
    fig.add_annotation(
        x=3, y=2.5,
        text="Nucleus",
        showarrow=False,
        font=dict(size=10)
    )
    
    return fig

def display_subcellular_location(location_text):
    """
    Parse the location text and display the visualization
    """
    matches = parse_subcellular_location(location_text)
    fig = create_cell_visualization(matches)
    st.plotly_chart(fig)
    
    if not matches:
        st.info("No specific subcellular locations recognized in the data.")
    else:
        # Display found locations in a more readable format
        st.write("**Found locations:**")
        for loc in matches:
            st.write(f"- {loc}")
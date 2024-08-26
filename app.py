import streamlit as st
import networkx as nx
import requests
import plotly.graph_objects as go
import plotly.io as pio

# Function to fetch PPI data from the STRING database
def get_ppi_data(protein_list):
    url = "https://string-db.org/api/json/network"
    params = {
        "identifiers": "%0d".join(protein_list),  # List of proteins
        "species": "9606",  # Human
        "required_score": 900  # High confidence score
    }
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        st.error(f"Error fetching data: {response.status_code}")
        return []
    
    return response.json()

# Function to build a PPI network from data
def build_ppi_network(ppi_data):
    G = nx.Graph()
    for interaction in ppi_data:
        protein1 = interaction['preferredName_A']
        protein2 = interaction['preferredName_B']
        score = interaction['score']
        G.add_edge(protein1, protein2, weight=score)
    return G

# Function to visualize the network using Plotly with animations
def visualize_network_plotly(G):
    pos = nx.spring_layout(G, seed=42)  # Fixed seed for reproducibility

    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.append(x0)
        edge_y.append(y0)
        edge_x.append(x1)
        edge_y.append(y1)
        edge_x.append(None)  # None for separating lines between edges
        edge_y.append(None)

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='#888'),
        hoverinfo='none',
        mode='lines',
        name='Edges')

    node_x = []
    node_y = []
    node_text = []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=15,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line_width=2),
        name='Nodes'
    )

    # Create an animated effect for node sizes
    node_trace.update(
        marker=dict(
            size=[15] * len(G.nodes()),  # Set the initial size for nodes
            color=[0] * len(G.nodes()),  # Set initial colors
        ),
        mode='markers+text'
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=0, l=0, r=0, t=40),
                        xaxis=dict(showgrid=True, zeroline=False),
                        yaxis=dict(showgrid=True, zeroline=False),
                        paper_bgcolor='rgb(245, 245, 245)',
                        plot_bgcolor='rgb(255, 255, 255)',
                        updatemenus=[
                        ###Can Add Something For Animation....   
                        ],
                        sliders=[{
                            'active': 0,
                            'steps': [
                                {
                                    'label': str(i),
                                    'method': 'animate',
                                    'args': [[None], {'frame': {'duration': 500, 'redraw': True}, 'mode': 'immediate'}]
                                } for i in range(1, 6)  # Create steps for animation
                            ],
                        }]
                    )
    )
    
    return fig

# Streamlit app layout
st.markdown("""
    <style>
    .header {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .header img {
        width: 150px;
        height: auto;
    }
    .footer {
        text-align: center;
        font-weight: bold;
        color: #5B2A7A;
        margin-top: 20px;
    }
    </style>
    <div class="header">
        <img src="https://media.istockphoto.com/id/1320786846/vector/made-in-india-vector-logo-with-indian-flag-painted-circles.jpg?s=612x612&w=0&k=20&c=79W9ygu_u1rSReQSSEDutUeFfCmN4vaoxN1e-3J51Xk=" alt="Logo">
    </div>
    <h1 style='text-align: center;'>Protein-Protein Interaction Network Visualization</h1>
""", unsafe_allow_html=True)

st.markdown("""
    **Enter a list of protein names separated by commas** (e.g., TP53, BRCA1, EGFR):
""")

# Input for protein names
user_input = st.text_input("Proteins", "TP53, BRCA1, EGFR")
proteins = [protein.strip() for protein in user_input.split(",")]

if st.button("Generate Network"):
    if proteins:
        with st.spinner('Fetching data...'):
            # Fetch PPI data
            ppi_data = get_ppi_data(proteins)
            
            # Check if any PPI data was fetched
            if ppi_data:
                # Build and visualize network
                G = build_ppi_network(ppi_data)
                fig = visualize_network_plotly(G)
                
                # Display the plotly chart
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("No PPI data found for the provided protein list.")
    else:
        st.write("Please enter a list of proteins.")

st.markdown("<h6 style='text-align: center; font-weight: bold; color: #5B2A7A;'>Designed and Maintained By <a href='https://www.linkedin.com/in/nishant-thalwal-a32091219/'>Nishant Thalwal</a></h6>", unsafe_allow_html=True)

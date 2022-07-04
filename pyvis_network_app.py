import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import numpy as np


# Set header title
st.title('Modernização SNs')

def aggrid_interactive_table(df: pd.DataFrame):
    """Creates an st-aggrid interactive table based on a dataframe.

    Args:
        df (pd.DataFrame]): Source dataframe

    Returns:
        dict: The selected row
    """
    options = GridOptionsBuilder.from_dataframe(
        df, enableRowGroup=True, enableValue=True, enablePivot=True
    )

    options.configure_side_bar()

    options.configure_selection("single")
    selection = AgGrid(
        df,
        enable_enterprise_modules=True,
        gridOptions=options.build(),
        theme="light",
        update_mode=GridUpdateMode.MODEL_CHANGED,
        allow_unsafe_jscode=True,
    )

    return selection

df_consolidate = pd.read_csv('data/df_consolidate_clusters.csv')
df_dir = pd.read_csv('data/diretoria.csv')
df_com = pd.read_csv('data/comunidade.csv')

unique_dir = list(np.sort(df_dir.diretoria.unique()))
unique_com = list(np.sort(df_com.comunidade.unique()))
unique_cluster = list(np.sort(df_consolidate.id_cluster.unique()))
min_len_cluster = df_consolidate.len_cluster.min()
max_len_cluster = df_consolidate.len_cluster.max()

# Implement multiselect dropdown menu for option selection (returns a list)
index_clusters_dir = unique_cluster
index_clusters_com = unique_cluster

if st.checkbox('Fitrar por DIRETORIA'):
    selected_diretoria = st.multiselect('Selecione uma DIRETORIA:', unique_dir)
    index_clusters_dir = df_dir.loc[df_dir.diretoria.isin(selected_diretoria),"id_cluster"].unique()

if st.checkbox('Fitrar por COMUNIDADE'):
    selected_comunidade = st.multiselect('Selecione uma COMUNIDADE:', unique_com)
    index_clusters_com = df_com.loc[df_com.comunidade.isin(selected_comunidade),"id_cluster"].unique()

selection_cluster_id = list(set(index_clusters_dir)&set(index_clusters_com))
print(selection_cluster_id)


#if st.checkbox('Fitrar por Tamanho do Cluster'):
#    x = st.slider(
#     'Select a range of values',
#     min_len_cluster, max_len_cluster, (min_len_cluster, max_len_cluster))
#    st.write(f"{range(x[0],x[1])}")

try:
    if len(selection_cluster_id) == 0:
        st.write("Selecione ao menos um filtro")
    else:
        st.write("Para plotar o Grafo do Cluster, clique em um tupla:")
        selection = aggrid_interactive_table(df=df_consolidate[df_consolidate.id_cluster.isin(selection_cluster_id)])
        dict_selection = selection['selected_rows'][0]
        target_cluster = dict_selection['id_cluster']
        print(f"\n\n{target_cluster}")

        G = nx.read_gpickle(f"data/clusters/{target_cluster}.pkl")
        # Initiate PyVis network object
        drug_net = Network(
                           height='400px',
                           width='100%',
                           bgcolor='white',
                           font_color='#222222'
                          )

        # Take Networkx graph and translate it to a PyVis graph format
        drug_net.from_nx(G)

        # Generate network with specific layout settings
        drug_net.repulsion(
                            node_distance=420,
                            central_gravity=0.33,
                            spring_length=110,
                            spring_strength=0.10,
                            damping=0.95
                           )

        # Save and read graph as HTML file (on Streamlit Sharing)
        try:
            path = '/tmp'
            drug_net.save_graph(f'{path}/pyvis_graph.html')
            HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Save and read graph as HTML file (locally)
        except:
            path = '/html_files'
            drug_net.save_graph(f'{path}/pyvis_graph.html')
            HtmlFile = open(f'{path}/pyvis_graph.html', 'r', encoding='utf-8')

        # Load HTML file in HTML component for display on Streamlit page
        components.html(HtmlFile.read(), height=435)
except:
    pass


st.markdown(
    """
    <br>
    <h6><a href="https://github.com/kennethleungty/Pyvis-Network-Graph-Streamlit" target="_blank">GitHub Repo</a></h6>
    <h6><a href="https://kennethleungty.medium.com" target="_blank">Medium article</a></h6>
    <h6>Disclaimer: This app is NOT intended to provide any form of medical advice or recommendations. Please consult your doctor or pharmacist for professional advice relating to any drug therapy.</h6>
    """, unsafe_allow_html=True
    )

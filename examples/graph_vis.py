from yfiles_jupyter_graphs import GraphWidget

def display_graph(graph, hide_edge=True, meta=False):
    styles = { "Protein": {"color" : "#01C0B5"},
        "Compound": {"color" : "#C51CC6"},
        "Variant": {"color" : "#8391BB"},
        "Reaction": {"color" : "#FF67FF"},
        "Gene": {"color" : "#3863F2"},
        "ProteinDomain": {"color" : "#81BBB8"},
        "DietarySupplement": {"color" : "#63bde8"},
        "Anatomy": {"color" : "#00C459"},
        "BiologicalProcess": {"color" : "#E79F0C"},
        "Food": {"color" : "#FFA726"},
        "Organism": {"color" : "#666600"},
        "Disease": {"color" : "#FE2B59"},
        "EC": {"color" : "#9933FF"},
        "SideEffect": {"color" : "#8ACFF6"},
        "Pathway": {"color" : "#FFC80D"},
        "PwGroup": {"color" : "#FFC80D"},
        "Complex": {"color" : "#0F8A84"},
        "MolecularFunction": {"color" : "#FF8E00"},
        "CellType": {"color" : "#51B961"},
        "MiRNA": {"color" : "#3863F2"},
        "Haplotype": {"color" : "#8391BB"},
        "CellularComponent": {"color" : "#FF4D0D"},
        "Symptom": {"color" : "#FDC3FD"},
        "Cytoband": {"color" : "#8391BB"},
        "ProteinFamily": {"color" : "#177C77"},
        "None": {"color" : "#80899a"},
        "PharmacologicClass": {"color" : "#BEBADA"}}
    w= GraphWidget(graph=graph)
    if meta==False:
        for k in list(styles.keys()):
            styles[k]["label"]="name"
        w.set_node_label_mapping(lambda index, node : node["properties"][styles.get(node["properties"]["label"], {"label":"label"})["label"]] if 'name' in node["properties"] else node["properties"]['identifier'])
    w.set_node_styles_mapping(lambda index, node : styles.get(node["properties"]["label"], {}))
    if hide_edge:
        w.set_edge_label_mapping(lambda index, edge : None)
    #w.graph_layout = "organic_edge_router"
    w.set_sidebar(start_with='Neighborhood')
    w.show()


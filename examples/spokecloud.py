import numpy as np
import pandas as pd
import re
from graph_vis import display_graph
from open_neo4j import open_driver, get_graph, open_gds, make_graph_projection
import warnings
from sklearn.preprocessing import minmax_scale
warnings.filterwarnings('ignore')
warnings.simplefilter('ignore')

node_pattern = re.compile(r'\(n[0-9]+:[A-Za-z]+\)')
edge_pattern = re.compile(r'\[:[A-Za-z_]+\]')




SIMPLE_DWPC_QUERY = """
    MATCH (n0:%s) WHERE n0.identifier IN %s
    MATCH path=%s
    %s
    WITH path, %s, [
    %s
    ] AS degrees
    WITH %s, sum(reduce(pdp = 1.0, d in degrees| pdp * d ^ -0.7)) AS DWPC, count(path) AS PC
    %s
    RETURN elementId(%s) as Node_ID, %s.name as Node_Name, PC, DWPC ORDER BY DWPC DESC LIMIT %s
""" 

DWPC_MULTI_GENELISTS_QUERY = """
    WITH %s as gene_lists
    UNWIND gene_lists AS row
    WITH row[0] as gs, row[1] as gene_list
    CALL {
        WITH gs,gene_list
        %s
    }
    RETURN gs, Node_ID, Node_Name, PC, DWPC ORDER BY DWPC DESC
"""

GET_GENE_SET_SPOKE_NODE_IDS_QUERY = """
CALL {
    USE pkcomposite.pk
    MATCH (:GeneSet {identifier:'%s'})-[]-()-[]-(gp:%s)
    RETURN COLLECT(DISTINCT gp.identifier) AS ids
}
CALL {
    USE pkcomposite.pkspoke
    WITH ids
    MATCH path=(n:%s) WHERE n.identifier IN ids
    RETURN DISTINCT ID(n) as nodeId
}
RETURN DISTINCT nodeId
"""

OVERALL_WEIGHTED_DWPC_QUERY = """
CALL {
    USE compositenasa.glds
    MATCH %s %s
    RETURN COLLECT(DISTINCT n.identifier) AS ids
}
CALL {
    USE compositenasa.gldsspoke
    WITH ids
    MATCH %s WHERE n0.identifier IN ids
    RETURN DISTINCT n0.identifier AS overlap_nodes
}
CALL {
    WITH overlap_nodes
    USE compositenasa.glds
    MATCH path_1=%s {identifier:overlap_nodes})%s
    RETURN  n { .* } AS p, r
}
CALL {
    WITH overlap_nodes
    USE compositenasa.gldsspoke
    WITH COLLECT(overlap_nodes) as overlap
    MATCH path_2=%s WHERE n0.identifier IN overlap
    WITH [%s] AS degrees, n0, n1
    WITH n0, %s, sum(reduce(pdp = 1.0, d in degrees| pdp * d ^ -0.7)) AS DWPC
    RETURN n0, %s, DWPC
}
WITH n1, sum(r.%s*DWPC) as weighted_DWPC
RETURN DISTINCT %s.identifier as identifier, %s.name as name , weighted_DWPC ORDER BY weighted_DWPC DESC
"""

PAGERANK_WEIGHT_QUERY = """
CALL {
    USE compositenasa.glds
    MATCH %s %s
    WITH n, AVG(r.%s) as weight
    RETURN DISTINCT n.identifier AS id, weight
}
CALL {
    USE compositenasa.gldsspoke
    WITH id
    MATCH (n0:Gene) WHERE n0.identifier = id
    RETURN DISTINCT ID(n0) as nodeId, n0.identifier as Node
}
RETURN DISTINCT nodeId, Node, weight
"""

PAGERANK_SINGLE_GENELIST_QUERY = """
CALL {
    USE compositenasa.glds
    MATCH %s%s
    RETURN COLLECT(DISTINCT n.identifier) AS ids
}
CALL {
    USE compositenasa.gldsspoke
    WITH ids
    MATCH (g:%s) WHERE g.identifier IN ids
    RETURN DISTINCT ID(g) AS overlap_genes
}
WITH COLLECT(overlap_genes) as sourceNodes
CALL {
    USE compositenasa.gldsspoke
    WITH sourceNodes
    CALL gds.pageRank.stream('%s', { sourceNodes:sourceNodes, maxIterations:40,dampingFactor:%s})
    YIELD nodeId, score
    RETURN nodeId, score 
}
RETURN nodeId, score ORDER BY score DESC
"""

def plot_dwpc_paths(genelab, driver, spoke_metapath, group_by_node, gs_metapath, gs_filter, inner_nodes, max_show = 10):
    query = """
    WITH $inner_nodes as inner_nodes
    UNWIND inner_nodes AS n
    CALL {
        WITH n
        MATCH path=%s
        WHERE n0.identifier in $gene_list AND %s.identifier=n
        RETURN path LIMIT %s
    } 
    RETURN path
    """
    geneset_lists = list(genelab.run_cypher("MATCH %s %s RETURN DISTINCT n.identifier as i" % (gs_metapath, gs_filter)).i.unique())
    display_graph(get_graph(driver, query % (spoke_metapath, group_by_node, max_show), 'spoke', params={'gene_list':geneset_lists, 'inner_nodes':inner_nodes}), hide_edge=True, meta=False)


def run_pagerank(db, G, sourceNodes):
    pr_results = db.pageRank.stream(
        G,
        sourceNodes=sourceNodes,
        maxIterations=40,
        dampingFactor=0.33
    )
    return pr_results

def run_multi_pagerank(spoke, G, node_info_df, pagerank_weight_df):
    multi_pagerank_df = node_info_df.drop_duplicates()
    for source_node, weight in pagerank_weight_df[['nodeId', 'weight']].values:
        col = str(int(source_node))
        multi_pagerank_df = multi_pagerank_df.merge(run_pagerank(spoke, G, [int(source_node)]), on='nodeId')
        multi_pagerank_df = multi_pagerank_df.rename(columns={'score':col})
        multi_pagerank_df.loc[:,col] = multi_pagerank_df[col].values*weight
    cols = multi_pagerank_df.columns.values[4:]
    multi_pagerank_df = pd.concat((multi_pagerank_df[multi_pagerank_df.columns.values[:4]], 
                                   pd.DataFrame(minmax_scale(multi_pagerank_df[cols].values, axis=1), columns=cols)), axis=1)
    multi_pagerank_df.loc[:,'mean_pr'] = np.mean(multi_pagerank_df[[str(i) for i in pagerank_weight_df.nodeId.values]].values, axis=1)
    return multi_pagerank_df



def display_top_nodes(df, driver, n_top=10, score_col='score', asc=False, db_name='humanspoke'):
    top_node_df = df.sort_values(score_col, ascending=asc)
    top_node_df.loc[:,'Rank'] = top_node_df.groupby('Node_Type').cumcount(ascending=True).values + 1
    top_node_df = top_node_df[top_node_df.Rank <= n_top]
    query = "MATCH path=(n1)-[]->(n2) WHERE ID(n1) IN $node_1 AND ID(n2) IN $node_2 RETURN path"
    top_nodes = top_node_df.nodeId.unique()
    display_graph(get_graph(driver, query, db_name, params={'node_1':top_nodes, 'node_2':top_nodes}), hide_edge=True, meta=False)
    return top_node_df

def get_id(db, nt, identifier):
    if type(identifier) == str:
        identifier = '"%s"' % identifier
    query = 'MATCH (n:%s {identifier:%s}) RETURN DISTINCT ID(n) as i'
    node_id = db.run_cypher(query % (nt, identifier)).i.values[0]
    return node_id


def get_node_ids_in_genelist(db, nt, identifier):
    node_id = db.run_cypher(GET_GENE_SET_SPOKE_NODE_IDS_QUERY % (identifier, nt, nt)).nodeId.values
    return node_id

def get_projection_info(db, projection_name):
    query = """CALL gds.degree.stream('%s')
            YIELD nodeId, score
            RETURN nodeId as nodeId, gds.util.asNode(nodeId).identifier AS Node, gds.util.asNode(nodeId).name AS Node_Name, HEAD(LABELS(gds.util.asNode(nodeId))) AS Node_Type
            """
    node_info_df = db.run_cypher(query % projection_name)
    return node_info_df


def get_nodes_from_gene_list(passkey, filter_list='', nt='Gene'):
    if filter_list !='':
        filter_list = 'WHERE gs.identifier IN %s ' % filter_list
    query = 'MATCH (gs:GeneSet)-[]-()-[]-(n:%s) %sRETURN DISTINCT gs.identifier as GeneSet, COLLECT(DISTINCT n.identifier) as Nodes'
    geneset_lists = [list(row) for row in passkey.run_cypher(query % (nt, filter_list)).values]
    return geneset_lists
    
def get_inner_dwpc_degree_str(edges):
    degree_str = []
    inner_degree_str = "size([(n%s)-[:%s]-() | n%s]), size([()-[:%s]-(n%s) | n%s])"
    for i, edge in enumerate(edges):
        degree_str.append(inner_degree_str%(i, edge, i, edge, i+1, i+1))
    degree_str = ',\n'.join(degree_str)
    return degree_str

def get_dwpc(spoke, metapath, start_lists, start_nt, group_by_node, max_results, multi_group, filter_str = '', pc_filter = 'WHERE PC > 1'):
    edges = [edge[2:-1] for edge in edge_pattern.findall(metapath)]
    query = ''
    if multi_group==True:
        query = SIMPLE_DWPC_QUERY % (start_nt, 'gene_list', metapath, filter_str, 'gs, '+group_by_node, get_inner_dwpc_degree_str(edges), 'gs, '+group_by_node, pc_filter, group_by_node, group_by_node, max_results)
        query = DWPC_MULTI_GENELISTS_QUERY % (start_lists, query)
    else:
        query = SIMPLE_DWPC_QUERY % (start_nt, start_lists, metapath, filter_str, group_by_node, get_inner_dwpc_degree_str(edges), group_by_node, pc_filter, group_by_node, group_by_node, max_results)
    df = spoke.run_cypher(query)
    return df

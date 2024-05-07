from graphdatascience import GraphDataScience
from neo4j import GraphDatabase, basic_auth

i, u, p = '','',''
with open('spoke_auth', 'r') as auth_file:
    i, u, p = [i.strip() for i in auth_file.readlines()]

def open_driver():
    return GraphDatabase.driver(i, auth=basic_auth(u, p), encrypted=False)

def get_graph(driver, query, db='spoke', params={}):
    with driver.session(database=db) as session:
        graph = session.run(query, **params).graph()
    return graph

def open_gds(db):
    return GraphDataScience(i, auth=(u, p), database=db)

def make_graph_projection(db, projection_name, projection_query):
    query = """
    CALL gds.graph.list() YIELD graphName, database, nodeCount, relationshipCount
    RETURN graphName, database, nodeCount, relationshipCount
    """
    current_df = db.run_cypher(query)
    if projection_name in current_df.graphName.values:
        print('Dropping Projection Graph')
        print(db.run_cypher("CALL gds.graph.drop('%s') YIELD graphName;" % projection_name))
    print('Making Projection Graph')
    print(db.run_cypher(projection_query))
    G=db.graph.get(projection_name)
    return G



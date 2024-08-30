#streamlit run .\test1.py --server.port 8502
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from server.neo4j.main import Neo4jWorker
from server.utils import *
from configs import *
import streamlit
from streamlit_agraph import agraph, Node, Edge, Config


if __name__ == '__main__':
    source_id_list=['dfad29d6-7961-4d21-9dca-02a9d1d51f63','bc03fc7a-d466-4b35-8d39-f4c0ac779de2']
    
    graph=create_graph_database_connection()
    neo4j_worker=Neo4jWorker(graph)
    query="""
    MATCH (d:Document)-[r]->(n)
    where d.source_id in $source_id_list
    RETURN collect(distinct {id:id(d), title:d.source_id, label:labels(d)[0],text:d.text,source:d.source}) as documents, collect(distinct {id:id(n), title:n.id, label:labels(n)[0]}) as nodes, collect(distinct {source:id(d), target:id(n), label:type(r)}) as relations
    """
    query2="""
    MATCH (d:Document)-[r]->(n)
    where d.source_id in $source_id_list
    WITH n
    MATCH (n)-[r2]->(m)
    RETURN collect(distinct {source:id(n), target:id(m), label:type(r2)}) as relations
    """
    result=neo4j_worker.run(query,{'source_id_list':source_id_list})
    result2=neo4j_worker.run(query2,{'source_id_list':source_id_list})
    neo4j_worker.close_db_connection()
    
    
    nodes=[]
    edges=[]
    
    document_list=result[0]['documents']
    node_list=result[0]['nodes']
    relation_list=result[0]['relations']+result2[0]['relations']
    
    print(relation_list)
    
    #显示title和label与预期相反
    for document in document_list:
        nodes.append(Node(id=document['id'], title=document['label'],  label=document['title'], text=document['text'], source=document['source'],color='#F7A7A6'))
        
    for node in node_list:
        nodes.append(Node(id=node['id'], title=node['label'],  label=node['title']))
        
    for relation in relation_list:
        edges.append(Edge(source=relation['source'], target=relation['target'], label=relation['label']))
    
    streamlit.title("Knowledge Graph") 
    agraph(nodes=nodes, edges=edges, config=Config(width=1000, height=800, directed=True, nodeHighlightBehavior=True, highlightColor="#F7A7A6", collapsible=True, node={'color': 'lightblue', 'fontWeight': 'bold', 'fontSize': 14, 'labelProperty': 'title', 'labelHighlightBold': True, 'highlightFontSize': 16, 'highlightFontWeight': 'bold', 'highlightStrokeColor': 'blue', 'highlightStrokeWidth': 2}))

    
    
    
    

        
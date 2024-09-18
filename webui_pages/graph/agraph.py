from server.neo4j.main import Neo4jWorker
from server.utils import *
from configs import *
from streamlit_agraph import agraph, Node, Edge, Config

#效率有待提高
def get_agraph_by_graphinfo(info_dict:dict):
    """根据图信息绘制知识图谱

    Args:
        info_dict (dict): Neo4jWorker.get_graphinfo_by_source_id()的返回值
            result_dict={"document_list":document_list,"node_list":node_list,"relation_list":relation_list}

    Returns:
        agraph
    """
    
    nodes=[]
    edges=[]
    
    document_list=info_dict['document_list']
    node_list=info_dict['node_list']
    relation_list=info_dict['relation_list']
    
    #显示title和label与预期相反
    for document in document_list:
        nodes.append(Node(id=document['id'], title=document['label'],  label=document['title'], text=document['text'], source=document['source'],color='#F7A7A6'))
        
    for node in node_list:
        nodes.append(Node(id=node['id'], title=node['label'],  label=node['title']))
        
    for relation in relation_list:
        edges.append(Edge(source=relation['source'], target=relation['target'], label=relation['label']))
    
    return agraph(nodes=nodes, edges=edges, config=Config(directed=True, nodeHighlightBehavior=True, highlightColor="#F7A7A6", collapsible=True, node={'color': 'lightblue', 'fontWeight': 'bold', 'fontSize': 14, 'labelProperty': 'title', 'labelHighlightBold': True, 'highlightFontSize': 16, 'highlightFontWeight': 'bold', 'highlightStrokeColor': 'blue', 'highlightStrokeWidth': 2}))
    
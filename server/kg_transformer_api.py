from server.knowledge_graph_transformer import LLMGraphTransformer
from server.utils import BaseResponse
from server.utils import get_llm
from configs import KG_LLM_MODELS
from fastapi import Body
from typing import List, Optional
from langchain_core.documents import Document
from langchain_community.graphs.graph_document import GraphDocument
from server.neo4j.main import Neo4jWorker
from server.knowledge_base.kb_service.base import KBServiceFactory
from server.utils import create_graph_database_connection


def rebuild_graph_by_filename_list(
        filename_list: List[str],
        kb_name: str,
        allowed_nodes: List[str] = None,
        allowed_relationships: List[str] = None,
        model_name: str = KG_LLM_MODELS[0],
        strict_mode: bool = False, 
):
    """
    对同一个知识库中若干向量化文档的重新构建KG。
    """
    llm = get_llm(model_name)
    
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=allowed_nodes,
        allowed_relationships=allowed_relationships,
        strict_mode=strict_mode,
    )
    
    documents = []
    
    kb=KBServiceFactory.get_service_by_name(kb_name)#这里可能会获得空向量
    for file_name in filename_list:
        result=kb.list_docs(file_name)
        documents=[]
        for item in result:
            document=Document(page_content="null")
            document.page_content=item.page_content
            document.metadata=item.metadata
            document.metadata["source_id"]=item.id
            documents.append(document)
            
    graph_documents = transformer.convert_to_graph_documents(documents)
    
    graph=create_graph_database_connection("neo4j")
    worker=Neo4jWorker(graph)
    
    #这里应该是删除了之前的文档，然后保存新的文档
    worker.delete_nodes_and_relationships_by_filename_list(filename_list)
    
    worker.save_graphDocuments_in_neo4j(graph_documents)
    
    

def rebuilt_graph_by_source_id_list(
        source_id_list: List[str],
        kb_name: str,
        allowed_nodes: List[str] = None,
        allowed_relationships: List[str] = None,
        model_name: str = KG_LLM_MODELS[0],
        strict_mode: bool = False, 
):  
    """
    对同一个知识库中若干条向量的重新构建KG。

    Args:
        source_id_list (List[str]): _description_
        kb_name (str): _description_
        allowed_nodes (List[str], optional): _description_. Defaults to None.
        allowed_relationships (List[str], optional): _description_. Defaults to None.
        model_name (str, optional): _description_. Defaults to KG_LLM_MODELS[0].
        strict_mode (bool, optional): _description_. Defaults to False.
    """
    llm = get_llm(model_name)
    
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=allowed_nodes,
        allowed_relationships=allowed_relationships,
        strict_mode=strict_mode,
    )
    
    kb=KBServiceFactory.get_service_by_name(kb_name)#这里可能会获得空向量
    result=kb.get_doc_by_ids(source_id_list)
    
    
    documents=[]
    for item,source_id in zip(result,source_id_list):
        document=Document(page_content="null")
        document.page_content=item.page_content
        document.metadata=item.metadata
        document.metadata["source_id"]=source_id
        documents.append(document)
        
    
    graph_documents = transformer.convert_to_graph_documents(documents)
    
    graph=create_graph_database_connection("neo4j")
    worker=Neo4jWorker(graph)
    
    #这里应该是删除了之前的向量图谱，然后保存新的向量图谱
    worker.delete_nodes_and_relationships_by_source_id_list(source_id_list)
    
    worker.save_graphDocuments_in_neo4j(graph_documents)
    

def texts2graphs(
        texts: List[str] ,
        allowed_nodes: List[str] ,
        allowed_relationships: List[str] ,
        model_name :str=KG_LLM_MODELS[0],
        strict_mode: bool=False
) -> List[GraphDocument]:
    
    llm=get_llm(model_name)
    
    transformer = LLMGraphTransformer(
        llm=llm,
        allowed_nodes=allowed_nodes,
        allowed_relationships=allowed_relationships,
        strict_mode=strict_mode,
    )
    
    documents = []
    for text in texts:
        document=Document(page_content=text)
        documents.append(document)
        
    return transformer.convert_to_graph_documents(documents)
    


def files2graphs(
        files: List[str] = Body(..., description="要转换的文档列表", examples=[["CTI.txt"]]),
        kb_name: str = Body(..., description="知识库名称", examples=["CTI"]),
        allowed_nodes: List[str] = Body(..., description="待抽取的实体类型", examples=[["Person", "Organization"]]),
        allowed_relationships: List[str] = Body(..., description="待抽取的关系", examples=[["CEO", "FOUNDED"]]),
        model_name : str = Body(KG_LLM_MODELS[0], description="用于生成KG的LLM模型名称。"),
        strict_mode: bool = Body(False, description="是否严格模式。(当为True时，仅抽取允许的实体和关系)"),
)-> BaseResponse:
    rebuild_graph_by_filename_list(files,kb_name,allowed_nodes,allowed_relationships,model_name,strict_mode)
    return BaseResponse(msg="success")

def docs2graphs(
        source_id_list: List[str] = Body(..., description="要转换的文档ID列表", examples=[["b0737aaa-5268-4e7d-8e2c-3944d0b14444","32edca9f-051e-4223-b8ae-3124ca533a70"]]),
        kb_name: str = Body(..., description="知识库名称", examples=["CTI"]),
        allowed_nodes: List[str] = Body(..., description="待抽取的实体类型", examples=[["Person", "Organization"]]),
        allowed_relationships: List[str] = Body(..., description="待抽取的关系", examples=[["CEO", "FOUNDED"]]),
        model_name : str = Body(KG_LLM_MODELS[0], description="用于生成KG的LLM模型名称。"),
        strict_mode: bool = Body(False, description="是否严格模式。(当为True时，仅抽取允许的实体和关系)"),
)-> BaseResponse:
    rebuilt_graph_by_source_id_list(source_id_list,kb_name,allowed_nodes,allowed_relationships,model_name,strict_mode)
    return BaseResponse(msg="success")


def texts_to_graphs(
        texts: List[str] = Body(..., description="要转换的文本列表", examples=[["马斯克是SpaceX和Tesla的CEO。", "苹果公司由史蒂夫·乔布斯、史蒂夫·沃兹尼亚克和罗纳德·韦恩创立。"]]),
        allowed_nodes: List[str] = Body(..., description="待抽取的实体类型", examples=[["Person", "Organization"]]),
        allowed_relationships: List[str] = Body(..., description="待抽取的关系", examples=[["CEO", "FOUNDED"]]),
        model_name: str = Body(KG_LLM_MODELS[0], description="用于生成KG的LLM模型名称。"),
        strict_mode: bool = Body(False, description="是否严格模式。(当为True时，仅抽取允许的实体和关系)")
) -> BaseResponse:
    return BaseResponse(data=texts2graphs(texts,allowed_nodes,allowed_relationships,model_name,strict_mode))

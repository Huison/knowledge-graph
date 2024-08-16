from fastapi import APIRouter
from fastapi import Body

from app.services.knowledge_graph_service import KnowledgeGraphService

router = APIRouter()


@router.get("/all-relationships-of-node/node-name")
async def get_all_relationships_of_node(node_name: str):
    graph = KnowledgeGraphService()
    res = graph.query_node_all_relations_by_name(node_name)
    print(res)
    return res


@router.get("/query-relationship-between-nodes")
async def query_relationship_between_nodes(name1, name2):
    graph = KnowledgeGraphService()
    res = graph.query_relationship_between_nodes(name1, name2)
    return res


@router.post("/create-kg-using-llm")
async def create_kg_using_llm(user_input: str = Body(...),
                              prompt: str = Body(...)):
    graph = KnowledgeGraphService()
    res = graph.create_kg_using_llm(user_input, prompt)
    return res


@router.get("/query-nodes")
async def query_nodes(limit):
    graph = KnowledgeGraphService()
    res = graph.query_nodes(limit)
    return res

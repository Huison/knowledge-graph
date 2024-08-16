from fastapi import APIRouter

from app.api.routes import example, knowledge_graph, chat

api_router = APIRouter()

api_router.include_router(example.router, prefix="/example", tags=["example"])
api_router.include_router(knowledge_graph.router, prefix="/knowledge-graph", tags=["knowledge-graph"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])

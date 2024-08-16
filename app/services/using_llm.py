from fastapi import FastAPI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langserve import add_routes

from app.config.config import settings

# 1. Create prompt template
system_template = "Translate the following into {language}:"
prompt_template = ChatPromptTemplate.from_messages([
    ('system', system_template),
    ('user', '{text}')
])

# 2. Create model
llm = ChatOpenAI(
    temperature=0,
    model="glm-4",
    openai_api_key=settings.zhipu_api_key,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

# 3. Create parser
parser = StrOutputParser()

# 4. Create chain
chain = prompt_template | llm | parser

# 5. App definition
app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="A simple API server using LangChain's Runnable interfaces",
)

# 6. Adding chain route
add_routes(
    app,
    chain,
    path="/chain",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)

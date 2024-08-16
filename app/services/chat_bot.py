from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.config.config import settings

llm = ChatOpenAI(
    temperature=0,
    model="glm-4",
    openai_api_key=settings.zhipu_api_key,
    openai_api_base="https://open.bigmodel.cn/api/paas/v4/"
)

res = llm.invoke([HumanMessage(content="我是huison")])
print(res.content)

res1 = llm.invoke([HumanMessage(content="我叫什么名字?")])
print(res1.content)
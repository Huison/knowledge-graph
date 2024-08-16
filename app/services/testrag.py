from app.llm_api.zhipu_api import Zhipu

zhipu = Zhipu()
from langchain.vectorstores import DocArrayInMemorySearch
from langchain_core.documents import Document

documents = [
    Document(
        page_content="狗是很好的伴侣，以忠诚和友善著称。",
        metadata={"source": "pets-doc"},
    ),
    Document(
        page_content="猫是独立的宠物，通常喜欢有自己的空间。",
        metadata={"source": "mammal-pets-doc"},
    ),
    Document(
        page_content="金鱼是初学者喜爱的宠物，需要的护理相对简单。",
        metadata={"source": "fish-pets-doc"},
    ),
    Document(
        page_content="鹦鹉是一种聪明的鸟类，能够模仿人类说话。",
        metadata={"source": "bird-pets-doc"},
    ),
    Document(
        page_content="兔子是群居动物，需要足够的空间跳来跳去。",
        metadata={"source": "mammal-pets-doc"},
    ),
]
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.embeddings import ZhipuAIEmbeddings
from app.config.config import settings

embeddings = ZhipuAIEmbeddings(
    model="embedding-2",
    api_key=settings.zhipu_api_key,
)
index = VectorstoreIndexCreator(
    vectorstore_cls=DocArrayInMemorySearch,
    embedding=embeddings
).from_documents(documents)

retriever = index.vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"filter": {"source": "pets-doc"}})

query = "忠诚的宠物"
results = retriever.get_relevant_documents(query, metadata={"source": "pets-doc"})
for i, result in enumerate(results):
    print(f"结果 {i+1}:")
    print(f"内容: {result.page_content}")
    print(f"来源: {result.metadata['source']}")
    print("-" * 50)
# all_results = index.vectorstore.search(
#     query="狗",
#     search_type="similarity",
#     metadata_filter={"source": "pets-doc"}
# )
#
# for all_result in all_results:
#     print(all_result)

from langserve import RemoteRunnable

remote_chain = RemoteRunnable("http://localhost:8000/chain/")
res = remote_chain.invoke({"language": "中文", "text": "as warm as the sunshine"})
print(res)

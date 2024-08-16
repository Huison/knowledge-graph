import json
from typing import Optional

import requests
from fastapi import APIRouter

router = APIRouter()


@router.post("/chat")
async def chat(query: Optional[str] = None):
    url = 'http://192.168.1.24:7861/chat/chat'
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    json_example = {'edges': [{'data': {'color': '#FFA07A',
                                        'label': 'label 1',
                                        'source': 'source 1',
                                        'target': 'target 1'}},
                              {'data': {'color': '#FFA07A',
                                        'label': 'label 2',
                                        'source': 'source 2',
                                        'target': 'target 2'}}
                              ],
                    'nodes': [{'data': {'color': '#FFC0CB', 'id': 'id 1', 'label': 'label 1'}},
                              {'data': {'color': '#90EE90', 'id': 'id 2', 'label': 'label 2'}},
                              {'data': {'color': '#87CEEB', 'id': 'id 3', 'label': 'label 3'}}]}

    __retriever_prompt = f"""
            你是一名人工智能专家，擅长创建知识图谱，目标是根据给定的输入或请求捕捉关系。
            你的任务是根据输入创建一个知识图谱。
            节点必须有一个标签参数，其中标签是来自输入的直接单词或短语。
            边也必须有一个标签参数，其中标签是直接来自输入的单词或短语。
            响应只能是 JSON 格式，我们可以用 python 进行 jsonify 并直接输入 cy.add(data)，包含 “color ”属性，以便在前端显示图表。
            您可以参考给出的示例： {json_example}.
            确保边的目标和来源与现有节点相匹配。
            """
    messages = [
        {"role": "system", "content": "你现在扮演信息抽取的角色，要求根据用户输入和AI的回答，正确提取出信息。"},
        {"role": "user", "content": query},
        {"role": "user", "content": __retriever_prompt}
    ]

    messages_str = json.dumps(messages, ensure_ascii=False)

    data = {
        "query": f'请帮我分析{query}中的实体关系，并将结果输出为json格式',
        "conversation_id": "",
        "history_len": -1,
        "stream": False,
        "model_name": "chatglm3-6b",
        "temperature": 0.7,
        "max_tokens": 0,
        "prompt_name": "default"
    }

    response = requests.post(url, headers=headers, json=data)

    res = response.text
    print(res)

    # json_str = res[len("data:"):].strip()
    # json_obj = json.loads(json_str)
    # return json_obj
    return res
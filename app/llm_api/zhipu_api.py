from zhipuai import ZhipuAI

from app.config.config import settings


class Zhipu:
    def __init__(self):
        self.client = ZhipuAI(api_key=settings.zhipu_api_key)

    def synchronous_chat(self, messages, model_name="glm-4"):
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0,
                stream=False,
                max_tokens=20480
            )
            return response.choices[0].message
        except Exception as e:
            return f"Error: {e}"

    def stream_chat(self, messages, model_name="glm-4"):
        try:
            response = self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                stream=True,
            )
        except Exception as e:
            return f"Error: {e}"

        for chunk in response:
            delta = chunk.choices[0].delta
            if delta:
                yield delta.content


if __name__ == '__main__':
    zhipu = Zhipu()

    input = f"2019年9月28日张三在香山参加微积分岗前培训，被任命为微积分助理工程师，同时被授予了中尉军衔。"
    f"2020年6月21日张三在大兴参加线性代数岗前培训，被任命为线性代数助理工程师。"
    f"2021年10月9日张三在大兴参加概率与统计岗前培训，被任命为概率与统计助理工程师。"
    f"2022年8月17日张三在大兴参加离散数学岗前培训，被任命为离散数学工程师。"
    f"2023年12月3日张三在大兴参加微分方程考试，被任命为微分方程工程师，同时也被任命为副科长。"
    f"计划2024年12月1日张三在大兴参加实分析和复分析的理论学习。"

    json_example = {
        'nodes': [
            {
                'data': {
                    'id': 'b6851e09-1346-4649-bcf0-dfcc377691c9',
                    'label': 'label1',
                    'name': 'name1'
                }
            },
            {
                'data': {
                    'id': 'f6ea5f95-f78d-4916-905a-cff24ffeea42',
                    'label': 'label2',
                    'name': 'name2'
                }
            }
        ],
        'edges': [
            {
                'data': {
                    'id': '022bd94c-d759-45df-abd6-1dbaef4e38a7',
                    'source': 'b6851e09-1346-4649-bcf0-dfcc377691c9',
                    'target': 'f6ea5f95-f78d-4916-905a-cff24ffeea42',
                    'label': 'label3',
                    'location': 'location1',
                    'date': 'date1'
                }
            },
            {
                'data': {
                    'id': '1610d9aa-387e-4d2e-8343-cdd8a00cbb33',
                    'source': 'b6851e09-1346-4649-bcf0-dfcc377691c9',
                    'target': '856571a5-1a07-4f52-b9eb-58c3c96d2f45',
                    'label': 'label4',
                    'location': 'location2',
                    'date': 'date2'
                }
            }
        ]
    }

    response = zhipu.synchronous_chat([
        {"role": "user", "content": "你是一名人工智能专家，擅长创建知识图谱,你的任务是根据用户输入创建一个知识图谱。"},
        {"role": "user", "content": f"{input}"},
        {"role": "user",
         "content": f"可以参考给出的示例: + {json_example}, 其中id为随机生成的，人的label是人物，事件的label为事件。"
                    f"请输出一个JSON格式的知识图谱数据，用于cytoscape库的渲染。"
         }
    ])

    result = response.content
    import json

    if '```' in result:
        graph_data = json.loads(result.split('```', 2)[1].replace("json", ''))
    else:
        graph_data = json.loads(result)

    print(graph_data)

import json
import uuid
from datetime import datetime
from typing import Sequence, Set

from loguru import logger
from py2neo import Graph, Node, ConnectionUnavailable, NodeMatcher, Relationship, RelationshipMatcher

from app.llm_api.zhipu_api import Zhipu


class KnowledgeGraphService(object):
    """
    连接图数据库neo4j
    """

    def __init__(self):
        # 读取yaml配置
        self.__url = "bolt://localhost:7687"
        self.__username = "neo4j"
        self.__password = "88888888"
        self.__connect_graph()

        self.__node_matcher = NodeMatcher(self.__graph) if self.__graph else None
        self.__relationship_matcher = RelationshipMatcher(self.__graph) if self.__graph else None

    def __connect_graph(self):
        try:
            self.__graph = Graph(self.__url, auth=(self.__username, self.__password))
        except ConnectionUnavailable as e:
            logger.error("连接失败")
            self.__graph = None

    def create_node(self, label, properties):
        """
        创建节点
        :param label: 节点标签
        :param properties: 节点属性
        :return: 创建的节点对象

        cytoscape.js展示知识图谱使用的实体或关系的id不能重复.
        """
        if not properties["id"]:
            properties['id'] = str(uuid.uuid4())
        node = Node(label, **properties)
        self.__graph.create(node)
        return node

    def create_meta_node(self, version: int):
        """
        创建元节点
        :return: 创建的元节点对象,记录创建时间等信息
        """
        meta_node = Node(
            'Meta',
            id=self.__meta_node_id,
            title='libai-graph meta node',
            text='store some meta info',
            # python获取当前时间
            timestamp=datetime.now(),
            version=version,
            status='active',
        )
        self.__graph.create(meta_node)
        return meta_node

    def query_meta_node(self):
        return self.__node_matcher.match('Meta', id=self.__meta_node_id).first()

    def query_data_version(self):
        return int(self.query_meta_node()['version'])

    def update_version(self):
        """
        更新元节点的版本号
        return: 更新后的元节点对象
        """
        meta_node = self.query_meta_node()
        if meta_node:
            meta_node['version'] += 1
            self.__graph.push(meta_node)
            return meta_node
        else:
            raise Exception('Meta node not found')

    def delete_node(self, label, name):
        matcher = NodeMatcher(self.__graph)
        node = matcher.match(label, name=name).first()
        self.__graph.delete(node)

    def delete_relationship(self, start_node_label, start_node_props, end_node_label, end_node_props, relation_type):
        """
        删除关系
        :param start_node_label: 起始节点标签
        :param start_node_props: 起始节点属性
        :param end_node_label: 结束节点标签
        :param end_node_props: 结束节点属性
        :param relation_type: 关系类型
        :return: 是否删除成功
        """
        start_node = self.__node_matcher.match(start_node_label, **start_node_props).first()
        end_node = self.__node_matcher.match(end_node_label, **end_node_props).first()

        if start_node and end_node:
            try:
                relationship = self.__relationship_matcher.match(
                    nodes=(start_node, end_node), r_type=relation_type
                ).first()
                if relationship:
                    self.__graph.separate(relationship)
                    logger.info(f"删除关系成功：{start_node_props} -[{relation_type}]-> {end_node_props}")
                    return True
                else:
                    logger.error(f"未找到符合条件的关系：{start_node_props} -[{relation_type}]-> {end_node_props}")
                    return False
            except Exception as e:
                logger.error(f"删除关系失败：{e}")
                return False
        else:
            logger.error(
                f"未找到符合条件的节点：{start_node_label} {start_node_props}, {end_node_label} {end_node_props}")
            return False

    def update_node(self, node, properties):
        ...

    def update_relationship(self, relationship, properties):
        ...

    def query_node(self, *label, **properties):
        return self.__node_matcher.match(*label, **properties)

    def query_relationship(self, nodes: Sequence | Set | None = None, r_type=None, **properties):
        return self.__relationship_matcher.match(nodes, r_type, **properties)

    def get_relationship_properties(self, start_name, end_name):
        query = (
            f"MATCH (n {{name: '{start_name}'}})-[r]-(m {{name: '{end_name}'}}) "
            f"RETURN properties(r) AS relationship_properties"
        )
        results = self.run_cypher(query)
        return results.data()

    def query_relationship_by_2person_name(self, first_person, second_person):
        rel = self.__graph.run(
            f"match(:`人物`{{name:'{first_person}'}})-[r]-(:`人物`{{name:'{second_person}'}}) return r, type(r)").data()
        return rel

    def query_path(self, start_node, end_node, rel_type, rel_properties):
        ...

    def query_nodes(self, limit: int = None):

        query = (
            f"MATCH (n)-[r]-(m) "
            f"RETURN r, type(r) AS relation_type, properties(r) AS relation_properties"
        )
        if limit is not None:
            query += f" LIMIT {limit}"
        results = self.run_cypher(query).data()
        return self._format_relationship_results(results)

    def run_cypher(self, query):
        result = self.__graph.run(query)
        return result

    def create_relationship(self, node1_label, node1_props, node2_label, node2_props, relation_type,
                            relation_props=None):
        node1 = self.__node_matcher.match(node1_label, **node1_props).first()
        node2 = self.__node_matcher.match(node2_label, **node2_props).first()

        if node1 and node2:
            relationship = Relationship(node1, relation_type, node2)
            if not relationship["id"]:
                relationship["id"] = str(uuid.uuid4())
            if relation_props:
                for k, v in relation_props.items():
                    relationship[k] = v
            try:
                self.__graph.create(relationship)
                return True
            except Exception as e:
                logger.error(f"创建关系失败：{e}")
                return False
        else:
            logger.error(f"未找到符合条件的节点：{node1_label} {node1_props}, {node2_label} {node2_props}")
            return False

    def batch_create_node(self, nodes: list[Node]):
        for node in nodes:
            self.__graph.create(node)

    def query_node_all_relations_by_name(self, node_name):
        query = (
            f"MATCH (n {{name: '{node_name}'}})-[r]-(m) "
            f"RETURN r, type(r) AS relation_type, properties(r) AS relation_properties"
        )
        results = self.run_cypher(query).data()
        return self._format_relationship_results(results)

    def query_relationship_between_nodes(self, name1, name2):
        query = (
            f"MATCH (n {{name: '{name1}'}})-[r]-(m {{name: '{name2}'}}) "
            f"RETURN r, type(r) AS relation_type, properties(r) AS relation_properties"
        )
        results = self.run_cypher(query).data()
        return self._format_relationship_results(results)

    @staticmethod
    def _format_relationship_results(results):
        formatted_results = {
            "nodes": [],
            "edges": []
        }
        node_ids = set()

        for result in results:
            relationship = result['r']
            relation_type = result['relation_type']
            relation_properties = result['relation_properties']

            start_node = relationship.start_node
            start_node_id = dict(start_node).get('id', str(start_node.identity))
            start_node_label = list(start_node.labels)[0]
            start_node_properties = dict(start_node)
            start_node_data = {
                "id": start_node_id,
                "label": start_node_label,
                **start_node_properties
            }

            if start_node_id not in node_ids:
                formatted_results["nodes"].append({"data": start_node_data})
                node_ids.add(start_node_id)

            end_node = relationship.end_node
            end_node_id = dict(end_node).get('id', str(end_node.identity))
            end_node_label = list(end_node.labels)[0]
            end_node_properties = dict(end_node)
            end_node_data = {
                "id": end_node_id,
                "label": end_node_label,
                **end_node_properties
            }

            if end_node_id not in node_ids:
                formatted_results["nodes"].append({"data": end_node_data})
                node_ids.add(end_node_id)

            edge_data = {
                "id": str(relationship.identity),
                "source": start_node_id,
                "target": end_node_id,
                "label": relation_type
            }
            edge_data.update(relation_properties)
            formatted_results["edges"].append({"data": edge_data})

        return formatted_results

    def create_kg_using_llm(self, user_input, prompt):
        zhipu = Zhipu()
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
            {"role": "user",
             "content": "你是一名人工智能专家，擅长创建知识图谱,你的任务是根据用户输入创建一个知识图谱。"},
            {"role": "user", "content": f"{user_input}"},
            {"role": "user",
             "content": f"可以参考给出的示例: + {json_example}, 其中id为随机生成的，人的label是人物，事件的label为事件。"
                        f"请输出一个JSON格式的知识图谱数据，用于cytoscape库的渲染。"
             }
        ])
        result = response.content

        if '```' in result:
            graph_data = json.loads(result.split('```', 2)[1].replace("json", ''))
        else:
            graph_data = json.loads(result)

        print(graph_data)
        return graph_data

    def import_json_from_file(self, file_path):
        """
        从 JSON 文件导入知识图谱数据到 Neo4j 数据库。

        :param file_path: JSON 文件的路径
        """
        try:
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                self.import_json_to_neo4j(json_data)
        except FileNotFoundError:
            logger.error(f"文件未找到: {file_path}")
        except json.JSONDecodeError:
            logger.error(f"文件内容不是有效的 JSON: {file_path}")
        except Exception as e:
            logger.error(f"导入 JSON 文件失败: {e}")

    def import_json_to_neo4j(self, json_data):
        """
        将 JSON 数据导入 Neo4j 数据库。
        :param json_data: JSON 格式的知识图谱数据
        """
        nodes = {}
        # 创建节点
        for node_data in json_data.get('nodes', []):
            node_id = node_data.get('id')
            label = node_data.get('label')
            if node_id and label:
                properties = {key: value for key, value in node_data.items() if key != 'id' and key != 'label'}
                node = Node(label, id=node_id, **properties)
                # self.__graph.create(node)
                nodes[node_id] = node

        # 创建关系
        for edge_data in json_data.get('edges', []):
            source_id = edge_data.get('source')
            target_id = edge_data.get('target')
            relation_type = edge_data.get('type')
            if source_id and target_id and relation_type:
                source_node = nodes.get(source_id)
                target_node = nodes.get(target_id)
                if source_node and target_node:
                    relationship = Relationship(source_node, relation_type, target_node)
                    relationship["id"] = edge_data.get('id', str(uuid.uuid4()))
                    for key, value in edge_data.items():
                        if key not in ['source', 'target', 'type', 'id']:
                            relationship[key] = value
                    try:
                        self.__graph.create(relationship)
                    except Exception as e:
                        logger.error(f"创建关系失败：{e}")

    def delete_nodes_without_relationships(self):
        """
        删除没有任何关系的节点。
        """
        try:
            # 查询所有节点
            query = "MATCH (n) RETURN n"
            nodes = self.run_cypher(query).data()

            for node in nodes:
                node_obj = node['n']
                # 查询节点是否有任何关系
                relationship_query = f"MATCH (n)-[r]-(m) WHERE id(n) = {node_obj.identity} RETURN r"
                relationships = self.run_cypher(relationship_query).data()

                # 如果没有关系则删除节点
                if not relationships:
                    self.__graph.delete(node_obj)
                    logger.info(f"删除没有关系的节点: {node_obj.identity}")

        except Exception as e:
            logger.error(f"删除没有关系的节点失败: {e}")

    def delete_relationships_and_nodes(self, node_label, node_props):
        """
        删除特定节点的所有关系，并删除与该节点具有关系的所有其他节点。
        :param node_label: 节点标签
        :param node_props: 节点属性
        """
        try:
            # 查找节点
            node = self.__node_matcher.match(node_label, **node_props).first()
            if not node:
                logger.error(f"未找到符合条件的节点：{node_label} {node_props}")
                return

            # 查找并删除所有节点发出的关系
            query_outgoing = (
                f"MATCH (n)-[r]->(m) WHERE id(n) = {node.identity} DELETE r"
            )
            self.run_cypher(query_outgoing)
            logger.info(f"成功删除节点 {node.identity} 的所有发出的关系")

            # 查找并删除所有节点接收的关系
            query_incoming = (
                f"MATCH (n)<-[r]-(m) WHERE id(n) = {node.identity} DELETE r"
            )
            self.run_cypher(query_incoming)
            logger.info(f"成功删除节点 {node.identity} 的所有接收的关系")

            # 查找并删除与指定节点有关系的其他节点
            query_related_nodes = (
                f"MATCH (n)-[r]-(m) WHERE id(n) = {node.identity} DELETE m"
            )
            self.run_cypher(query_related_nodes)
            logger.info(f"成功删除与节点 {node.identity} 有关系的所有其他节点")

            # 删除指定节点本身
            self.__graph.delete(node)
            logger.info(f"成功删除节点 {node.identity}")

        except Exception as e:
            logger.error(f"删除节点及其相关节点失败: {e}")

    def delete_all_nodes_with_label(self, label):
        """
        删除所有具有指定标签的节点及其所有关系。
        :param label: 节点标签
        """
        try:
            # 查找并删除所有具有指定标签的节点的所有发出的关系
            query_outgoing = (
                f"MATCH (n:{label})-[r]->(m) DELETE r"
            )
            self.run_cypher(query_outgoing)
            logger.info(f"成功删除所有标签为 {label} 的节点的所有发出的关系")

            # 查找并删除所有具有指定标签的节点的所有接收的关系
            query_incoming = (
                f"MATCH (n:{label})<-[r]-(m) DELETE r"
            )
            self.run_cypher(query_incoming)
            logger.info(f"成功删除所有标签为 {label} 的节点的所有接收的关系")

            # 删除所有具有指定标签的节点
            query_delete_nodes = (
                f"MATCH (n:{label}) DELETE n"
            )
            self.run_cypher(query_delete_nodes)
            logger.info(f"成功删除所有标签为 {label} 的节点")

        except Exception as e:
            logger.error(f"删除标签为 {label} 的节点及其所有关系失败: {e}")


if __name__ == '__main__':
    graph = KnowledgeGraphService()
    # print(graph.query_node_all_relations_by_name("张三"))
    # graph.delete_relationship("人物", {"name": "张三"},
    #                           "事件",{"name": "概率与统计岗前培训"},
    #                           "参加1")
    # graph.delete_nodes_without_relationships()
    # graph.delete_relationships_and_nodes("课程", {"name": "课程5"})
    # graph.delete_all_nodes_with_label("子章节")
    # graph.import_json_from_file("/home/huison/ai/knowledge-graph/learning_path.json")
    # graph.create_relationship("知识点", {"name": "函数"},
    #                           "知识点", {"name": "函数的概念"},
    #                           "子级")
    # graph.create_node("知识点", {"name": "函数的概念", "id": "k2-1"})
    # graph.create_relationship("子章节", {"id": "a10"},
    #                           "知识点", {"id": "k5"},
    #                           "引用")
    # print(edges)
    # graph.create_relationship()
    print(graph.query_nodes(2))

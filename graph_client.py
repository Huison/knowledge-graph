from datetime import datetime
from typing import Sequence, Set

from loguru import logger
from py2neo import Graph, Node, ConnectionUnavailable, NodeMatcher, Relationship, RelationshipMatcher


# 编写一个GraphDao类，该类包含与图相关的数据库操作方法。
class GraphDao(object):
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
        """
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

    def delete_relationship(self, relationship):
        ...

    def update_node(self, node, properties):
        ...

    def update_relationship(self, relationship, properties):
        ...

    def query_node(self, *label, **properties):
        return self.__node_matcher.match(*label, **properties)

    def query_relationship(self, nodes: Sequence | Set | None = None, r_type=None, **properties):
        return self.__relationship_matcher.match(nodes, r_type, **properties)

    def query_relationship_by_2person_name(self, first_person, second_person):
        rel = self.__graph.run(
            f"match(:`人物`{{name:'{first_person}'}})-[r]-(:`人物`{{name:'{second_person}'}}) return r, type(r)").data()
        return rel

    def query_path(self, start_node, end_node, rel_type, rel_properties):
        ...

    def query_all(self):
        ...

    def run_cypher(self, query):
        result = self.__graph.run(query)
        return result

    def create_relationship(self, node1_label, node1_props, node2_label, node2_props, relation_type,
                            relation_props=None):
        node1 = self.__node_matcher.match(node1_label, **node1_props).first()
        node2 = self.__node_matcher.match(node2_label, **node2_props).first()

        if node1 and node2:
            relationship = Relationship(node1, relation_type, node2)
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


if __name__ == '__main__':
    graph = GraphDao()
    # 要查询的节点的 ID
    # node_id = 19  # 替换为实际节点的 ID
    #
    # # 编写 Cypher 查询语句
    # query = f"MATCH (n)-[r]-(m) WHERE ID(n) = {node_id} RETURN n, r, m"
    #
    # # 执行查询并处理结果
    # results = graph.run_cypher(query)
    # for record in results:
    #     print(record)

    node_name = "张三"  # 替换为实际节点的 name 属性值
    # 编写 Cypher 查询语句
    query = f"MATCH (n {{name: '{node_name}'}})-[r]-(m) RETURN n, r, m"
    # 执行查询并处理结果
    results = graph.run_cypher(query)
    print(results.data()[0])
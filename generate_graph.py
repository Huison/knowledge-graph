from datetime import datetime
from typing import Sequence, Set

from loguru import logger
from py2neo import Graph, Node, ConnectionUnavailable, NodeMatcher, Relationship
import uuid

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


if __name__ == '__main__':
    """
    2019年9月28日张三在香山参加微积分岗前培训，被任命为微积分助理工程师，同时被授予了中尉军衔。
    2020年6月21日张三在大兴参加线性代数岗前培训，被任命为线性代数助理工程师。
    2021年10月9日张三在大兴参加概率与统计岗前培训，被任命为概率与统计助理工程师。
    2022年8月17日张三在大兴参加离散数学岗前培训，被任命为离散数学工程师。
    2023年12月3日张三在大兴参加微分方程考试，被任命为微分方程工程师，同时也被任命为副科长。
    计划2024年12月1日张三在大兴参加实分析和复分析的理论学习。
    """
    graph = GraphDao()
    # graph.create_node("人物", {"name": "张三"})
    # graph.create_node("事件", {"name": "微积分岗前培训"})
    # graph.create_node("事件", {"name": "线性代数岗前培训"})
    # graph.create_node("事件", {"name": "概率与统计岗前培训"})
    # graph.create_node("事件", {"name": "离散数学岗前培训"})
    # graph.create_node("事件", {"name": "微分方程考试"})
    # graph.create_node("事件", {"name": "实分析和复分析的理论学习"})
    # graph.create_node("职务", {"name": "微积分助理工程师"})
    # graph.create_node("职务", {"name": "线性代数助理工程师"})
    # graph.create_node("职务", {"name": "概率与统计助理工程师"})
    # graph.create_node("职务", {"name": "离散数学工程师"})
    # graph.create_node("职务", {"name": "微分方程工程师"})
    # graph.create_node("职务", {"name": "副科长"})
    # graph.create_node("军衔", {"name": "中尉"})

    """
    2019年9月28日张三在香山参加微积分岗前培训，被任命为微积分助理工程师，同时被授予了中尉军衔。
    2020年6月21日张三在大兴参加线性代数岗前培训，被任命为线性代数助理工程师。
    2021年10月9日张三在大兴参加概率与统计岗前培训，被任命为概率与统计助理工程师。
    2022年8月17日张三在大兴参加离散数学岗前培训，被任命为离散数学工程师。
    2023年12月3日张三在大兴参加微分方程考试，被任命为微分方程工程师，同时也被任命为副科长。
    计划2024年12月1日张三在大兴参加实分析和复分析的理论学习。
    """
    # graph.create_relationship('人物', {'name': '张三'},
    #                                     '事件', {'name': '微积分岗前培训'},
    #                                     '参加', {'时间': '2019年9月28日', '地点': '香山'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '职务', {'name': '微积分助理工程师'},
    #                           '被任命', {'时间': '2019年9月28日', '地点': '香山'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '军衔', {'name': '中尉'},
    #                           '被授予', {'时间': '2019年9月28日', '地点': '香山'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '事件', {'name': '线性代数岗前培训'},
    #                           '参加', {'时间': '2020年6月21日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '职务', {'name': '线性代数助理工程师'},
    #                           '被任命', {'时间': '2020年6月21日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '事件', {'name': '概率与统计岗前培训'},
    #                           '参加', {'时间': '2021年10月9日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '职务', {'name': '概率与统计助理工程师'},
    #                           '被任命', {'时间': '2021年10月9日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '事件', {'name': '离散数学岗前培训'},
    #                           '参加', {'时间': '2022年8月17日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '职务', {'name': '离散数学工程师'},
    #                           '被任命', {'时间': '2022年8月17日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '事件', {'name': '微分方程考试'},
    #                           '参加', {'时间': '2023年12月3日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '职务', {'name': '微分方程工程师'},
    #                           '被任命', {'时间': '2023年12月3日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '职务', {'name': '副科长'},
    #                           '被任命', {'时间': '2023年12月3日', '地点': '大兴'})
    # graph.create_relationship('人物', {'name': '张三'},
    #                           '事件', {'name': '实分析和复分析的理论学习'},
    #                           '计划参加', {'时间': '2024年12月1日', '地点': '大兴'})

    # graph.create_relationship('事件', {'name': '实分析和复分析的理论学习'},
    #                       '人物', {'name': '张三'},
    #                       'test_type', {'时间': 'test_time', '地点': 'test_location'})

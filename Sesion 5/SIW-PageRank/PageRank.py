import argparse
import math

import networkx as nx
import matplotlib.pyplot as plt


class PageRank:
    """
        PageRank para la asignatura de Sistemas de Información para la Web
    """

    def __init__(self, g: bool):
        self.g = g
        self.graph = nx.DiGraph()
        self.social_network = {}

    def load_data(self, social_network_file: str):
        """
            Carga los datos del archivo en un diccionario de diccionarios, de la forma:
                {
                    AC: {AG: 3, HT: 2},
                    AG: {AC: 3},
                    HT: {AC: 3, PA: 5}
                    PA: {HT: 5}
                }
            :param social_network_file:
            :return:
        """
        with open(social_network_file, 'r') as file:
            for line in file:
                # Separación de la línea en el identificador del nodo y sus relaciones
                node_data = line.strip().split(',', 1)
                node_id, node_relations = node_data[0], node_data[1].split(',')
                self._add_nodes(node_id, node_relations)
        self._create_graph()

    def run(self, ego_character: str, character_1: str, character_2: str):
        """
            Ejecuta el page rank y las diferentes partes del script
            :param ego_character:
            :param character_1:
            :param character_2:
            :return:
        """
        # Creación el page rank global y muestra de los 5 personajes más importantes
        graph_pagerank = self.create_page_rank(self.graph)
        self.print_pagerank(graph_pagerank)

        # Creación del grafo egocéntrico del personaje pasado por parámetro
        ego_graph = self._create_ego_graph(ego_character)
        ego_graph_pagerank = self.create_page_rank(ego_graph)
        self.print_pagerank(ego_graph_pagerank)

        print("\t-------------------------------------------------")
        print("\tCOMPARACIÓN DE PERSONAJES:")
        cosine = self._compare_characters(character_1, character_2)
        print(f"\t La similitud entre {character_1} y {character_2} (valor del coseno) es {cosine}")

        # Desactivación del dibujo de grafos para evitar sobrecargas
        self.g = False
        print("\t-------------------------------------------------")
        print("\tCLUSTERS DE PERSONAJES:")
        self._find_character_clusters(graph_pagerank[:50])

    def _add_nodes(self, node_id, node_relations):
        """
            Carga los nodos y sus relaciones en el diccionario de diccionarios
            :param node_id:
            :param node_relations:
            :return:
        """
        if node_id not in self.social_network.keys():
            self.social_network[node_id] = {}
        for relation in node_relations:
            if relation not in self.social_network.keys():
                self.social_network[relation] = {}
            # Creación de las relaciones bidireccionales
            self._create_relationships(node_id, relation)
            self._create_relationships(relation, node_id)

    def _create_relationships(self, node1, node2):
        """
            Crea las relaciones entre los nodos o aumenta el peso de ellas
            :param node1:
            :param node2:
            :return:
        """
        self.social_network[node1][node2] = self.social_network[node1].get(node2, 0) + 1

    def _create_graph(self):
        """
            Crea el grafo de la red social
            :return:
        """
        for node_id, node_relations in self.social_network.items():
            self.graph.add_node(node_id)
            for node_relation, relation_weight in node_relations.items():
                self.graph.add_node(node_relation)
                self.graph.add_edge(node_id, node_relation, weight=relation_weight)
        # En caso de que se quiera mostrar el grafo
        if self.g:
            self.draw_graph(self.graph, "Grafo general")

    def _create_ego_graph(self, character):
        """
            Crea el grafo egocéntrico de un personaje
            :param character:
            :return:
        """
        ego_graph = nx.ego_graph(self.graph, character, radius=1, center=True, undirected=False, distance=None)
        # En caso de que se quiera mostrar el grafo
        if self.g:
            self.draw_graph(ego_graph, f"Grafo egocéntrico de {character}")
        return ego_graph

    def _compare_characters(self, character_1: str, character_2: str) -> float:
        """
            Calcula la similitud entre dos personajes
            :param character_1:
            :param character_2:
            :return:
        """
        # Obtención de los nodos relacionados con el personaje 1
        character1_graph = self._create_ego_graph(character_1)
        character1_pagerank = self.create_page_rank(character1_graph)
        if self.g:
            self.print_pagerank(character1_pagerank)

        # Obtención de los nodos relacionados con el personaje 2
        character2_graph = self._create_ego_graph(character_2)
        character2_pagerank = self.create_page_rank(character2_graph)
        if self.g:
            self.print_pagerank(character2_pagerank)

        # Conversión de la lista de tuplas en sets con los nodos
        character1_set = {key for key, _ in character1_pagerank}
        character2_set = {key for key, _ in character2_pagerank}
        # Cálculo del valor del coseno (similitud)
        cosine = self.calculate_cosine(character1_set, character2_set)
        return cosine

    def _find_character_clusters(self, pagerank_results):
        """
            Búsqueda de los clusters de personajes
            :param pagerank_results:
            :return:
        """
        # Conversión de la lista de tuplas en un set con los nodos
        pagerank_set = {key for key, _ in pagerank_results}
        clusters = {}
        # Comparación de cada nodo con el resto
        for pr_1 in pagerank_set:
            cluster = {}
            for pr_2 in pagerank_set:
                if pr_1 != pr_2:
                    cosine = self._compare_characters(pr_1, pr_2)
                    # En caso de superar el umbral, forma parte del cluster
                    if cosine >= 0.4:
                        cluster[pr_2] = cosine
            clusters[pr_1] = cluster
        self.print_clusters(clusters)

    @staticmethod
    def create_page_rank(graph):
        """
            Crea el pagerank
            :param graph:
            :return:
        """
        pagerank_dict = nx.pagerank(graph, alpha=0.85, personalization=None,
                                    max_iter=100, tol=1e-06, nstart=None,
                                    weight='weight', dangling=None)
        # Ordena los resultados de mayor a menor
        sorted_pagerank = sorted(pagerank_dict.items(), key=lambda x: x[1], reverse=True)
        return sorted_pagerank

    @staticmethod
    def calculate_cosine(s1: set, s2: set):
        """
            Cálcula el coseno de dos conjuntos:
                | X ∩ Y| / √(|X| * |Y|)
            :param s1:
            :param s2:
            :return:
        """
        intersection = s1.intersection(s2)
        return len(intersection) / math.sqrt(len(s1) * len(s2))

    @staticmethod
    def print_pagerank(pagerank_results):
        """
            Muestra los personajes más importantes
            :param pagerank_results:
            :return:
        """
        print("\t\t * Personajes más importantes:")
        for index, (key, value) in enumerate(pagerank_results[:7]):
            print(f"\t\t\t {index + 1}. {key}: {value}")

    @staticmethod
    def print_clusters(clusters):
        """
            Muestra los clusters
            :param clusters:
            :return:
        """
        for key, value in clusters.items():
            print(f"\t\t- {key}: {value}")

    @staticmethod
    def draw_graph(graph, graph_title):
        """
            Dibuja un grafo
            :param graph:
            :param graph_title:
            :return:
        """
        print(f"\t -> {graph_title}: {graph}")
        print(f"\t\t Drawing...")
        # Opciones de configuración del grafo
        options = {
            'node_color': 'skyblue',
            'node_size': 50,
            'width': 1,
            'edge_color': 'gray',
            'font_color': 'black',
            'font_size': 10,
        }
        plt.title(graph_title)
        nx.draw_networkx(graph, arrows=True, **options)
        plt.show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='SimHashOmar', description='PageRank para la asignatura de Sistemas de '
                                                                     'Información para la Web [SIW]')
    parser.add_argument('social_network_file', type=str,
                        help='path of the file that contains the social network with its relationships')
    parser.add_argument('-ego_character', type=str, default='AG', help="character to create ego graph")
    parser.add_argument('-character_1', type=str, default='PA', help='first character to compare')
    parser.add_argument('-character_2', type=str, default='HT', help='second character to compare')
    parser.add_argument('-g', action='store_true', default=True, help='draw graphs')
    args = parser.parse_args()

    print("SISTEMAS DE INFORMACIÓN PARA LA WEB\n- PAGE RANK")
    pagerank = PageRank(args.g)
    pagerank.load_data(args.social_network_file)
    pagerank.run(args.ego_character, args.character_1, args.character_2)

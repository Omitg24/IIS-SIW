from Crawler import Crawler
from .Search import Search


class BreadthFirst(Search):

    def __init__(self, crawler: Crawler):
        self.crawler: Crawler = crawler

    def crawl(self, links: list[str]):
        """
            Realiza el crawling mediante recorrido en anchura
            :param links:
            :return:
        """
        print("\tRecorrido en anchura")
        self._crawl(links.pop(0), links)
        print(" - FIN DEL CRAWLING")

    def _crawl(self, link, queue):
        # En caso de haber agotado el número de descargas permitidas finaliza el crawling
        if self.crawler.max_downloads == 0:
            return
        print("\t-->", self.crawler.max_downloads, "---------------")
        self.crawler.max_downloads -= 1
        print("\t\tLink actual: ", link)
        if Crawler.check_robots_file(link):
            # Se añade el link a la lista de links visitados
            self.crawler.visited_links.add(link)
            # Obtención de los links de la página
            link_list = self.crawler.download_website(link)
            if link_list is not None:
                for link_item in link_list:
                    # Se añaden los links a la cola para recorrerlos en anchura
                    queue.append(link_item)
        self._crawl(queue.pop(0), queue)

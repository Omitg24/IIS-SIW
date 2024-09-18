import argparse
import time
import urllib
import requests
import validators
from urllib import robotparser, parse
from bs4 import BeautifulSoup
from warcio import WARCWriter, StatusAndHeaders
from io import BytesIO

from search import *


class Crawler:
    """
        Crawler para la asignatura de Sistemas de Información para la Web
    """

    def __init__(self, max_downloads: int, seconds: int):
        self.max_downloads = max_downloads
        self.seconds = seconds
        self.links: list[str] = []
        # Set para evitar repeticiones de los links
        self.visited_links = set()

    def gather_links(self, filename: str):
        """
            Carga los links de un archivo en la lista de links de la clase
            :param filename:
            :return:
        """
        # Se abre el archivo y se cargan los links
        print("\tLinks a explorar: ")
        with open(filename, 'r') as f:
            for line in f:
                link = line.strip()
                self.links.append(link)
                print("\t ->", link)

    def run(self, search: Search):
        """
            Ejecuta el crawler, recorriendo en profundidad o en anchura en función del parámetro
            :return:
        """
        print("\tNúmero de descargas permitidas: ", self.max_downloads)
        print("\tTiempo de espera entre peticiones: ", self.seconds, "sec")

        # Iteración a través de los links, lanzando el crawling en profundidad o en anchura
        search.crawl(self.links)

    def download_website(self, link: str):
        """
            Descarga la web
            :param link:
            :return:
        """
        # Descarga de la web en un archivo WARC
        with open('files/warc/file.warc.gz', 'ab') as output:
            writer = WARCWriter(output, gzip=True)
            response = requests.get(link)
            headers_list = response.raw.headers.items()
            http_headers = StatusAndHeaders('200 OK', headers_list, protocol='HTTP/1.0')
            record = writer.create_warc_record(link, 'response', payload=BytesIO(response.content),
                                               http_headers=http_headers)
            writer.write_record(record)
        # Tiempo de espera entre peticiones
        time.sleep(self.seconds)
        # Comprobación de que el tipo de contenido sea html y que la petición haya tenido éxito
        if response.headers.get('content-type').__contains__("text/html") and response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            for a in soup.find_all('a'):
                if a.get('href') is not None:
                    link_item = Crawler.normalize_link(link, a.get('href'))
                    parsed_link_item = urllib.parse.urlparse(link_item)
                    if (link_item not in self.visited_links and parsed_link_item.path != '/'
                            and validators.url(link_item)):
                        links.append(link_item)
            return links
        return None

    @staticmethod
    def check_robots_file(link: str):
        """
            Comprueba el fichero robots.txt de la página y si se puede acceder a este
            :param link:
            :return:
        """
        parsed_link = urllib.parse.urlparse(link)
        robots_link = parsed_link.scheme + '://' + parsed_link.netloc + "/robots.txt"
        try:
            rp = robotparser.RobotFileParser()
            # Lectura del fichero robots.txt
            rp.set_url(robots_link)
            rp.read()
            # Comprobación de acceso al enlace
            return rp.can_fetch('*', link)
        except Exception as e:
            print("ERROR: Se ha producido una excepción al verificar el archivo robots.txt: ", e)
            return False

    @staticmethod
    def normalize_link(url: str, link: str):
        """
            Normaliza los links
            :param url:
            :param link:
            :return:
        """
        return urllib.parse.urljoin(url, link) if link.startswith('/') or link.startswith('#') else link


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='CrawlerOmar', description='Crawler para la asignatura de Sistemas de '
                                                                     'Información para la Web [SIW]')
    parser.add_argument('file', type=str,
                        help='path of the file that contains the links to be processed by the crawler')
    parser.add_argument('-downloads', type=int, default=10, help='Maximum number of allowed downloads for '
                                                                 'the crawler, by default is 10 seconds')
    parser.add_argument('-seconds', type=int, default=2, help='Number of seconds to wait after a request, '
                                                              'by default is 2 seconds')
    parser.add_argument('-search', action='store_true', default=False, help='Type of search to '
                                                                            ' perform on the web, by default'
                                                                            ' is depth first search')

    args = parser.parse_args()

    print("SISTEMAS DE INFORMACIÓN PARA LA WEB\n- CRAWLER BÁSICO")
    crawler = Crawler(args.downloads, args.seconds)
    crawler.gather_links(args.file)
    # Ejecución del crawling con el algoritmo de búsqueda introducido
    if args.search:
        crawler.run(BreadthFirst(crawler))
    else:
        crawler.run(DepthFirst(crawler))

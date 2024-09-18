import argparse

from simhash import Simhash, SimhashIndex
from textblob import TextBlob
import nltk.tokenize as tokenizers


class SimHash:
    """
        SimHash para la asignatura de Sistemas de Información para la Web
    """

    def __init__(self, tokenizer_name: str, k: int, f: int):
        self.tokenizer = getattr(tokenizers, tokenizer_name)()
        self.k_value = k
        self.f_value = f
        # Diccionario de documentos
        self.documents = {}
        # Listado de queries
        self.queries = []

    def run(self):
        """
            Ejecuta la detección de cuasi-duplicados y la búsqueda de las queries
            :return:
        """
        signatures = self._generate_signatures()
        index = self._generate_index(signatures)
        self._detect_duplicates(index)
        self._vectorize_documents()
        self.search()

    def load_documents(self, documents_filename: str):
        """
            Carga de los documentos y los tokeniza con el tokenizador elegido por el usuario
            :param documents_filename:
            :return:
        """
        with open(documents_filename, 'r') as f:
            docs = f.readlines()
        f.close()
        for doc in docs:
            key, value = doc.strip().split(' ', 1)
            # self.documents[key] = value | Realización previa a la implementación del tokenizador
            blob = TextBlob(value)
            # Tokenización de los documentos con el tokenizador elegido
            document = blob.tokenize(self.tokenizer)
            self.documents[key] = document
        # Se ordenan los documentos
        self.documents = dict(sorted(self.documents.items()))

    def load_queries(self, queries_filename: str):
        """
            Carga de las queries y las vectoriza con el tokenizador elegido por el usuario
            :param queries_filename:
            :return:
        """
        with open(queries_filename, 'r') as f:
            queries = f.readlines()
        f.close()
        index = 1
        print('\tQueries:')
        for query in queries:
            q = query.replace('\n', '')
            print(f'\t * {index}. {q}')
            index += 1

            blob = TextBlob(q)
            # Tokenización de las queries
            q = blob.tokenize(self.tokenizer)
            # Vectorización de las queries
            vectorized_queries = set(word.lower() for word in q)
            self.queries.append(vectorized_queries)
        # Al final la lista de queries será una lista de listas con las palabras que forman esas queries, es decir:
        # [[bangladesh, anti-government, strike], [baseball, players, legal, victory], ...]

    def search(self):
        """
            Realiza la búsqueda de las queries en los documentos vectorizados
            :return:
        """
        # Diccionario formado por {valor_query, listado_documentos}
        results = {}
        for query in self.queries:
            # Diccionario formado por: {clave_documento, valor_solapamiento}
            query_results = {}
            for key, value in self.documents.items():
                # Cálculo de la similitud entre las queries y los documentos
                overlap = self.calculate_overlap(query, value)
                query_results[key] = overlap
            # Ordenación del diccionario basándose en el coeficiente de solapamiento
            sorted_query_results = dict(sorted(query_results.items(), key=lambda x: x[1], reverse=True))
            # Obtención de los 10 primeros
            top_10_documents = list(sorted_query_results.keys())[:10]
            results[' '.join(query)] = top_10_documents
        self.print_collection('Query results:', results)

    def _generate_signatures(self):
        """
            Genera las firmas de los documentos para realizar la detección de cuasi-duplicados
            :return:
        """
        signatures = []
        for key, value in self.documents.items():
            # Generación de las firmas
            signature = Simhash(value, f=self.f_value)
            signatures.append((key, signature))
        return signatures

    def _generate_index(self, signatures: list):
        """
            Genera el índice con las firmas previamente creadas para realizar la detección de cuasi-duplicados
            :param signatures:
            :return:
        """
        return SimhashIndex(signatures, k=self.k_value, f=self.f_value)

    def _detect_duplicates(self, index: SimhashIndex):
        """
            Detecta los cuasi-duplicados en el índice y los elimina
            :param index:
            :return:
        """
        # Contiene las claves de los documentos que han de ser eliminados debido a la detección de cuasi-duplicados
        keys_to_remove = set()
        duplicates = {}
        for key, duplicate_key in self.documents.items():
            signature = Simhash(duplicate_key, f=self.f_value)
            # Detección de los duplicados
            signature_duplicates = [dup for dup in index.get_near_dups(signature) if dup != key]
            # Filtrado de los duplicados
            if signature_duplicates and not any(dup in duplicates for dup in signature_duplicates):
                duplicates[key] = signature_duplicates
                keys_to_remove.update(signature_duplicates)
        for key in keys_to_remove:
            # Eliminación de los duplicados
            self.documents.pop(key)
        self.print_collection('Duplicated documents:', duplicates)

    def _vectorize_documents(self):
        """
            Vectoriza los documentos
            :return:
        """
        for key, value in self.documents.items():
            # Vectorización de los documentos (de forma que queden igual que las queries)
            vectorized_documents = {word.lower() for word in value}
            self.documents[key] = vectorized_documents

    @staticmethod
    def calculate_overlap(s1: set, s2: set):
        """
            Cálcula el coeficiente de solapamiento, se ha realizado este como resultado de:
                32892095 mod 4 = 3
                    ⇒ Coeficiente de solapamiento:
                        | X ∩ Y| / min(|X|, |Y|)
            :param s1:
            :param s2:
            :return:
        """
        intersection = s1.intersection(s2)
        min_length = min(len(s1), len(s2))
        return len(intersection) / min_length

    @staticmethod
    def print_collection(collection_name: str, collection: dict):
        """
            Imprime el contenido de las colecciones pasadas por parámetro
            :param collection_name: 
            :param collection: 
            :return: 
        """
        print(f'\t{collection_name}')
        index = 1
        for key, value in collection.items():
            formatted_keys = ', '.join([f'{i}' for i in value])
            print(f'\t -> {index}. {key} | {formatted_keys}')
            index += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='SimHashOmar', description='SimHash para la asignatura de Sistemas de '
                                                                     'Información para la Web [SIW]')
    parser.add_argument('documents_file', type=str,
                        help='path of the file that contains documents to be analyzed')
    parser.add_argument('queries_file', type=str, help='path of the file that contains queries to be analyzed')
    parser.add_argument('-k', type=int, default=3, help='length of the shingles that are going to be '
                                                        'generated')
    parser.add_argument('-f', type=int, default=64, help='dimensions of fingerprints, in bits')
    # Posibilidad de cargar un tokenizador distinto, eligiéndolo como parámetro
    parser.add_argument('-tokenizer_name', type=str, default='WhitespaceTokenizer', help='name of the '
                                                                                         'tokenizer that will be used')

    args = parser.parse_args()

    print("SISTEMAS DE INFORMACIÓN PARA LA WEB\n- SIM HASH")
    simHash = SimHash(args.tokenizer_name, args.k, args.f)
    simHash.load_documents(args.documents_file)
    simHash.load_queries(args.queries_file)
    simHash.run()

import glob
import math
import os
import random
import re
from collections import Counter
from tqdm import tqdm

from retriv import SearchEngine

retriv_base_path = "files/.retriv"

cisi_queries_path = "files/cisi/cisi.que"
cisi_documents_path = "files/cisi/cisi.jsonl"
cisi_relevance_path = "files/cisi/cisi.rel"

def menu_principal():
    while True:
        print("Menú principal:")
        print("1. pizzas")
        print("2. 10000.train")
        print("3. 20newsgroups")
        print("4. cisi")
        print("X. SALIR")

        seleccion = input("Elige una opción: ")

        if seleccion == "1":
            pizzas()
        elif seleccion == "2":
            articles_10000()
        elif seleccion == "3":
            twenty_news_groups()
        elif seleccion == "4":
            cisi()
        elif seleccion == "x" or seleccion == "X":
            exit()
        else:
            print(seleccion, "no es una opción válida.")

def pizzas():
    os.environ["retriv_base_path"] = retriv_base_path

    try:
        se = SearchEngine.load("pizzas")
        print("Ya existe el índice \"pizzas\" así que lo cargamos.")
    except:
        print("No existe el índice \"pizzas\" así que lo creamos...")
        pizzas = [
            {"id": "caprichosa", "text": "alcachofas mozzarella champiñones aceite aceitunas tomate"},
            {"id": "marinera", "text": " ajo aceite orégano tomate"},
            {"id": "cuatro quesos", "text": "fontina gorgonzola mozzarella tomate stracchino"},
            {"id": "romana", "text": "anchoas mozzarella aceite orégano tomate"},
            {"id": "vienesa", "text": " mozzarella aceite orégano salchicha tomate"}
        ]

        se = SearchEngine(
            index_name="pizzas",
            model="tf-idf",
            stemmer="spanish",
            tokenizer="whitespace",
            do_lowercasing=True
        )

        se.index(
            collection=pizzas,
            show_progress=True
        )

        se.save()  # No es estrictamente necesario invocar save(), retriv siempre va a persistir el índice a disco

    menu_pizzas(se=se)

def menu_pizzas(se):
    while True:
        print("Menú pizzas")
        print("1. tomate")
        print("2. orégano")
        print("3. tomate orégano")
        print("4. tomate orégano ajo")
        print("5. tomate orégano aceitunas")
        print("6. TU PROPIA CONSULTA")
        print("X. VOLVER")

        seleccion = input("Elige una opción: ")

        consulta = None
        if seleccion == "1":
            consulta = "tomate"
        elif seleccion == "2":
            consulta = "orégano"
        elif seleccion == "3":
            consulta = " tomate orégano"
        elif seleccion == "4":
            consulta = "tomate orégano ajo"
        elif seleccion == "5":
            consulta = "tomate orégano aceitunas"
        elif seleccion == "6":
            consulta = input("Escribe tu propia consulta: ")
        elif seleccion == "x" or seleccion == "X":
            return
        else:
            print(seleccion, "no es una opción válida.")

        if consulta is not None:
            results = se.search(consulta)
            print(consulta)
            for result in results:
                print(result)
            print("----")
            query_biased_summaries(consulta, results)

def articles_10000():
    os.environ["retriv_base_path"] = retriv_base_path

    try:
        se = SearchEngine.load("articles_10000")
        print("Ya existe el índice \"articles_10000\" así que lo cargamos.")
    except:
        print("No existe el índice \"articles_10000\" así que lo creamos...")
        se = SearchEngine(
            index_name="articles_10000",
            model="bm25",
            stemmer="english",
            tokenizer="word",
            do_lowercasing=True,
            do_punctuation_removal=True
        )

        se.index_file(
            path="articles_10000.jsonl",
            show_progress=True
        )

        se.save()  # No es estrictamente necesario invocar save(), retriv siempre va a persistir el índice a disco

    menu_articles(se=se)

def menu_articles(se):
    consultas = [
        "bangladesh anti-government strike",
        "baseball players legal victory",
        "british prime minister john major",
        "diego maradona coaching job",
        "dow jones index historic high",
        "heavy snowfall stockholm",
        "hillary clinton south asia tour",
        "kuwait oil company crisis",
        "mafia killings sicily",
        "michael johnson world record",
        "michael schumacher formula one crash",
        "passenger bus collision",
        "pat buchanan running for president",
        "peseta all-time low",
        "russia ukraine agreements",
        "silvio berlusconi political career",
        "st. patrick's day celebration",
        "trial nice mayor jacques medecin",
        "turkey withdrawing forces northern iraq",
        "u.s. no plans aid china three gorges dam"
    ]

    consulta_previa = None

    while True:
        print("Menú articles_10000")
        print("1. Consulta predefinida al azar")
        print("2. TU PROPIA CONSULTA")
        print("3. More like this")
        print("X. VOLVER")

        seleccion = input("Elige una opción: ")

        consulta = None
        if seleccion == "1":
            random.shuffle(consultas)
            consulta = consultas[0]
        elif seleccion == "2":
            consulta = input("Escribe tu propia consulta: ")
        elif seleccion == "3":
            if consulta_previa is not None:
                more_like_this(se, consulta_previa)
            else:
                print("Para buscar documentos similares necesitamos realizar primero una consulta...")
        elif seleccion == "x" or seleccion == "X":
            return
        else:
            print(seleccion, "no es una opción válida.")

        if consulta is not None:
            consulta_previa = consulta
            results = se.search(consulta, cutoff=5)
            print("\nConsulta: " + consulta + "\n\nResultados:")
            for result in results:
                result["text"] = result["text"][:80] + "..."
                print(result)
            print("----")
            # print(
            #     "¡Atención! Necesitaríamos snippets generados en base a la consulta, aka, \'query-biased "
            #     "summaries\'...\n")
            query_biased_summaries(consulta, results)

def twenty_news_groups():
    os.environ["retriv_base_path"] = retriv_base_path

    try:
        se = SearchEngine.load("20newsgroups")
        print("Ya existe el índice \"20newsgroups\" así que lo cargamos.")
    except:
        print("No existe el índice \"20newsgroups\" así que lo creamos...")
        se = SearchEngine(
            index_name="20newsgroups",
            model="bm25",
            stemmer="english",
            tokenizer="word",
            do_lowercasing=True,
            do_punctuation_removal=True
        )

        folder_path = ".retriv/20news-18828.zip"

        collection = list()

        for archivo in glob.glob(os.path.join(folder_path, '**', '*'), recursive=True):
            if not os.path.isdir(archivo):
                print(archivo)
                with open(archivo, "r") as f:
                    text = f.read()
                    text = " ".join(text.splitlines())
                    text = re.sub(r'\s+', ' ', text)

                    collection.append({
                        "id": archivo,
                        "text": text
                    })

        se.index(collection=collection, show_progress=True)

    menu_20newsgroups(se=se)

def menu_20newsgroups(se):
    consultas = ["audi s4", "battery charger", "david koresh", "dennis martinez", "dodge wagon", "dos 5.0", "dos 6.0",
                 "encryption algorithm", "fortran library", "frequent nosebleeds", "game boy", "genesis",
                 "graphics library", "hard disk", "headphones", "honda cbr600", "honda crx", "honda cx650", "ibm",
                 "islam", "jehovah's witnesses", "jesus", "joystick", "jpeg specification", "mac modem", "macintosh",
                 "mark whiten", "megadrive", "metallica", "ms excel", "nikon", "noisy engine", "playoff results",
                 "powerbook", "rock and roll", "saab", "scsi cable", "sega", "siggraph", "space shuttle", "stanley cup",
                 "toyota land cruiser", "toyota wagons", "vw passat", "windows 3.1", "windows nt"]

    consulta_previa = None

    while True:
        print("Menú 20newsgroups")
        print("1. Consulta predefinida al azar")
        print("2. TU PROPIA CONSULTA")
        print("3. More like this")
        print("4. Expansión de consultas con pseudo-relevance feedback")
        print("X. VOLVER")

        seleccion = input("Elige una opción: ")

        consulta = None
        if seleccion == "1":
            random.shuffle(consultas)
            consulta = consultas[0]
        elif seleccion == "2":
            consulta = input("Escribe tu propia consulta: ")
        elif seleccion == "3":
            if consulta_previa is not None:
                more_like_this(se, consulta_previa)
            else:
                print("Para buscar documentos similares necesitamos realizar primero una consulta...")
        elif seleccion == "4":
            if consulta_previa is not None:
                expansion_consultas(se, consulta_previa)
            else:
                print("Necesitamos primero una consulta para expandirla...")
        elif seleccion == "x" or seleccion == "X":
            return
        else:
            print(seleccion, "no es una opción válida.")

        if consulta is not None:
            consulta_previa = consulta
            results = se.search(consulta, cutoff=5)
            print("\nConsulta: " + consulta + "\n\nResultados:")
            for result in results:
                result["text"] = result["text"][:160] + "..."
                print(result)
            print("----")
            # print(
            #     "¡Atención! Necesitaríamos snippets generados en base a la consulta, aka, \'query-biased "
            #     "summaries\'...\n")
            query_biased_summaries(consulta, results)

def cisi():
    """
        Creación del índice CISI
        :return:
    """
    os.environ["retriv_base_path"] = retriv_base_path

    try:
        se = SearchEngine.load("cisi")
        print("Ya existe el índice \"cisi\" así que lo cargamos.")
    except:
        print("No existe el índice \"cisi\" así que lo creamos...")
        se = SearchEngine(
            index_name="cisi",
            model="bm25",
            stemmer="english",
            tokenizer="word",
            do_lowercasing=True,
            do_punctuation_removal=True
        )

        se.index_file(
            path=cisi_documents_path,
            show_progress=True
        )

        se.save()  # No es estrictamente necesario invocar save(), retriv siempre va a persistir el índice a disco

    menu_cisi(se=se)

def menu_cisi(se: SearchEngine):
    consultas = load_cisi_queries()
    
    consulta_previa = None

    while True:
        print("Menú cisi")
        print("1. Consulta predefinida al azar")
        print("2. TU PROPIA CONSULTA")
        print("3. More like this")
        print("4. Expansión de consultas con pseudo-relevance feedback")
        print("5. Evaluar rendimiento")
        print("X. VOLVER")

        seleccion = input("Elige una opción: ")

        consulta = None
        if seleccion == "1":
            random.shuffle(list(consultas.values()))
            consulta = list(consultas.values())[0]
        elif seleccion == "2":
            consulta = input("Escribe tu propia consulta: ")
        elif seleccion == "3":
            if consulta_previa is not None:
                id_consulta = get_query_id(consulta_previa, consultas)
                more_like_this(se, consulta_previa, id_consulta)
            else:
                print("Para buscar documentos similares necesitamos realizar primero una consulta...")
        elif seleccion == "4":
            if consulta_previa is not None:
                id_consulta = get_query_id(consulta_previa, consultas)
                expansion_consultas(se, consulta_previa, id_consulta)
            else:
                print("Necesitamos primero una consulta para expandirla...")
        elif seleccion == "5":
            report()
            continue
        elif seleccion == "x" or seleccion == "X":
            return
        else:
            print(seleccion, "no es una opción válida.")

        if consulta is not None:
            consulta_previa = consulta
            results = se.search(consulta, cutoff=5)
            print("\nConsulta: " + consulta + "\n\nResultados:")
            for result in results:
                print(result["text"][:80] + "...")
            print("----")
            id_consulta = get_query_id(consulta, consultas)
            p_1, p_10 = calculate_precision(id_consulta, results)
            print("Precisiones:")
            print(f"\tP@1 = {p_1}")
            print(f"\tP@10 = {p_10}")
            print("----")
            print(
                "¡Atención! Necesitaríamos snippets generados en base a la consulta, aka, \'query-biased "
                "summaries\'...\n")
            query_biased_summaries(consulta, results)

def get_query_id(consulta: str, consultas : dict) -> str:
    """
        Obtiene el identificador de una consulta
        :param consulta:
        :param consultas:
        :return:
    """
    for key, value in consultas.items():
        if consulta.strip() == value.strip():
            return key
    return None

def calculate_precision(id_consulta: str, results: list) -> tuple:
    """
        Calcula la precisión en 1 y la precisión en 10 de una consulta
        :param id_consulta:
        :param results:
        :return:
    """
    # Comprobación de que el id de la consulta exista en el documento y esté en los juicios de relevancia
    if id_consulta is None and id_consulta not in relevant_docs.keys():
        return
    # Carga de los juicios de relevancia
    relevant_docs = load_relevant_docs()
    p_1 = p_10 = 0
    for result in results:
        if result["id"] in relevant_docs[id_consulta][:1]:
            p_1 += 1
        if result["id"] in relevant_docs[id_consulta][:10]:
            p_10 += 1
    return (p_1/1, p_10/10)

def load_cisi_queries() -> dict:
    """
        Carga las consultas de Cisi en un diccionario
        :return:
    """
    consultas = {}
    with open(cisi_queries_path, "r") as f:
        for consulta in f.readlines():
            consultas[consulta.split("\t")[0]] = consulta.split("\t")[1].strip().replace("\n", "")
    return consultas

def load_relevant_docs() -> dict:
    """
        Carga los juicios de relevancia en un diccionario
        :return:
    """
    relevant_docs = {}
    with open(cisi_relevance_path, "r") as f:
        for consulta in f.readlines():
            relevant = consulta.split("\t")[1].split(' ')
            relevant_docs[consulta.split("\t")[0]] = relevant
    return relevant_docs

def more_like_this(se, consulta_previa, id_consulta: str = None):
    results = se.search(consulta_previa, cutoff=5)
    print("\nConsulta: " + consulta_previa + "\n\nResultados:")

    if len(results) > 0:
        top_result_text = results[0]
    else:
        top_result_text = None

    for result in results:
        print(result["text"][:80] + "...")
    print("----")

    if top_result_text is not None:
        # Modificación de more like this para usar query-biased summaries
        snippets = query_biased_summaries(consulta_previa, [top_result_text])
        best_snippet = next(iter(snippets.values()))[0]
        new_results = se.search(best_snippet , cutoff=5)
        print(f"\nResultados similares al snippet \'{best_snippet}\':")
        for result in new_results:
            print(result["text"][:160] + "...")
        print("----")
        if id_consulta is not None:
            p_1, p_10 = calculate_precision(id_consulta, results)
            print("Precisiones:")
            print(f"\tP@1 = {p_1}")
            print(f"\tP@10 = {p_10}")
    print("¡Atención! Necesitaríamos snippets generados en base a la consulta, aka, \'query-biased summaries\'...\n")
    print(
        "¡Atención con la colección 10000.train! Puesto que son combinaciones básicamente aleatorias de titulares, "
        "que dos documentos se parezcan no implica que el segundo documento tenga especial relación con la consulta "
        "original... Podría aplicarse more_like_this solo sobre el query-biased summary...\n")

def expansion_consultas(se, consulta, id_consulta: str = None):
    num_docs = input("¿Cuántos documentos quieres usar para el feedback (p.ej., 10)? ")
    try:
        num_docs = int(num_docs)
    except:
        num_docs = 10
    num_terms = input("¿Cuántos términos quieres añadir a la consulta expandida (p.ej., 10)? ")
    try:
        num_terms = int(num_terms)
    except:
        num_terms = 10
    search_with_pseudo_relevance_feedback(se, consulta, id_consulta, 5, num_docs, num_terms)

def search_with_pseudo_relevance_feedback(search_engine, consulta, id_consulta, cutoff, num_docs, num_terms):
    if num_docs > 0:
        top_documents = search_engine.search(consulta, cutoff=num_docs)
        texto = []
        for result in top_documents:
            texto.append(result["text"])
        texto = search_engine.query_preprocessing(" ".join(texto))
        texto = [s for s in texto if s.strip() != ""]
        frecuencias = Counter(texto)
        terminos = list(frecuencias.keys())
        doc_freqs = search_engine.get_term_doc_freqs(terminos)
        idfs = list()
        for entry in doc_freqs:
            try:
                idf = math.log(search_engine.doc_count / len(entry))
            except:
                idf = 0
            idfs.append(idf)

        tf_idfs = dict()
        for i in range(len(terminos)):
            termino = terminos[i]
            tf_idf = frecuencias[termino] * idfs[i]
            tf_idfs[termino] = tf_idf
        sorted_tf_idfs = dict(sorted(tf_idfs.items(), key=lambda item: item[1], reverse=True))
        top_terms = dict(list(sorted_tf_idfs.items())[:num_terms])
        print("Consulta original: ", consulta, "\n")
        print("Top terms: ", top_terms, "\n")
        consulta = consulta + " " + " ".join(top_terms)
        print("Consulta expandida: ", consulta, "\n\nResultados:")

    results = search_engine.search(consulta, cutoff=cutoff)
    for result in results:
        result["text"] = result["text"][:160] + "..."
        print(result)
    print("----")
    if id_consulta is not None:
        p_1, p_10 = calculate_precision(id_consulta, results)
        print("Precisiones:")
        print(f"\tP@1 = {p_1}")
        print(f"\tP@10 = {p_10}")

def query_biased_summaries(consulta: str, results: list) -> dict:
    """
        Crea query-biased summaries para los resultados
        :param consulta:
        :param results:
        :return:
    """
    # Vectorización de la consulta y de los documentos resultantes
    vectorized_query = set(word.lower() for word in consulta.split(' '))
    vectorized_results = vectorize(results)
    snippets = {} # {query: overlap_results}

    for vectorized_result in vectorized_results:
        overlap_results = {}  # {snippet: overlap}
        result = vectorized_result["text"]
        # Cálculo del overlap entre la consulta y los fragmentos de cada uno de los documentos
        for result_set in result:
            overlap = calculate_overlap(vectorized_query, result_set)
            overlap_results[' '.join(result_set)] = overlap
        snippets[vectorized_result["id"]] = overlap_results # {query: {snippet: overlap}}

    for key, value in snippets.items():
        # Ordenación de los snippets de cada documento en función de su valor de overlap
        sorted_query_results = dict(sorted(value.items(), key=lambda x: x[1], reverse=True))
        # Obtención de los cinco mejores snippets
        top_5_snippets = list(sorted_query_results.keys())[:5]
        snippets[key] = top_5_snippets

    print("\nQuery-Biased Summaries:")
    for key, value in snippets.items():
        print(f'{key}:')
        for snippet in value:
            print(f'\t{snippet}')
    print("----")
    return snippets

def vectorize(results: list) -> list:
    """
        Vectoriza los documentos de los resultados, de forma que cada documento sea una lista de listas de 10 palabras
        Documento:
            18 Editions of the Dewey Decimal Classifications The present study is a history of the DEWEY
            Decimal Classification. The first edition of the DDC was published in 1876, the eighteenth
            edition in 1971, and future editions will continue to appear as needed.
            In spite of the DDC's long and healthy life, however, its full story has never been told.
        Documento vectorizado:
            [
                ['18', 'edition', 'of', 'the', 'dewey', 'decimal', 'classifications', 'the', 'present', 'study'],
                ['is', 'a', 'history', 'of', 'the', 'dewey', 'decimal', 'classification'],
                ['the', 'first', 'edition', 'of', 'the', 'ddc', 'was', 'published', 'in', '1876'],
                ['the', 'eighteenth', 'edition', 'in', '1971'],
                ['future', 'editions', 'will', 'continue', 'to', 'appear', 'as', 'needed'],
                ['in', 'spite', 'of', 'the', 'ddc', 'long', 'and', 'healthy', 'life'],
                ['however', 'its', 'full', 'story', 'has', 'never', 'been', 'told']
            ]
        :param results:
        :return:
    """
    for result in results:
        words = result["text"].strip().split(' ')
        vectorized_results = []
        result_fragment = []
        for word in words:
            result_fragment.append(word.lower())
            if len(result_fragment) == 10:
                vectorized_results.append(list(result_fragment))
                result_fragment.clear()
        # En caso de que result_fragment no alcance 10 palabras y ya no haya más en el documento, añade el resto
        if result_fragment:
            vectorized_results.append(list(result_fragment))
        result["text"] = vectorized_results
    return results

def calculate_overlap(s1: set, s2: set) -> float:
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

def report():
    """
        Casos de prueba:
            - TF-IDF, con stemming
            - TF-IDF, sin stemming
            - BM-25, con stemming
            - BM-25, sin stemming
        :return:
    """

    queries = load_cisi_queries() # {id, consulta}

    report = []

    # Se añanden los casos de prueba al reporting
    report.append(test_conf(queries, "tf-idf", "english", "word"))
    report.append(test_conf(queries, "tf-idf", None, "word"))
    report.append(test_conf(queries, "bm25", "english", "word"))
    report.append(test_conf(queries, "bm25", None, "word"))

    print("El rendimiento del indice para distintas configuraciones es el siguiente:")
    for i in report: print(f"\t- {i}")

def test_conf(queries: dict, model: str, stemmer: str, tokenizer: str) -> str:
    """
        Cálculo de los valores de precisiones para distintas configuraciones
        :param queries:
        :param model:
        :param stemmer:
        :param tokenizer:
        :return:
    """
    se = configure_se_cisi(model, stemmer, tokenizer)
    values = []

    print(f"Model: {model}, Stemmer: {stemmer}, Tokenizer: {tokenizer}")
    for k, v in tqdm(queries.items()):
        # Obtención de los resultados para cada query
        results = se.search(v, cutoff=5)
        # Cálculo de los valores de precisiones
        t_1, t_10 = calculate_precision(k, results)
        values.append((t_1, t_10))

    t_1_mean = t_10_mean = 0

    # Cálculo de las medias
    for t in values:
        t_1_mean += t[0]
        t_10_mean += t[1]

    t_1_mean /= len(values)
    t_10_mean /= len(values)
    
    return f"[Conf: model={model}, stemmer={stemmer}, tokenizer={tokenizer}] - P@1={t_1_mean}, P@10={t_10_mean}"

def configure_se_cisi(model: str="bm25", stemmer: str=None, tokenizer: str=None) -> SearchEngine:
    """
        Configura el indice CISI
        :param model:
        :param stemmer:
        :param tokenizer:
        :return:
    """
    se = SearchEngine(
        index_name="cisi",
        model=model,
        stemmer=stemmer,
        tokenizer=tokenizer,
        do_lowercasing=True,
        do_punctuation_removal=True
    )

    se.index_file(
        path=cisi_documents_path,
        show_progress=False
    )

    return se

def main():
    menu_principal()

if __name__ == "__main__":
    main()

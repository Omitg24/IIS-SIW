import glob
import os
import random
import re

from ranx import Qrels, Run, compare
from retriv import DenseRetriever, SparseRetriever
from tqdm import tqdm

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
        print("4. Comparación de índices")
        print("X. SALIR")

        seleccion = input("Elige una opción: ")

        if seleccion == "1":
            pizzas()
        elif seleccion == "2":
            articles_10000()
        elif seleccion == "3":
            twenty_news_groups()
        elif seleccion == "4":
            compare_indexers()
        elif seleccion == "x" or seleccion == "X":
            exit()
        else:
            print(seleccion, "no es una opción válida.")


def pizzas():
    os.environ["retriv_base_path"] = retriv_base_path

    try:
        dr = DenseRetriever.load("pizzas_denso")
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

        dr = DenseRetriever(
            index_name="pizzas_denso",
            model="hiiamsid/sentence_similarity_spanish_es",
            # El modelo tiene que estar entrenado sobre textos en Español. Buscar modelos aquí: https://huggingface.co/models?pipeline_tag=sentence-similarity&sort=downloads
            normalize=True,
            max_length=128,
            use_ann=False
        )

        dr.index(
            collection=pizzas,
            show_progress=True
        )

        dr.save()  # No es estrictamente necesario invocar save(), retriv siempre va a persistir el índice a disco

    menu_pizzas(dr=dr)


def menu_pizzas(dr):
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

        if consulta != None:
            results = dr.search(consulta)
            print(consulta)
            for result in results:
                print(result)
            print("----")


def articles_10000():
    os.environ["retriv_base_path"] = retriv_base_path

    try:
        dr = DenseRetriever.load("articles_10000_denso")
        print("Ya existe el índice \"articles_10000\" así que lo cargamos.")
    except:
        print("No existe el índice \"articles_10000\" así que lo creamos...")
        dr = DenseRetriever(
            index_name="articles_10000_denso",
            model="sentence-transformers/all-MiniLM-L6-v2",  # "sentence-transformers/all-mpnet-base-v2",
            normalize=True,
            use_ann=True
            # ¡Atención! Hay un bug en autofaiss que parece solucionarse con este parche: https://github.com/criteo/autofaiss/issues/143
        )

        dr.index_file(
            path="articles_10000.jsonl",
            use_gpu=False,  # True,
            show_progress=True
        )

        dr.save()  # No es estrictamente necesario invocar save(), retriv siempre va a persistir el índice a disco

    menu_articles(dr=dr)


def menu_articles(dr):
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
            if consulta_previa != None:
                more_like_this(dr, consulta_previa)
            else:
                print("Para buscar documentos similares necesitamos realizar primero una consulta...")
        elif seleccion == "x" or seleccion == "X":
            return
        else:
            print(seleccion, "no es una opción válida.")

        if consulta != None:
            consulta_previa = consulta
            results = dr.search(consulta, cutoff=5)
            print("\nConsulta: " + consulta + "\n\nResultados:")
            for result in results:
                result["text"] = result["text"][:80] + "..."
                print(result)
            print("----")
            print(
                "¡Atención! Necesitaríamos snippets generados en base a la consulta, aka, \'query-biased summaries\'...\n")


def more_like_this(dr, consulta_previa):
    results = dr.search(consulta_previa, cutoff=5)
    print("\nConsulta: " + consulta_previa + "\n\nResultados:")

    if len(results) > 0:
        top_result_text = results[0]["text"]
    else:
        top_result_text = None

    for result in results:
        result["text"] = result["text"][:80] + "..."
        print(result)
    print("----")

    if top_result_text != None:
        new_results = dr.search(top_result_text, cutoff=5)
        print("\nResultados similares al primer documento:")
        for result in new_results:
            result["text"] = result["text"][:160] + "..."
            print(result)
        print("----")

    print("¡Atención! Necesitaríamos snippets generados en base a la consulta, aka, \'query-biased summaries\'...\n")
    print(
        "¡Atención con la colección 10000.train! Puesto que son combinaciones básicamente aleatorias de titulares, que dos documentos se parezcan no implica que el segundo documento tenga especial relación con la consulta original... Podría aplicarse more_like_this solo sobre el query-biased summary...\n")


def twenty_news_groups():
    os.environ["retriv_base_path"] = retriv_base_path

    try:
        dr = DenseRetriever.load("20newsgroups_denso")
        print("Ya existe el índice \"20newsgroups\" así que lo cargamos.")
    except:
        print("No existe el índice \"20newsgroups\" así que lo creamos...")
        dr = DenseRetriever(
            index_name="20newsgroups_denso",
            model="sentence-transformers/all-MiniLM-L6-v2",  # "sentence-transformers/all-mpnet-base-v2",
            normalize=True,
            use_ann=True
            # ¡Atención! Hay un bug en autofaiss que parece solucionarse con este parche: https://github.com/criteo/autofaiss/issues/143
        )

        folder_path = ".retriv/20news-18828.zip"

        collection = list()

        for archivo in glob.glob(os.path.join(folder_path, '**', '*'), recursive=True):
            if not os.path.isdir(archivo):
                print(archivo)

                with open(archivo, "r", encoding="latin1") as f:
                    text = f.read()
                    text = " ".join(text.splitlines())
                    text = re.sub(r'\s+', ' ', text)

                    collection.append({
                        "id": archivo,
                        "text": text
                    })

        dr.index(collection=collection, show_progress=True)

    menu_20_news_groups(dr=dr)


def menu_20_news_groups(dr):
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
        print("X. VOLVER")

        seleccion = input("Elige una opción: ")

        consulta = None
        if seleccion == "1":
            random.shuffle(consultas)
            consulta = consultas[0]
        elif seleccion == "2":
            consulta = input("Escribe tu propia consulta: ")
        elif seleccion == "3":
            if consulta_previa != None:
                more_like_this(dr, consulta_previa)
            else:
                print("Para buscar documentos similares necesitamos realizar primero una consulta...")
        elif seleccion == "x" or seleccion == "X":
            return
        else:
            print(seleccion, "no es una opción válida.")

        if consulta != None:
            consulta_previa = consulta
            results = dr.search(consulta, cutoff=5)
            print("\nConsulta: " + consulta + "\n\nResultados:")
            for result in results:
                result["text"] = result["text"][:160] + "..."
                print(result)
            print("----")
            print(
                "¡Atención! Necesitaríamos snippets generados en base a la consulta, aka, \'query-biased summaries\'...\n")


def compare_indexers():
    """
        Crea los QRels y las rondas de ejecución de ambos índices, para después compararlos y hacer un reporting de ello
        :return:
    """
    print("\nCOMPARACIÓN DE ÍNDICES DISPERSOS Y DENSOS")
    queries = load_cisi_queries()
    qrels = create_qrels(queries)
    # Creación del índice disperso y obtención de resultados
    sr = create_sparse_retriever()
    sr_run = create_run(sr, queries)
    # Creación del índice denso y obtención de resultados
    dr = create_dense_retriever()
    dr_run = create_run(dr, queries)
    # Comparación de los resultados obtenidos con cada índice con los QRels reales
    report = compare(qrels=qrels,
                     runs=[sr_run, dr_run],
                     metrics=[
                         "hit_rate@50",
                         "precision@50",
                         "recall@50",
                         "map@50",
                         "mrr@50"],
                     max_p=0.01,
                     make_comparable=True)
    print(report)


def create_run(r, queries: dict) -> Run:
    """
        Crea una ronda de ejecución para el índice y las queries pasadas por parámetro
        :param r:
        :param queries:
        :return:
    """
    run_dict = {}
    print(f"\n\tCreando Run: {r.__class__.__name__}...")
    for q_key, q_value in tqdm(queries.items()):
        # Obtención de los primeros 50 resultados
        results = r.search(q_value, cutoff=50)
        # Creación del diccionario de resultados
        run_dict[q_value] = {result["id"]: result["score"] for result in results}
    print('----')
    return Run(run_dict, name=f'CISI-{r.__class__.__name__}')


def create_qrels(queries: dict) -> Qrels:
    """
        Crea un Qrels a partir de las consultas pasadas por parámetro
        :param queries:
        :return:
    """
    relevant_docs = load_relevant_docs()
    qrels_dict = {}
    print("\tCreando Qrels...")
    for q_key, q_value in tqdm(queries.items()):
        for rd_key, rd_value in relevant_docs.items():
            # En caso de que los ids coincidan, añadir todos los documentos relevantes de dicha consulta
            if q_key == rd_key:
                qrels_dict[q_value] = {rd: 100 - (score / len(rd_value[:50])) * 100 for score, rd in
                                       enumerate(rd_value)}
    print('----')
    return Qrels(qrels_dict, name="CISI-QRels")


def create_sparse_retriever() -> SparseRetriever:
    """
        Crea un índice disperso
        :return:
    """
    os.environ["retriv_base_path"] = retriv_base_path
    try:
        sr = SparseRetriever.load("cisi_sparse")
        print("Ya existe el índice \"cisi_sparse\" así que lo cargamos.")
    except:
        print("No existe el índice \"cisi_sparse\" así que lo creamos...")
        sr = SparseRetriever(
            index_name="cisi_sparse",
            model="bm25",
            stemmer="english",
            tokenizer="word",
            do_lowercasing=True,
            do_punctuation_removal=True
        )

        sr = sr.index_file(
            path=cisi_documents_path,
            show_progress=True
        )

        sr.save()
    return sr


def create_dense_retriever() -> DenseRetriever:
    """
        Crea un índice denso
        :return:
    """
    os.environ["retriv_base_path"] = retriv_base_path
    try:
        dr = DenseRetriever.load("cisi_dense")
        print("Ya existe el índice \"cisi_dense\" así que lo cargamos.")
    except:
        print("No existe el índice \"cisi_dense\" así que lo creamos...")
        dr = DenseRetriever(
            index_name="cisi_dense",
            model="sentence-transformers/all-MiniLM-L6-v2",
            normalize=True,
            use_ann=False
        )

        dr = dr.index_file(
            path=cisi_documents_path,
            show_progress=True,
            use_gpu=False
        )

        dr.save()
    return dr


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


def main():
    menu_principal()


if __name__ == "__main__":
    main()

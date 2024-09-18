"""

Referencia del lenguaje de consulta:
    https://docs.vespa.ai/en/query-language.html

"""

def menu_principal():
    while True:
        print("Menú principal:")
        print("1. Ranking BM25")
        print("2. Ranking \"nativo\"")
        print("3. Búsqueda semántica")
        print("4. Experimento \"pregananant\"")
        print("X. SALIR")

        seleccion = input("Elige una opción: ")

        if seleccion=="1":
            ranking_bm25()
        elif seleccion=="2":
            ranking_nativo()
        elif seleccion=="3":
            busqueda_semantica()
        elif seleccion=="4":
            pregananant()
        elif seleccion=="x" or seleccion=="X":
            exit()
        else:
            print(seleccion,"no es una opción válida.")

from transformers import BertTokenizer, BertModel
from vespa.application import Vespa

"""

Función que recibe un texto *en inglés* y genera un embedding de 348 dimensiones.

Es exactamente la misma que en SIW-vespa-feed... Debe aplicarse exactamente el
mismo proceso para transformar la consulta puesto que, de lo contrario, estaremos
comparando "manzanas" con "naranjas", aún cuando las dimensiones de los embeddings
sean iguales.

"""

tokenizer = BertTokenizer.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')
model = BertModel.from_pretrained('sentence-transformers/all-MiniLM-L6-v2')

def text_to_embedding(text):
    tokens = tokenizer(text, return_tensors="pt", max_length=100, truncation=True, padding=True)
    outputs = model(**tokens)
    return outputs[0].tolist()[0][0]


def pregananant():
    app = Vespa(url = "http://localhost:8080/")

    typos = ["gregnant", "pegnat", "pegnate", "pegrancy", "pegrent", "prangent", "pregananant", "preganont", "pregant", "pregante", "pregegnant", "pregernet", "pregonate", "prengan", "prregnant"]

    print("Documentos que contienen alguno de los errores tipográficos de \"pregnant\" o \"pregnancy\"...\n")
    for consulta in typos:
        query = {
            'yql': 'select * from sources * where userQuery()',
            'query': consulta,
            'ranking': 'bm25',
            'type': 'all',
            'hits': 5
        }

        res = app.query(body=query)

        print(consulta, res.number_documents_retrieved)

    print("\n------\n")

    print("Documentos de la coleccion 20 Newsgroups \"próximos\" aka \"semánticamente relacionados\" con alguno de los términos con errores...\n")

    report = dict()

    for consulta in typos:
        query = {
          'yql': 'select * from VespaDemoSIW_content where ({targetHits:200}nearestNeighbor(text_embeddings,query_embedding));',
          'hits': 5,
          'query' : consulta,
          'ranking.features.query(query_embedding)': text_to_embedding(consulta),
          'ranking.profile': 'embedding_similarity'
        }


        res = app.query(body=query)

        for hit in res.hits:
            if hit["id"] not in report.keys():
                report[hit["id"]] = {
                    "consulta": consulta,
                    "relevance": hit["relevance"],
                    "text": hit["fields"]["text"]
                }
            else:
                new_relevance = hit["relevance"]
                current_relevance = report[hit["id"]]["relevance"]

                if new_relevance>current_relevance:
                    report[hit["id"]]["consulta"] = consulta

    valores = dict()

    for _id in report.keys():
        valores[_id] = report[_id]["relevance"]

    valores = sorted(valores.items(), key=lambda x: x[1], reverse=True)

    for (valor, relevance) in valores[0:20]:
        print(valor, "\t", relevance, "\t", report[valor]["consulta"], "\t", report[valor]["text"][:80])

    print("\n------\n")

def ranking_bm25():
    app = Vespa(url = "http://localhost:8080/")

    consultas = ["audi s4","battery charger","david koresh","dennis martinez","dodge wagon","dos 5.0","dos 6.0","encryption algorithm","fortran library","frequent nosebleeds","game boy","genesis","graphics library","hard disk","headphones","honda cbr600","honda crx","honda cx650","ibm","islam","jehovah's witnesses","jesus","joystick","jpeg specification","mac modem","macintosh","mark whiten","megadrive","metallica","ms excel","nikon","noisy engine","playoff results","powerbook","rock and roll","saab","scsi cable","sega","siggraph","space shuttle","stanley cup","toyota land cruiser","toyota wagons","vw passat","windows 3.1","windows nt"]

    for consulta in consultas:
        print(consulta, "(BM25)")

        query = {
            'yql': 'select * from sources * where userQuery()',
            'query': consulta,
            'ranking': 'bm25',
            'type': 'all',
            'hits': 5
        }

        res = app.query(body=query)

        print('Número de documentos disponibles: '+ str(res.number_documents_retrieved))
        print('Número de documentos retornados: '+ str(len(res.hits)))


        for hit in res.hits:
            print(hit["id"], "\t", hit["relevance"], "\t", hit["fields"]["text"][:80])

        print("\n------\n")


def ranking_nativo():
    app = Vespa(url = "http://localhost:8080/")

    consultas = ["audi s4","battery charger","david koresh","dennis martinez","dodge wagon","dos 5.0","dos 6.0","encryption algorithm","fortran library","frequent nosebleeds","game boy","genesis","graphics library","hard disk","headphones","honda cbr600","honda crx","honda cx650","ibm","islam","jehovah's witnesses","jesus","joystick","jpeg specification","mac modem","macintosh","mark whiten","megadrive","metallica","ms excel","nikon","noisy engine","playoff results","powerbook","rock and roll","saab","scsi cable","sega","siggraph","space shuttle","stanley cup","toyota land cruiser","toyota wagons","vw passat","windows 3.1","windows nt"]

    for consulta in consultas:
        print(consulta, "(Native rank)")

        query = {
            'yql': 'select * from sources * where userQuery()',
            'query': consulta,
            'ranking': 'native_rank',
            'type': 'all',
            'hits': 5
        }

        res = app.query(body=query)

        print('Número de documentos disponibles: '+ str(res.number_documents_retrieved))
        print('Número de documentos retornados: '+ str(len(res.hits)))


        for hit in res.hits:
            print(hit["id"], "\t", hit["relevance"], "\t", hit["fields"]["text"][:80])

        print("\n------\n")

def busqueda_semantica():
    app = Vespa(url = "http://localhost:8080/")

    consultas = ["audi s4","battery charger","david koresh","dennis martinez","dodge wagon","dos 5.0","dos 6.0","encryption algorithm","fortran library","frequent nosebleeds","game boy","genesis","graphics library","hard disk","headphones","honda cbr600","honda crx","honda cx650","ibm","islam","jehovah's witnesses","jesus","joystick","jpeg specification","mac modem","macintosh","mark whiten","megadrive","metallica","ms excel","nikon","noisy engine","playoff results","powerbook","rock and roll","saab","scsi cable","sega","siggraph","space shuttle","stanley cup","toyota land cruiser","toyota wagons","vw passat","windows 3.1","windows nt"]

    for consulta in consultas:
        print(consulta, "(Embeddings aka \"búsqueda semántica\")")

        query = {
          'yql': 'select * from VespaDemoSIW_content where ({targetHits:100}nearestNeighbor(text_embeddings,query_embedding));',
          'hits': 5,
          'query' : consulta,
          'ranking.features.query(query_embedding)': text_to_embedding(consulta),
          'ranking.profile': 'embedding_similarity'
        }


        res = app.query(body=query)

        print('Número de documentos disponibles: '+ str(res.number_documents_retrieved))
        print('Número de documentos retornados: '+ str(len(res.hits)))


        for hit in res.hits:
            print("\t", hit["id"], "\t", hit["relevance"], "\t", hit["fields"]["text"][:80])

        print("\n------\n")

def main():
    menu_principal()

if __name__ == "__main__":
    main()

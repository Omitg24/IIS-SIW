from vespa.package import ApplicationPackage, Field, FieldSet, HNSW, QueryProfile, QueryProfileType, QueryTypeField, RankProfile
from vespa.deployment import VespaDocker

"""

Creamos el "Application Package":
    https://docs.vespa.ai/en/application-packages.html

"""

app_package = ApplicationPackage(name="VespaDemoSIW")

"""

Definimos el esquema de los documentos de nuestra aplicación

Referencia sobre campos "attribute":
    https://docs.vespa.ai/en/attributes.html
Referencia sobre campos "summary":
    https://docs.vespa.ai/en/document-summaries.html
Referencia sobre campos "index":
    https://docs.vespa.ai/en/reference/schema-reference.html#index
Referencia sobre el algoritmo Hierarchical Navigable Small World (HNSW) para
búsqueda de k-vecinos:
    https://docs.vespa.ai/en/reference/schema-reference.html#index-hnsw

Los nombres "id", "text" y "text_embeddings" se los proporcionamos nosotros;
podrían ser "identificador", "contenido" y "vectores" o cualquier otra cosa...

Obsérvese que el tipo de "text_embeddings" es un "tensor"
(https://en.wikipedia.org/wiki/Tensor) con 384 componentes. ¿Por qué 384?
Porque va a utilizarse este modelo lingüístico para generar los vectores densos:
    https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2
Y ese modelo genera vectores de 384 componentes...

Si usáramos google/bert_uncased_L-8_H-512_A-8 entonces el tipo sería:
    tensor<float>(x[512])

"""

app_package.schema.add_fields(
    Field(name = "id", type = "string", indexing = ["attribute", "summary"]),
    Field(name = "text", type = "string", indexing = ["index", "summary"], index = "enable-bm25"),
    Field(name = "text_embeddings", type="tensor<float>(x[384])", indexing=["attribute", "index"],
        ann=HNSW(
            distance_metric="euclidean",
            max_links_per_node=16,
            neighbors_to_explore_at_insert=500
        ),
    )
)

"""

¡Ojo, cuidado! Si se desea utilizar userQuery() que permite indicar consultas
en un lenguaje de consulta simplificado pero con operadores (análogo al de
Google o ElasticSearch) tiene que haber un conjunto de campos por defecto para
aplicarlo.

"""

app_package.schema.add_field_set(
    FieldSet(name = "default", fields = ["text"])
)


"""

Se añaden distintos sistemas de ranking:

    - El conocido BM25: https://docs.vespa.ai/en/reference/rank-features.html#bm25
    - Un método de ranking propio de Vespa: https://docs.vespa.ai/en/reference/nativerank.html
    - Un método "semántico": proximidad entre consulta y el campo que almacena
      los embeddings correspondientes al texto de cada documento...

"""

app_package.schema.add_rank_profile(RankProfile(name = "bm25", first_phase = "bm25(text)"))
app_package.schema.add_rank_profile(RankProfile(name = "native_rank", first_phase = "nativeRank(text)"))
app_package.schema.add_rank_profile(RankProfile(name = "embedding_similarity", first_phase = "closeness(text_embeddings)"))

"""

Al utilizar embeddings hay que indicar cómo se va a codificar la consulta.

Por supuesto tiene que ser un "tensor" con el mismo número de dimensiones que
los documentos y que, además, se debe generar con el mismo modelo lingüístico.

"""

app_package.query_profile = QueryProfile()
app_package.query_profile_type = QueryProfileType(
    fields=[
        QueryTypeField(
            name="ranking.features.query(query_embedding)",
            type="tensor<float>(x[384])",
        )
    ]
)

"""

Nos conectamos a Docker y desplegamos una instancia Vespa con esta aplicación.

El puerto por defecto es el 8080.

Pueden tenerse varias instancias siempre que se desplieguen en puertos diferentes...

"""

vespa_docker = VespaDocker()
app = vespa_docker.deploy(application_package=app_package)
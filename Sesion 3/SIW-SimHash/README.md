# Sistemas de Información para la Web
## SimHash
### Descripción
<p text-align="justify">
    Práctica 3, correspondiente a SimHash, que se basa en la búsqueda de cuasi-duplicados de un archivo de documentos, para su posterior filtrado y realizar consultas en esos documentos, utilizando la medida de similitud asignada (en mi caso Coeficiente de Solapamiento).
</p>

### Forma de uso
<p text-align="justify">
    Para utilizarlo es necesario el paso de 5 parámetros, los cuales son:
</p>

* _documents_file:_ nombre del archivo donde se encuentran los documentos con los que se va a realizar la detección de cuasi-duplicados y de donde buscarán las consultas
* _queries_file:_ nombre del archivo donde se encuentran las queries con las que se van a realizar las consultas.
* _k:_ longitud de los shingles a generar.
    * valor por defecto: *3*.
* _f:_ dimensión de las firmas, a mayor número de documentos se recomienda que el valor sea 128.
    * valor por defecto: *64*.
* _tokenizer_name:_ Tokenizador que se va a utilizar tanto para los documentos como para las queries.
    * valor por defecto: *WhitespaceTokenizer*.

### Medida de similitud a utilizar
<p text-align="justify">
    <em>"La medida de similitud a implementar dependerá de tu número de DNI. Coge el número y calcula su módulo 4. En función del resultado implementarás la siguiente medida: 0 = Dice, 1 = Jaccard, 2 = Coseno, 3 = Solapamiento."</em> 
</p>

3289095 mod 4 = 3 -> Coeficiente de solapamiento: | X ∩ Y| / min(|X|, |Y|)

### Decisiones tomadas.
<p text-align="justify">
  Para la realización de la práctica se ha empleado un tokenizador que podrá ser seleccionado por el usuario (por defecto está el WhitespaceTokenizer, como ya se ha mencionado). Posteriormente, tanto los documentos como las consultas serán pasados a minúsculas, además de la tokenización ya realizada.  
</p>

<p text-align="justify">
  Un ejemplo de como serían los documentos o las queries tras la tokenización y vectorización es el siguiente:
</p>

```
  Documentos:
    {
      (t980, [a, man, was, shot, dead, and, fifteen, others, injured, when, zambian, policemen, clashed, with, ...]),
      (t1088, [russian, prime, minister, viktor, chernomyrdin, on, thursday, proposed, a, three-phase, solution, ...]),
      ...
    }
    
  Queries:
    [
      [bangladesh, anti-government, strike], 
      [baseball, players, legal, victory], 
      ...
    ]
```
# Sistemas de Información para la Web
## Creación de un _crawler_ básico
### Descripción
<p text-align="justify">
    El crawler realizado para la práctica 2 de la asignatura representa una implementación básica de lo que sería un crawler real para la extracción de información y documentos en la web.
</p>

### Forma de uso
<p text-align="justify">
    Para utilizarlo es necesario el paso de 4 parámetros, los cuales son:
</p>

* _filename:_ nombre del archivo donde se encuentran los enlaces para su posterior _crawling_ correspondiente.
* _max_downloads:_ número máximo de descargas permitidas.
    * valor por defecto: *10*.
* _seconds:_ número de segundos a esperar entre peticiones.
    * valor por defecto: *2*.
* _search_type:_ tipo de búsqueda a realizar, siendo este _breadth-first_ (en anchura) o _depth-first_ (en profundidad).
    * valor por defecto: *false (_depth-first_)*.

### Ejemplos y resultados obtenidos.

<p text-align="justify">
    <em>seed.txt</em> contiene el siguiente enlace: <a href="https://www.game.es/"><em>https://www.game.es/</em></a>.
    <br>
    <em>seeds.txt</em> contiene los siguientes enlaces: 
    <ul>
        <li>
            <a href="https://en.wikipedia.org/wiki/Dromaeosauroides"><em>https://en.wikipedia.org/wiki/Dromaeosauroides</em></a>.
        </li>
        <li>
            <a href="https://en.wikipedia.org/wiki/Theropoda"><em>https://en.wikipedia.org/wiki/Theropoda</em></a>.
        </li>
        <li>
            <a href="https://en.wikipedia.org/wiki/Dinosaur"><em>https://en.wikipedia.org/wiki/Dinosaur</em></a>.
        </li>
        <li>
            <a href="https://en.wikipedia.org/wiki/Early_Cretaceous"><em>https://en.wikipedia.org/wiki/Early_Cretaceous</em></a>.
        </li>
    </ul>        
<p text-align="justify">
  Cabe mencionar que se intentó probar con otros enlaces, tales como: <a href="http://ingenieriainformatica.uniovi.es/"><em>http://ingenieriainformatica.uniovi.es/</em></a>, pero se encintraron errores relacionados con la configuración SSL, uno de ellos (el más predominante) era el siguiente:
</p>


<urlopen error [SSL: UNSAFE_LEGACY_RENEGOTIATION_DISABLED] unsafe legacy renegotiation disabled (_ssl.c:1006)>

Pasando a los resultados obtenidos, distingo entre los dos tipos de recorrido empleado.


#### Un único enlace
##### Recorrido en profundidad.
```commandline    
    Crawyler.py files/seed.txt
```
##### Resultados obtenidos.
````text
SISTEMAS DE INFORMACIÓN PARA LA WEB
- CRAWLER BÁSICO
	Links a explorar: 
	 -> https://www.game.es
	Número de descargas permitidas:  10
	Tiempo de espera entre peticiones:  2 sec
	Recorrido en profundidad
	--> 10 ---------------
		Link actual:  https://www.game.es
	--> 9 ---------------
		Link actual:  https://www.game.es/tiendas
	--> 8 ---------------
		Link actual:  https://www.game.es/app
	--> 7 ---------------
		Link actual:  https://www.game.es/atencion-al-cliente
	--> 6 ---------------
		Link actual:  https://www.game.es/atencion-al-cliente#header-login
	--> 5 ---------------
		Link actual:  https://www.game.es/comprar
	--> 4 ---------------
		Link actual:  https://www.game.es/comprar#header-login
	--> 3 ---------------
		Link actual:  https://www.game.es/VIDEOJUEGOS
	--> 2 ---------------
		Link actual:  https://www.game.es/VIDEOJUEGOS#header-login
	--> 1 ---------------
		Link actual:  https://www.game.es/xbox-all-access
 - FIN DEL CRAWLING
````

##### Recorrido en anchura.
```commandline    
    Crawyler.py files/seed.txt -downloads 10 -seconds 2 -search
```
##### Resultados obtenidos.
````text
SISTEMAS DE INFORMACIÓN PARA LA WEB
- CRAWLER BÁSICO
	Links a explorar: 
	 -> https://www.game.es
	Número de descargas permitidas:  10
	Tiempo de espera entre peticiones:  2 sec
	Recorrido en anchura
	--> 10 ---------------
		Link actual:  https://www.game.es
	--> 9 ---------------
		Link actual:  https://www.game.es/tiendas
	--> 8 ---------------
		Link actual:  https://www.game.es/app
	--> 7 ---------------
		Link actual:  https://www.game.es/atencion-al-cliente
	--> 6 ---------------
		Link actual:  https://www.game.es#header-login
	--> 5 ---------------
		Link actual:  https://www.game.es/comprar
	--> 4 ---------------
		Link actual:  https://www.game.es/VIDEOJUEGOS
	--> 3 ---------------
		Link actual:  https://www.game.es/xbox-all-access
	--> 2 ---------------
		Link actual:  https://www.game.es/videojuegos/consolas
	--> 1 ---------------
		Link actual:  https://www.game.es/VIDEOJUEGOS/PS5
 - FIN DEL CRAWLING
````

#### Fichero con múltiples enlaces.

###### Recorrido en profundidad
```commandline    
    Crawyler.py files/seeds.txt
```
###### Resultados obtenidos
````text
SISTEMAS DE INFORMACIÓN PARA LA WEB
- CRAWLER BÁSICO
	Links a explorar: 
	 -> https://en.wikipedia.org/wiki/Dromaeosauroides
	 -> https://en.wikipedia.org/wiki/Theropoda
	 -> https://en.wikipedia.org/wiki/Dinosaur
	 -> https://en.wikipedia.org/wiki/Early_Cretaceous
	Número de descargas permitidas:  10
	Tiempo de espera entre peticiones:  2 sec
	Recorrido en profundidad
	--> 10 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Dromaeosauroides
	--> 9 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Dromaeosauroides#bodyContent
	--> 8 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Main_Page
	--> 7 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Main_Page#bodyContent
	--> 6 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Wikipedia:Contents
	--> 5 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Wikipedia:Contents#bodyContent
	--> 4 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Portal:Current_events
	--> 3 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Portal:Current_events#bodyContent
	--> 2 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Special:Random
	--> 1 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Wikipedia:About
 - FIN DEL CRAWLING
````

##### Recorrido en anchura
```commandline    
    Crawyler.py files/seeds.txt -downloads 10 -seconds 2 -search
```
###### Resultados obtenidos
````text
SISTEMAS DE INFORMACIÓN PARA LA WEB
- CRAWLER BÁSICO
	Links a explorar: 
	 -> https://en.wikipedia.org/wiki/Dromaeosauroides
	 -> https://en.wikipedia.org/wiki/Theropoda
	 -> https://en.wikipedia.org/wiki/Dinosaur
	 -> https://en.wikipedia.org/wiki/Early_Cretaceous
	Número de descargas permitidas:  10
	Tiempo de espera entre peticiones:  2 sec
	Recorrido en anchura
	--> 10 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Dromaeosauroides
	--> 9 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Theropoda
	--> 8 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Dinosaur
	--> 7 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Early_Cretaceous
	--> 6 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Dromaeosauroides#bodyContent
	--> 5 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Main_Page
	--> 4 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Wikipedia:Contents
	--> 3 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Portal:Current_events
	--> 2 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Special:Random
	--> 1 ---------------
		Link actual:  https://en.wikipedia.org/wiki/Wikipedia:About
 - FIN DEL CRAWLING
````
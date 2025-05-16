# 0. Enllaç al Repositori

`https://github.com/Krisoc123/ProjecteWeb.git`

El codi coresponen a aquesta entrega serà el que es troba a la branca `main` del repositori.

# 1. Autocompletat amb AJAX i l'API de Google Books



En el nostre projecte d'intercanvi de llibres, hem implementat una funcionalitat d'autocompletat que utilitza AJAX (Asynchronous JavaScript and XML) per fer consultes en temps real a l'API de Google Books, proporcionant suggeriments mentre l'usuari escriu en els camps del formulari.

## Com funciona l'autocompletat en el nostre projecte?

Quan un usuari comença a escriure el títol d'un llibre o el nom d'un autor en el nostre formulari de cerca, el sistema realitza una petició en segon pla a l'API de Google Books. L'API processa aquesta petició i retorna una llista de possibles coincidències, que es mostren immediatament sota el camp de text sense necessitat de recarregar la pàgina.

## Implementació

La nostra implementació utilitza jQuery UI Autocomplete i fa crides AJAX a l'API de Google Books. Hem creat dues funcionalitats d'autocompletat separades:

### 1. Autocompletat per a títols de llibres

Quan l'usuari escriu al camp de títol, el sistema fa una crida a l'API de Google Books cercant llibres que continguin el text introduït en el seu títol. Només s'inicien les cerques quan l'usuari ha escrit almenys 4 caràcters, per evitar resultats massa generals.

```javascript
$(function() {
    console.log("Document ready, inicialitzant autocompletat");
    
    if ($("#id_title").length) {
        console.log("Element #id_title trobat, aplicant autocompletat");
        
        $("#id_title").autocomplete({
            source: function(request, response) {
                console.log("Enviant petició a Google Books:", request.term);
                
                $.ajax({
                    url: "https://www.googleapis.com/books/v1/volumes",
                    dataType: "json",
                    data: {
                        q: "intitle:" + request.term,
                        maxResults: 10
                    },
                    success: function(data) {
                        console.log("Resposta rebuda:", data);
                        
                        if (!data.items) {
                            console.log("No s'han trobat resultats");
                            return response([]);
                        }
                        
                        response($.map(data.items, function(item) {
                            const volume = item.volumeInfo;
                            return {
                                label: volume.title,
                                value: volume.title
                            };
                        }));
                    },
                    error: function(xhr, status, error) {
                        console.error("Error API:", error);
                        response([]);
                    }
                });
            },
            minLength: 4
        });
    } else {
        console.log("ERROR: No s'ha trobat l'element #id_title!");
    }
});
```

#### Explicació detallada del codi:


  * `$(function() { ... })`: Aquesta funció s'executa quan el document HTML està completament carregat.
  * Garanteix que tots els elements del DOM estan disponibles abans de manipular-los.


  * `$("#id_title").autocomplete({ ... })`: Inicialitza el component jQuery UI Autocomplete.
  * La propietat `source` és una funció que proporciona les dades per a l'autocompletat.
  * `minLength: 4`: Estableix que l'autocompletat només s'activi quan s'hagin escrit almenys 4 caràcters.

  * `$.ajax({ ... })`: Realitza una petició asíncrona a l'API de Google Books.
  * `url`: Especifica l'endpoint de l'API.
  * `dataType: "json"`: Indica que espera rebre les dades en format JSON.
  * `data`: Conté els paràmetres de la petició:
    * `q: "intitle:" + request.term`: Opera amb "intitle:" per buscar el text només als títols dels llibres.
    * `maxResults: 10`: Limita el nombre de resultats.

    D'aquesta manera, la consulta a l'endpoint de Google Books es realitza amb el següent format:
    ```
    https://www.googleapis.com/books/v1/volumes?q=intitle:{{text}}&maxResults=10
    ```
  * `success: function(data) { ... }`: S'executa quan la petició té èxit.
  * Comprova si hi ha resultats amb `if (!data.items)`.
  * Transforma les dades rebudes al format que necessita l'autocomplete mitjançant `$.map()`.
  * Cada ítem es transforma en un objecte amb `label` (text visible) i `value` (valor seleccionat).
  * `error: function(xhr, status, error) { ... }`: S'executa si hi ha un error en la petició.
  * Registra l'error a la consola i retorna un array buit.



De manera similar, quan l'usuari escriu al camp d'autor, el sistema cerca autors que coincideixin amb el text introduït. En aquest cas, hem implementat una lògica addicional per extreure tots els autors únics dels resultats retornats per l'API.

```javascript
$(function() {
    $("#id_author").autocomplete({
        source: function(request, response) {
            $.ajax({
                url: "https://www.googleapis.com/books/v1/volumes",
                dataType: "json",
                data: {
                    q: "inauthor:" + request.term,
                    maxResults: 10
                },
                success: function(data) {
                    if (!data.items) {
                        return response([]);
                    }
                    
                    const authors = new Set();
                    
                    $.each(data.items, function(i, item) {
                        const volume = item.volumeInfo;
                        if (volume.authors && Array.isArray(volume.authors)) {
                            volume.authors.forEach(function(author) {
                                authors.add(author);
                            });
                        }
                    });
                    
                    const uniqueAuthors = Array.from(authors).map(function(author) {
                        return {
                            label: author,
                            value: author
                        };
                    });
                    
                    response(uniqueAuthors);
                },
                error: function(xhr, status, error) {
                    console.error("Error API:", error);
                    response([]);
                }
            });
        },
        minLength: 3,
        delay: 300
    });
});
```


* **Inicialització de l'autocompletat**:
  * `$("#id_author").autocomplete({ ... })`: Configura el component d'autocompletat al camp d'autor.
  * A diferència del cas anterior, aquest s'activa amb només 3 caràcters (`minLength: 3`).

  * Utilitza el mateix endpoint de Google Books, però amb el paràmetre `inauthor:` per cercar específicament autors.
  * De manera similar a la cerca de títols, es limita a 10 resultats.


  * A diferència de la cerca de títols, un llibre pot tenir múltiples autors.
  * `const authors = new Set()`: Crea un conjunt (Set) per emmagatzemar autors únics.
  * `volume.authors.forEach(function(author) { authors.add(author) })`: Afegeix cada autor al conjunt, automàticament eliminant duplicats.


  * `Array.from(authors).map(...)`: Converteix el conjunt d'autors en un array i després aplica una transformació.
  * Crea un objecte amb `label` i `value` per cada autor, que és el format que espera l'autocompletat.

  * `response(uniqueAuthors)`: Retorna la llista d'autors únics al component d'autocompletat.
  * De manera similar a la cerca de títols, gestiona els errors retornant un array buit.

Aquestes funcionalitats d'autocompletat s'integren en el nostre formulari de cerca de llibres, aquests són els camps HTML corresponents:

```html
    <input id="id_title" type="text" name="title" placeholder="Book title..." value="{{ request.GET.title }}">
    <input id="id_author" type="text" name="author" placeholder="Author name..." value="{{ request.GET.author }}">
```

![](https://i.imgur.com/ZzxEbjl.png)

# Creació d'instàncies
S'han implementat diverses funcionalitats on es creen instàncies a la base de dades, a continuació s'explica detalladament la creació d'instàncies en les relacions `Have` i `Want` (WishList) del model relacional.
Aquestes funcionalitats es poden trobar a `books.html` i `book-entry.html`, on es troben els botons pertinents. S'han utilitzat Class-Based Views i ModelForms per a la creació, actualització i eliminació d'instàncies a la base de dades.



## Implementació de WishList i HaveList amb Class-Based Views

La implementació de les funcionalitats WishList i HaveList al nostre sistema segueix un flux complet des de la interfície d'usuari fins a la persistència a la base de dades. Hem utilitzat les vistes basades en classes de Django tal com es recomanava a l'enunciat, aconseguint un codi més organitzat i reutilitzable.

El flux complet de l'aplicació comença a les targetes de llibres, on l'usuari inicia el procés fent clic en un botó. En aquest punt, el nostre sistema segueix una seqüència de passos que explicarem detalladament.

### Del botó a la vista: Inici del procés

Tot comença a les targetes de llibres (`book_card.html` i `external_book_card.html`), on implementem botons que permeten als usuaris afegir un llibre a les seves llistes personals. Aquests botons són enllaços HTML que inclouen els paràmetres necessaris:

```html
<!-- book_card.html -->
<a href="{% url 'add_to_wishlist' %}?isbn={{ book.ISBN }}&title={{ book.title|urlencode }}&author={{ book.author.name|urlencode }}" class="love-button" title="Want!">
    <svg>...</svg>
</a>
```


![](https://i.imgur.com/IepxlLq.png)


Quan l'usuari clica aquest botó, l'aplicació redirigeix a la URL especificada, afegint com a paràmetres GET les dades del llibre. Al fitxer `urls.py` definim les rutes corresponents que connecten aquestes URLs amb les vistes adequades:

```python
# urls.py
path('add-to-wishlist/', views.CreateWantView.as_view(), name='add_to_wishlist'),
path('add-to-havelist/', views.CreateHaveView.as_view(), name='add_to_havelist'),
```

### Processament a la vista (GET): Preparació del formulari

Quan la petició arriba a la vista, s'executa el mètode GET. Hem implementat dues classes: `CreateWantView` i `CreateHaveView`, que hereten de `LoginRequiredMixin` (per assegurar que l'usuari està autenticat) i `CreateView` (per gestionar la creació de nous objectes). 

```python
# views.py
class CreateWantView(LoginRequiredMixin, CreateView):
    model = Want
    form_class = WantForm
    template_name = 'want_form.html'
    success_url = reverse_lazy('books')
```

El mètode `get_initial()` s'encarrega de recollir els paràmetres de la URL i inicialitzar el formulari:

```python
def get_initial(self):
    initial = super().get_initial()
    initial['isbn'] = self.request.GET.get('isbn', '')
    initial['title'] = self.request.GET.get('title', '')
    initial['author'] = self.request.GET.get('author', '')
    initial['topic'] = self.request.GET.get('topic', '')
    return initial
```

### Renderització del formulari: Presentació a l'usuari

La vista renderitza el formulari al template corresponent, mostrant la informació del llibre i els camps necessaris per completar l'acció. El template `want_form.html` mostra un formulari amb dades precàrregades:

```html
<!-- want_form.html -->
<div class="book-info2">
    <h3>{{ request.GET.title }}</h3>
    <p>by {{ request.GET.author }}</p>
    <p class="isbn">ISBN: {{ request.GET.isbn }}</p>
</div>

<div class="form-group">
    <label for="{{ form.priority.id_for_label }}">Priority:</label>
    {{ form.priority }}
    <small class="form-text">{{ form.priority.help_text }}</small>
</div>

{{ form.isbn }}  <!-- Camp ocult -->
{{ form.title }}  <!-- Camp ocult -->
{{ form.author }}  <!-- Camp ocult -->
```
![](https://i.imgur.com/vOVyewi.png)

Els camps específics (prioritat per WishList, estat per HaveList) es mostren visiblement, mentre que els camps amb la informació del llibre es mantenen ocults:

```python
# forms.py
class WantForm(forms.ModelForm):
    priority = forms.IntegerField(
        min_value=1, max_value=5,
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text='Set the priority of this book (1=lowest, 5=highest)'
    )
    
```

### Processament a la vista (POST): Persistència de dades

Quan l'usuari envia el formulari, s'executa el mètode POST que activa `form_valid()`. Aquest mètode realitza les següents accions:

1. Verifica si el llibre existeix a la base de dades, creant-lo si és necessari:

```python
try:
    book = Book.objects.get(ISBN=isbn)
except Book.DoesNotExist:
    book = Book(
        ISBN=isbn,
        title=title,
        author=author,
        topic=topic or "General",
        publish_date=timezone.now().date(),
        base_price=10
    )
    book.save()
```

2. Comprova si ja existeix una relació usuari-llibre, actualitzant-la o creant-ne una nova:

```python
# Per WishList:
existing_want = Want.objects.filter(user=custom_user, book=book).first()

if existing_want:
    existing_want.priority = form.cleaned_data['priority']
    existing_want.save()
else:
    want = form.save(commit=False)
    want.user = custom_user
    want.book = book
    want.save()
```

3. Redirigeix l'usuari a la pàgina de llibres (`success_url = reverse_lazy('books')`).

Aquest flux complet garanteix poder afegir llibres a les llistes personals amb només uns pocs clics, mentre que el sistema s'encarrega de la validació, la consistència de les dades i la gestió d'errors.

La integració amb fonts externes com Google Books és transparent per a l'usuari, ja que el sistema crea automàticament els llibres que no existeixen prèviament a la nostra base de dades, realitzant validacions addicionals de l'ISBN i altres camps per mantenir la integritat de les dades.

```python
# models.py
class Have(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('used', 'Used'),
        ('damaged', 'Damaged')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='used')
```

En resum, la implementació de WishList i HaveList segueix un flux complet: des del botó a la targeta del llibre, passant per les URLs i vistes, mostrant un formulari adaptat, i finalment processant i emmagatzemant les dades, tot mentre garanteix l'autenticació d'usuaris, la validació de dades i la prevenció de duplicats.


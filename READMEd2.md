# Autocompletat amb AJAX i l'API de Google Books

## Introducció

En el nostre projecte d'intercanvi de llibres, hem implementat una funcionalitat d'autocompletat que utilitza AJAX (Asynchronous JavaScript and XML) per fer consultes en temps real a l'API de Google Books, proporcionant suggeriments mentre l'usuari escriu en els camps del formulari.

## Com funciona l'autocompletat en el nostre projecte

Quan un usuari comença a escriure el títol d'un llibre o el nom d'un autor en el nostre formulari de cerca, el sistema realitza una petició en segon pla a l'API de Google Books. L'API processa aquesta petició i retorna una llista de possibles coincidències, que es mostren immediatament sota el camp de text sense necessitat de recarregar la pàgina.

## Implementació tècnica

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

# Implementació de WishList i HaveList amb Class-Based Views i ModelForms

## Introducció

En el nostre projecte d'intercanvi de llibres, hem implementat dues funcionalitats essencials que permeten als usuaris gestionar els seus interessos: la llista de desitjos (WishList) i la llista de llibres que tenen (HaveList) utilitzant Class-Based Views i ModelForms per a la creació, actualització i eliminació d'instàncies a la base de dades.

# Creació d'instàncies a la base de dades

## Els ModelForms

Per gestionar la creació i actualització d'aquestes entitats, utilitzem ModelForms:

```python
# Exemple de ModelForms
from django import forms
from .models import WishList, HaveList

class WishListForm(forms.ModelForm):
    class Meta:
        model = WishList
        fields = ['book']  # Normalment només necessitem el llibre, ja que l'usuari s'obté del request
        
class HaveListForm(forms.ModelForm):
    class Meta:
        model = HaveList
        fields = ['book', 'condition']  # Incloem la condició del llibre
```

## Les Class-Based Views

Per implementar la creació d'instàncies a la base de dades, utilitzem Class-Based Views que simplifiquen el procés:

```python
# Exemple de Class-Based Views
from django.views.generic import CreateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from .models import Book, WishList, HaveList
from .forms import WishListForm, HaveListForm

class AddToWishListView(LoginRequiredMixin, CreateView):
    model = WishList
    form_class = WishListForm
    success_url = reverse_lazy('wishlist')
    
    def form_valid(self, form):
        # Assignem l'usuari actual abans de desar
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        # Gestió dels paràmetres GET (com en els enllaços del nostre exemple)
        isbn = request.GET.get('isbn')
        title = request.GET.get('title')
        author_name = request.GET.get('author')
        
        # Busquem o creem el llibre si no existeix
        book, created = Book.objects.get_or_create(
            ISBN=isbn,
            defaults={'title': title}
        )
        
        # Busquem o creem l'autor si no existeix
        if created and author_name:
            author, _ = Author.objects.get_or_create(name=author_name)
            book.author = author
            book.save()
        
        # Creem l'entrada a la WishList
        WishList.objects.get_or_create(user=request.user, book=book)
        
        return redirect('wishlist')

class AddToHaveListView(LoginRequiredMixin, CreateView):
    model = HaveList
    form_class = HaveListForm
    success_url = reverse_lazy('havelist')
    
    def form_valid(self, form):
        # Assignem l'usuari actual abans de desar
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get(self, request, *args, **kwargs):
        # Gestió dels paràmetres GET (com en els enllaços del nostre exemple)
        isbn = request.GET.get('isbn')
        title = request.GET.get('title')
        author_name = request.GET.get('author')
        
        # Busquem o creem el llibre si no existeix
        book, created = Book.objects.get_or_create(
            ISBN=isbn,
            defaults={'title': title}
        )
        
        # Busquem o creem l'autor si no existeix
        if created and author_name:
            author, _ = Author.objects.get_or_create(name=author_name)
            book.author = author
            book.save()
        
        # Redirigim al formulari per afegir detalls adicionals com la condició del llibre
        return redirect('add_have_details', isbn=isbn)
```

## La configuració d'URLs

Finalment, cal configurar les URLs per enllaçar amb les vistes:

```python
# Exemple de configuració d'URLs
from django.urls import path
from .views import AddToWishListView, AddToHaveListView

urlpatterns = [
    path('add-to-wishlist/', AddToWishListView.as_view(), name='add_to_wishlist'),
    path('add-to-havelist/', AddToHaveListView.as_view(), name='add_to_havelist'),
    # Altres URLs...
]
```

## Explicació dels enllaços d'exemple

En el nostre codi HTML, podem veure dos enllaços que utilitzen aquesta implementació:

```html
<a href="{% url 'add_to_wishlist' %}?isbn={{ book.ISBN }}&title={{ book.title|urlencode }}&author={{ book.author.name|urlencode }}" class="love-button" title="Want!">
    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-heart">
        <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path>
    </svg>
</a>

<a href="{% url 'add_to_havelist' %}?isbn={{ book.ISBN }}&title={{ book.title|urlencode }}&author={{ book.author.name|urlencode }}" class="have-button" title="I have it!">
    <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-library-big-icon">
        <rect width="8" height="18" x="3" y="3" rx="1"/>
        <path d="M7 3v18"/>
        <path d="M20.4 18.9c.2.5-.1 1.1-.6 1.3l-1.9.7c-.5.2-1.1-.1-1.3-.6L11.1 5.1c-.2-.5.1-1.1.6-1.3l1.9-.7c.5-.2 1.1.1 1.3.6Z"/>
    </svg>
</a>
```

Aquests enllaços funcionen de la següent manera:

1. **Generació de l'URL**: Utilitzem `{% url 'add_to_wishlist' %}` i `{% url 'add_to_havelist' %}` per generar les URLs correctes basades en les configuracions d'URLs.

2. **Paràmetres GET**: Afegim paràmetres a l'URL (`?isbn=...&title=...&author=...`) que contenen la informació necessària sobre el llibre.
   - Utilitzem `urlencode` per codificar correctament els valors i evitar problemes amb caràcters especials.

3. **Processament a la vista**: Quan l'usuari fa clic a un d'aquests enllaços, la petició GET s'envia a la Class-Based View corresponent:
   - La vista extreu els paràmetres de la petició GET.
   - Busca o crea el llibre a la base de dades.
   - Associa el llibre amb l'usuari en la llista corresponent.
   - Redirigeix l'usuari a la pàgina adequada.

4. **Estils i icones SVG**: Els enllaços tenen classes CSS per l'estilització i icones SVG per representar visualment les accions.

Aquest enfocament segueix les millors pràctiques de Django:
- Utilitza Class-Based Views per reduir el codi repetitiu.
- Implementa ModelForms per validació i creació d'instàncies.
- Aprofita els paràmetres GET per passar informació entre pàgines de manera neta.
- Segueix el principi DRY (Don't Repeat Yourself) reutilitzant components.


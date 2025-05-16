# Eliminació d'instàncies: El cas de les Reviews

De manera similar a la creació d'instàncies, també hem implementat una forma elegant d'eliminar elements de la base de dades, com és el cas de les reviews. El procés d'eliminació segueix un patró similar però amb algunes particularitats enfocades a garantir que només l'usuari apropiat pot eliminar el contingut i que la interfície proporciona confirmacions adequades per prevenir eliminacions accidentals.

El flux d'eliminació comença quan un usuari visualitza una ressenya que ha creat prèviament a la pàgina de detalls d'un llibre (`book-entry.html`). Per a cada ressenya de la seva autoria, el sistema mostra l'opció d'eliminació:

```html
<!-- book-entry.html -->
{% if user.is_authenticated and user.id == review.user.auth_user.id %}
    <div class="review-actions">
        <a href="{% url 'review-update' review.pk %}" class="review-edit">Edit</a>
        <a href="{% url 'review-delete' review.pk %}" class="review-delete">Delete</a>
    </div>
{% endif %}
```

Quan l'usuari fa clic en el botó "Delete", el sistema inicia una seqüència controlada per la classe `ReviewDeleteView`. Aquesta vista, configurada al fitxer `urls.py`, intercepta la petició:

```python
# urls.py
path('review/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review-delete'),
```

La vista d'eliminació hereta de tres classes fonamentals per garantir seguretat i funcionalitat adequades:
- `LoginRequiredMixin`: Assegura que només usuaris autenticats poden accedir a aquesta vista
- `UserPassesTestMixin`: Afegeix una capa de seguretat addicional verificant que l'usuari sigui l'autor de la ressenya
- `DeleteView`: Proporciona la funcionalitat bàsica per eliminar objectes del model

```python
# views.py
class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    template_name = 'review_confirm_delete.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user.auth_user
```

El mètode `test_func()` és especialment important per a la seguretat, ja que verifica que l'usuari actual és realment el propietari de la ressenya que intenta eliminar. Si aquesta comprovació falla, Django denegarà automàticament l'accés.

Quan l'usuari accedeix a aquesta vista, se li mostra una pantalla de confirmació (`review_confirm_delete.html`) que detalla quina ressenya està a punt d'eliminar i demana confirmació per procedir:

```html
<!-- review_confirm_delete.html -->
<div class="delete-confirmation">
    <h1>Delete Review</h1>
    <p>Are you sure you want to delete your review for "{{ book.title }}"?</p>
    <form method="post">
        {% csrf_token %}
        <div class="form-actions">
            <button type="submit" class="button delete-button">Delete Review</button>
            <a href="{% url 'book-entry' book.ISBN %}" class="button cancel-button">Cancel</a>
        </div>
    </form>
</div>
```

Si l'usuari confirma l'eliminació mitjançant el botó "Delete Review", s'envia una petició POST que la vista processa eliminant la ressenya de la base de dades. El sistema després redirigeix l'usuari a la pàgina de detalls del llibre, utilitzant el mètode `get_success_url()`:

```python
def get_success_url(self):
    return reverse_lazy('book-entry', kwargs={'ISBN': self.get_object().book.ISBN})
```



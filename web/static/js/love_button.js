
document.addEventListener('DOMContentLoaded', function() {
    // Seleccionem tots els botons love
    const haveButtons = document.querySelectorAll('.have-button');
    // print debug
    console.log("Botons have trobats:", haveButtons);
    // Afegim event listener a cada botó
    haveButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Obtenim les dades del llibre del botó o del contenidor pare
            const bookCard = this.closest('.book-card');
            let isbn, title, author, topic;
            
            if (bookCard.classList.contains('external-book')) {
                // Llibre extern
                isbn = bookCard.querySelector('.isbn') ? bookCard.querySelector('.isbn').textContent.replace('ISBN: ', '') : '';
                title = bookCard.querySelector('.title').textContent;
                author = bookCard.querySelector('.author').textContent.replace('by ', '');
                topic = '';
            } else {
                // Llibre local
                isbn = bookCard.querySelector('.isbn') ? bookCard.querySelector('.isbn').textContent.replace('ISBN: ', '') : '';
                title = bookCard.querySelector('h2') ? bookCard.querySelector('h2').textContent : 
                       (bookCard.querySelector('.title') ? bookCard.querySelector('.title').textContent : '');
                author = bookCard.querySelector('.author') ? bookCard.querySelector('.author').textContent.replace('by ', '') : '';
                topic = bookCard.querySelector('.category') ? bookCard.querySelector('.category').textContent : '';
            }
            
            // Construïm l'URL amb els paràmetres
            const url = `/add-to-havelist/?isbn=${encodeURIComponent(isbn)}&title=${encodeURIComponent(title)}&author=${encodeURIComponent(author)}&topic=${encodeURIComponent(topic)}`;
            
            // Redirigim a la pàgina del formulari
            window.location.href = url;
        });
    });
});


document.addEventListener('DOMContentLoaded', function() {
    // Seleccionem tots els botons love
    const loveButtons = document.querySelectorAll('.love-button');
    
    // Afegim event listener a cada botó
    loveButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();
            
            // Obtenim les dades del llibre del botó o del contenidor pare
            const bookCard = this.closest('.book-card');
            let isbn, title, author, topic;
            
            if (bookCard.classList.contains('external-book')) {
                // Llibre extern
                isbn = bookCard.querySelector('.isbn') ? bookCard.querySelector('.isbn').textContent.replace('ISBN: ', '') : '';
                title = bookCard.querySelector('.title').textContent;
                author = bookCard.querySelector('.author').textContent.replace('by ', '');
                topic = '';
            } else {
                // Llibre local
                isbn = bookCard.querySelector('.isbn') ? bookCard.querySelector('.isbn').textContent.replace('ISBN: ', '') : '';
                title = bookCard.querySelector('h2') ? bookCard.querySelector('h2').textContent : 
                       (bookCard.querySelector('.title') ? bookCard.querySelector('.title').textContent : '');
                author = bookCard.querySelector('.author') ? bookCard.querySelector('.author').textContent.replace('by ', '') : '';
                topic = bookCard.querySelector('.category') ? bookCard.querySelector('.category').textContent : '';
            }
            
            // Construïm l'URL amb els paràmetres
            const url = `/add-to-wishlist/?isbn=${encodeURIComponent(isbn)}&title=${encodeURIComponent(title)}&author=${encodeURIComponent(author)}&topic=${encodeURIComponent(topic)}`;
            
            // Redirigim a la pàgina del formulari
            window.location.href = url;
        });
    });
});

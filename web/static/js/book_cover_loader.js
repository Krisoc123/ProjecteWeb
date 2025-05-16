/**
 * Función para obtener portadas de libros desde Google Books API
 * Esta función intenta cargar la portada de un libro usando su ISBN
 * Si no encuentra resultados, carga una imagen predeterminada
 */
function fetchGoogleBooksCover(imgElement, isbn) {
    // Consultar la API para obtener el ID
    fetch(`https://www.googleapis.com/books/v1/volumes?q=isbn:${isbn}`)
        .then(response => response.json())
        .then(data => {
            if (data.items && data.items.length > 0) {
                // Obtener el ID del primer resultado
                const bookId = data.items[0].id;
                // Cambiar la URL de la imagen con el ID correcto
                imgElement.src = `https://books.google.com/books/content?id=${bookId}&printsec=frontcover&img=1&zoom=2`;
            } else {
                // No hay resultados, usar imagen predeterminada
                imgElement.src = 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png';
            }
        })
        .catch(error => {
            console.error('Error fetching Google Books data:', error);
            imgElement.src = 'https://s.gr-assets.com/assets/nophoto/book/111x148-bcc042a9c91a29c1d680899eff700a03.png';
        });
}

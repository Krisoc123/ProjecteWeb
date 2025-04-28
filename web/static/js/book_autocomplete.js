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

$(function() {
    console.log("Document ready, inicialitzant autocompletat per autors");
    
    if ($("#id_author").length) {
        console.log("Element #id_author trobat, aplicant autocompletat");
        
        $("#id_author").autocomplete({
            source: function(request, response) {
                console.log("Cercant autors amb:", request.term);
                
                $.ajax({
                    url: "https://www.googleapis.com/books/v1/volumes",
                    dataType: "json",
                    data: {
                        q: "inauthor:" + request.term,
                        maxResults: 10
                    },
                    success: function(data) {
                        console.log("Resposta rebuda:", data);
                        
                        if (!data.items) {
                            console.log("No s'han trobat resultats");
                            return response([]);
                        }
                        
                        // Recollir tots els autors únics dels resultats
                        const authors = new Set();
                        
                        $.each(data.items, function(i, item) {
                            const volume = item.volumeInfo;
                            if (volume.authors && Array.isArray(volume.authors)) {
                                volume.authors.forEach(function(author) {
                                    authors.add(author);
                                });
                            }
                        });
                        
                        // Convertir a format per autocomplete
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
    } else {
        console.log("ERROR: No s'ha trobat l'element #id_author!");
    }
});
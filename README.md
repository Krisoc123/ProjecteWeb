# ProjecteWeb

 # Descargar la portada usando curl con la opción -L para seguir redirecciones
curl -L -o portada.jpg "https://covers.openlibrary.org/b/isbn/9780747532743-L.jpg"


curl -L -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" -o portada.jpg "https://books.google.com/books/content?id=ISBN:9780747532743&printsec=frontcover&img=1&zoom=2"



sqlitebrowser ~/university/web_project/our_project/ProjecteWeb/db.sqlite3

### add book register (manual sql)

INSERT INTO web_book (ISBN, title, author, topic, publish_date, base_price) 
VALUES ('9780747532743', 'Harry Potter i la Pedra Filosofal', 'J.K. Rowling', 'Fantasia', '1997-06-26', 500);
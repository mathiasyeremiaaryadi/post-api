Tools
=================
1. Python
2. Flask
3. PostgreSQL

Cara Menjalankan Aplikasi
=============================
1. Pastikan Anda memiliki library python ```pipenv``` sebagai python dependency/package manager (seperti npm, composer)
2. Jika belum memiliki library tersebut, Anda dapat menginstall dengan command ```pip install pipenv```
3. Jika sudah menginstall library ```pipenv```, Anda dapat mengaktifkan virtual environment dengan command ```pipenv shell```
4. Setelah virtual environment diaktifkan, Anda dapat menginstall semua library yang dibutuhkan dengan command ```pipenv install``` atau jika ingin menginstall library dari file requirement.txt dengan command ```pipenv install -r path/to/requirements.txt```
5. Setelah semua library yang dibutuhkan telah tersintall, selanjutnya Anda menyetel CLI untuk Flask dengan command ```export FLASK_APP=app.py```, perlu diingat bahwa app.py merupakan aplikasi utama Anda yang menginisiasi Flask
6. Setelah itu, lakukan migration database, aplikasi ini menggunakan PostgreSQL database, ketikan command ```flask db init```, lalu ```flask db migrate```, lalu ```flask db upgrade```
7. Jika langkah sebelumnya terdapat error, buka file app.py, Anda perlu menyesuaikan URI database yang Anda miliki seperti database driver, username, port, dan password, dapat lihat disini https://flask-sqlalchemy.palletsprojects.com/en/2.x/config/#connection-uri-format
8. Jika langkah sebelumnya tidak terdapat error, Anda dapat menjalankan aplikasi Flask di local dengan command ```flask run```
9. Ketika aplikasi Flask sudah berhasil dijalankan, Anda dapat melakukan pengujian API melalui CURL maupun PostmanAPI

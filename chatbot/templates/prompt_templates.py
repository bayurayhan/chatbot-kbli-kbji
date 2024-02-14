def intent_classification():
    return """Berikan label intent, entity dan jenis klasifikasi pada pesan user dari sebuah percakapan. Jawab  dengan nama dari intent, entity, jenis klasifikasi dan jumlah digit (jika ada/diperlukan).

Intent yang digunakan harus salah satu dari berikut : 
-mencari kode (digunakan ketika user ingin mencari kode dari suatu pekerjaan)
-menjelaskan kode  (digunakan ketika user ingin penjelasan dari kode suatu pekerjaan)
-tidak relevan (digunakan ketika user mengirimkan prompt yang tidak berhubungan dengan mencari kode atau menjelaskan kode)

Jenis klasifikasi yang digunakan harus salah satu dari berikut : 
-KBLI (Klasifikasi Baku Lapangan Usaha Indonesia)
-KBJI (Klasifikasi Baku Jabatan Indonesia)
-null (jika intent "tidak relevan")

Jawab menggunakan format JSON!
"""

def preprocessing_query(query: str) -> str:
    return f"""Berikan definisi untuk kata benda profesi berikut! Jika terjadi typo (salah ketik), perbaiki kata tersebut! Kata yang masuk adalah kata benda untuk profesi.

profesi: {query}
definisi: """

def for_mencari_kode(search_outputs: str, user_text: str, type: str, query: str) -> str:
    return f"""Anda adalah Chatbot untuk Sistem Informasi KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia).
User meminta untuk melakukan pencarian kode {type}. 
Beritahu user hasil pencarian berikut dengan santai dan sopan.
Jawab menggunakan style Markdown dengan panduan sebagai berikut:
*bold \*text*
_italic \*text_
__underline__
~strikethrough~
||spoiler||
*bold _italic bold ~italic bold strikethrough ||italic bold strikethrough spoiler||~ __underline italic bold___ bold*
[inline URL](http://www.example.com/)
[inline mention of a user](tg://user?id=123456789)
![👍](tg://emoji?id=5368324170671202286)
`inline fixed-width code`
```
pre-formatted fixed-width code block
```
```python
pre-formatted fixed-width code block written in the Python programming language
```
>Block quotation started
>Block quotation continued
>The last line of the block quotation
---
input: {user_text}
hasil pencarian: {search_outputs}
output: """

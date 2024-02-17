from ..utils import read_chat_history


def intent_classification():
    return """Berikan label intent, entity dan jenis klasifikasi pada pesan user dari sebuah percakapan. Jawab  dengan nama dari intent, entity, jenis klasifikasi dan jumlah digit (jika ada/diperlukan).

Intent yang digunakan harus salah satu dari berikut : 
- CK: mencari kode (digunakan ketika user ingin mencari kode dari suatu pekerjaan)
- JK: jelaskan kode  (digunakan ketika user ingin penjelasan dari kode suatu pekerjaan)
- TR: tidak relevan (digunakan ketika user mengirimkan prompt yang tidak berhubungan dengan mencari kode atau menjelaskan kode)

Jenis klasifikasi yang digunakan harus salah satu dari berikut : 
-KBLI (Klasifikasi Baku Lapangan Usaha Indonesia)
-KBJI (Klasifikasi Baku Jabatan Indonesia)
-null (jika intent "tidak relevan")

JIKA TIDAK DISEBUTKAN KBLI ATAU KBJI, MAKA INTERPRETASIKAN SENDIRI BERDASARKAN KONTEKS DARI INPUT!

JAWAB MENGGUNAKAN FORMAT JSON!
"""


def preprocessing_query(query: str) -> list[str]:
    return [
        f"""system: Tugas Anda adalah memberikan definisi detail dari istilah kata yang diberikan oleh user. 
Perbaiki juga jika ada typo (salah ketik).\n""",
        f"""user: Apa itu 'pedagang'?\n""",
        f"""assistant: Pedagang adalah seseorang yang melakukan kegiatan membeli dan menjual barang atau jasa dengan tujuan untuk mendapatkan keuntungan. Pedagang bisa beroperasi dalam berbagai skala, mulai dari individu yang menjalankan bisnis kecil di pasar lokal hingga perusahaan besar yang beroperasi di pasar global. Mereka dapat berdagang dengan berbagai jenis produk atau layanan, termasuk barang konsumen, barang industri, layanan keuangan, dan banyak lagi. Pedagang dapat berdagang secara fisik di tempat-tempat seperti pasar tradisional atau toko ritel, atau melalui platform online dan pasar keuangan seperti bursa saham dan pasar valuta asing. Dalam menjalankan bisnis mereka, pedagang harus memperhatikan pasar, persaingan, kebijakan peraturan, dan faktor-faktor lain yang memengaruhi keberhasilan perdagangan mereka.\n""",
        f"""user: Apa itu '{query}'?\n""",
        f"""assistant: """,
    ]


def for_mencari_kode(
    search_outputs: str, user_text: str, type: str, query: str, chat_id
) -> list[str]:
    history = read_chat_history(chat_id)
    return [
        f"""system: Anda adalah chatbot yang interaktif dan menyenangkan. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia).

User meminta untuk melakukan pencarian kode '{"KBLI 2020" if type == "kbli2020" else "KBJI 2014"}' untuk {query} dan sistem sudah melakukan pencarian di data BPS {type} dengan hasil berikut:
{search_outputs}

Jawab kepada user mengenai hal hasil pencarian tersebut. 
Jika ada intepretasi dari pencarian tersebut, jelaskan juga kepada user.
Jelaskan dengan kata-kata yang panjang.
JAWAB MENGGUNAKAN FORMAT MARKDOWN TELEGRAM!
---\n""",
        *history,
        f"""assistant: """,
    ]


def for_menjelaskan_kode(
    search_outputs: str, user_text: str, type: str, query: str, chat_id
) -> list[str]:
    history = read_chat_history(chat_id)
    return [
        f"""system: Anda adalah chatbot yang interaktif dan menyenangkan. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia).
        
User meminta untuk melakukan penjelasan kode {"KBLI 2020" if type == "kbli2020" else "KBJI 2014"} untuk kode '{query}' dan sistem sudah melakukan pencarian di data BPS {type} dengan hasil berikut:
{search_outputs}

Jawab kepada user mengenai hal hasil pencarian tersebut. 
Jika ada intepretasi dari pencarian tersebut, jelaskan juga kepada user.
Jelaskan dengan kata-kata yang panjang.
JAWAB MENGGUNAKAN FORMAT MARKDOWN!
---\n""",
        *history,
        f"""assistant: """,
    ]


def for_tidak_relevan(query: str, chat_id):
    history = read_chat_history(chat_id)
    return [
        f"""system: Anda adalah chatbot yang interaktif dan menyenangkan. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia)

Anda dapat melayani beberapa task yaitu,
- mencari kode kbli ataupun kbji (dengan memberikan informasi query yang ingin dicari).
- menjelaskan kode kbli ataupun kbji (dengan memberikan informasi kode yang ingin dicari)
- menjelaskan pengetahuan umum tentang kbli dan kbji

Jawab permintaan dari user dengan baik dan sopan.
JANGAN MEMBERI JAWABAN JIKA PERTANYAAN DI LUAR KONTEKS KBLI DAN KBJI!
---\n""",
        *history,
        f"""assistant: """,
    ]

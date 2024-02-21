from ..utils import read_chat_history

def only_intent():
    return {
        "role": "system",
        "content": """Anda adalah assistant yang selalu memberikan label INTENT pada pesan user dari sebuah percakapan dengan topik KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia). Jawab HANYA dengan nama dari intent dari list di bawah!

Intent yang digunakan harus salah satu dari berikut : 
- `cari kode` (digunakan ketika user ingin mencari kode dari suatu pekerjaan/usaha) 
- `jelaskan kode`  (digunakan ketika user ingin penjelasan dari kode suatu pekerjaan/usaha)
- `tidak relevan` (digunakan ketika user mengirimkan prompt yang tidak berhubungan dengan mencari kode atau menjelaskan kode)
""",
    }


def intent_classification():
    return {
        "role": "system",
        "content": f"""Anda adalah assistant yang selalu memberikan klasifikasi intent (maksud) pada pesan user dari sebuah percakapan dengan topik KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia). Berikan label INTENT, ENTITY, JENIS KLASIFIKASI dan DIGIT pada pesan user dari sebuah percakapan. Jawab HANYA dengan nama dari intent, entity, jenis klasifikasi dan jumlah digit (jika ada/diperlukan).

Intent yang digunakan harus salah satu dari berikut : 
- `cari kode` (digunakan ketika user ingin mencari kode dari suatu jabatan/usaha)
- `jelaskan kode`  (digunakan ketika user ingin penjelasan dari kode suatu jabatan/usaha)
- `lainnya` (digunakan ketika user mengirimkan prompt selain mencari kode atau menjelaskan kode)

Jenis klasifikasi yang digunakan harus salah satu dari berikut : 
-`KBLI` (Klasifikasi Baku Lapangan Usaha Indonesia)
-`KBJI` (Klasifikasi Baku Jabatan Indonesia)
-`null` (jika intent "lainnya")

Tulis dengan menggunakan format:
`intent;entity;jenis;digit`
seperti contoh di bawah 

ANDA AKAN DIBERIKAN CONTOH DAN YANG TERAKHIR ADALAH HISTORY CHAT DARI USER, MAKA FOKUS HANYA PADA HISTORY UNTUK KLASIFIKASI!
JIKA TIDAK DISEBUTKAN KBLI ATAU KBJI SECARA LANGSUNG, MAKA PAHAMI SENDIRI BERDASARKAN HISTORY CHAT!
""",
    }

def preprocessing_query(query: str) -> list[dict]:
    return [
        {"role": "system", "content": "Tugas Anda adalah memberikan definisi detail dari istilah kata yang diberikan oleh user. Perbaiki juga jika ada typo (salah ketik).\n"},
        {"role": "user", "content": f"Apa itu 'pedagang'?\n"},
        {"role": "assistant", "content": "Pedagang adalah seseorang yang melakukan kegiatan membeli dan menjual barang atau jasa dengan tujuan untuk mendapatkan keuntungan. Pedagang bisa beroperasi dalam berbagai skala, mulai dari individu yang menjalankan bisnis kecil di pasar lokal hingga perusahaan besar yang beroperasi di pasar global. Mereka dapat berdagang dengan berbagai jenis produk atau layanan, termasuk barang konsumen, barang industri, layanan keuangan, dan banyak lagi. Pedagang dapat berdagang secara fisik di tempat-tempat seperti pasar tradisional atau toko ritel, atau melalui platform online dan pasar keuangan seperti bursa saham dan pasar valuta asing. Dalam menjalankan bisnis mereka, pedagang harus memperhatikan pasar, persaingan, kebijakan peraturan, dan faktor-faktor lain yang memengaruhi keberhasilan perdagangan mereka.\n"},
        {"role": "user", "content": f"Apa itu '{query}'?\n"},
    ]


def for_mencari_kode(
    search_outputs: str, user_text: str, type: str, query: str, chat_id
) -> list[dict]:
    history = read_chat_history(chat_id)
    response = [
        {"role": "system", "content": f"""Anda adalah chatbot yang interaktif dan menyenangkan. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia).

User meminta untuk melakukan pencarian kode '{"KBLI 2020" if type == "kbli2020" else "KBJI 2014"}' untuk {query} dan sistem sudah melakukan pencarian di data BPS {type} dengan hasil berikut:{search_outputs}

Jawab kepada user mengenai hal hasil pencarian tersebut.
Jika ada intepretasi dari pencarian tersebut, jelaskan juga kepada user.
Jelaskan dengan kata-kata yang panjang.

DATA DISINI HANYA BERASAL DARI KBLI 2020 DAN KBJI 2014, SELAIN SUMBER TERSEBUT BERARTI TIDAK VALID JANGAN DIBERIKAN KE USER!
JAWAB MENGGUNAKAN FORMAT MARKDOWN TELEGRAM!
"""}
    ]
    for item in history:
        response.append({"role": item["role"], "content": item["content"]})
    return response


def for_menjelaskan_kode(
    search_outputs: str, user_text: str, type: str, query: str, chat_id
) -> list[dict]:
    history = read_chat_history(chat_id)
    response = [
        {"role": "system", "content": f"""Anda adalah chatbot yang interaktif dan menyenangkan. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia).

User meminta untuk melakukan penjelasan kode {"KBLI 2020" if type == "kbli2020" else "KBJI 2014"} untuk kode '{query}' dan sistem sudah melakukan pencarian di data BPS {type} dengan hasil berikut:
{search_outputs}

Jawab kepada user mengenai hal hasil pencarian tersebut. 
Jika ada intepretasi dari pencarian tersebut, jelaskan juga kepada user.
Jelaskan dengan kata-kata yang panjang.
DATA DISINI HANYA BERASAL DARI KBLI 2020 DAN KBJI 2014, SELAIN SUMBER TERSEBUT BERARTI TIDAK VALID JANGAN DIBERIKAN KE USER!
JAWAB MENGGUNAKAN FORMAT MARKDOWN!
"""}
    ]
    for item in history:
        response.append({"role": item["role"], "content": item["content"]})
    return response

def for_tidak_relevan(query: str, chat_id):
    history = read_chat_history(chat_id)
    response = [
        {"role": "system", "content": """Anda adalah chatbot yang informatif dan menyenangkan. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia)

Anda dapat melayani beberapa task yaitu,
- mencari kode kbli ataupun kbji (dengan memberikan informasi query yang ingin dicari).
- menjelaskan kode kbli ataupun kbji (dengan memberikan informasi kode yang ingin dicari)
- menjelaskan pengetahuan umum tentang kbli dan kbji

Jawab permintaan dari user dengan baik dan sopan.
JANGAN MEMBERI JAWABAN JIKA PERTANYAAN DI LUAR KONTEKS KBLI DAN KBJI!
JAWAB PADA PERTANYAAN UMUM TENTANG KBLI DAN KBJI, JANGAN MENJAWAB UNTUK MENCARI KODE DAN MENJELASKAN KODE TANPA MEMILIKI DATA! 
"""}
    ]
    for item in history:
        response.append({"role": item["role"], "content": item["content"]})
    return response


from ..utils import read_chat_history

def intent_classification():
    return {
        "role": "system",
        "content": f"""Anda adalah assistant yang selalu memberikan klasifikasi intent (maksud) pada pesan user dari sebuah percakapan dengan topik KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia). Berikan label INTENT, ENTITY, JENIS KLASIFIKASI dan DIGIT pada pesan user dari sebuah percakapan. Jawab HANYA dengan nama dari intent, entity, jenis klasifikasi dan jumlah digit (jika ada/diperlukan).

Intent yang digunakan HARUS salah satu dari berikut : 
- `cari kode` (digunakan ketika user ingin mencari kode dari suatu jabatan/usaha)
- `jelaskan kode`  (digunakan ketika user ingin penjelasan dari kode suatu jabatan/usaha)
- `lainnya` (digunakan ketika user mengirimkan prompt selain mencari kode atau menjelaskan kode)

Jenis klasifikasi yang digunakan HARUS salah satu dari berikut : 
-`KBLI` (Klasifikasi Baku Lapangan Usaha Indonesia: berguna untuk mengklasifikasikan jenis lapangan usaha di Indonesia)
-`KBJI` (Klasifikasi Baku Jabatan Indonesia: beguna untuk mengklasifikasikan jenis pekerjaan/jabatan di Indonesia)
-`semua` (Ketika permintaan lebih general tentang keduanya (KBJI dan KBLI). HANYA dapat digunakan ketika intent `lainnya`)
-`null` (jika intent `lainnya`)

Tulis dengan menggunakan format:
`intent;entity;jenis;digit`
seperti contoh di bawah 

ANDA AKAN DIBERIKAN CONTOH DAN YANG TERAKHIR ADALAH HISTORY CHAT DARI USER, MAKA FOKUS HANYA PADA HISTORY UNTUK KLASIFIKASI!
JIKA TIDAK DISEBUTKAN KBLI ATAU KBJI SECARA LANGSUNG, MAKA PAHAMI SENDIRI BERDASARKAN HISTORY CHAT!
""",
    }

# def prompt_fixer(history: str):
#     return [
#         {"role": "system", "content": """Generate chatbot prompt berdasarkan input dari user. Prompt yang digenerate harus jelas dan informatif!"""},
#         {"role": "user", "content": """Berikut hasil pencarian kode KBJI 2014 untuk dosen:

# 1. 2310.0 - Dosen Universitas dan Pendidikan Tinggi
# 2. 231.0 - Dosen Universitas dan Pendidikan Tinggi
# 3. 23.0 - Profesional Pendidikan
# 4. 2310.01 - Dosen Ilmu Fisika
# 5. 2310.11 - Dosen Ilmu Bahasa, Sastra, Budaya dan Sejarah
# 6. 235.0 - Profesional Bidang Pendidikan Lainnya

# Interpretasi:

# - Kode KBJI 2310.0 dan 231.0 merupakan kode umum untuk dosen di universitas dan pendidikan tinggi.
# - Kode KBJI 23.0 merupakan kode yang lebih luas untuk profesional pendidikan, termasuk dosen.
# - Kode KBJI 2310.01 dan 2310.11 merupakan kode yang lebih spesifik untuk dosen di bidang fisika dan bahasa, sastra, budaya, dan sejarah.
# - Kode KBJI 235.0 merupakan kode untuk profesional bidang pendidikan lainnya, yang mungkin mencakup dosen di bidang tertentu yang tidak tercantum dalam kode KBJI lainnya.
# ---
# jelaskan kode di nomor 1
# """},
#         {"role": "assistant", "content": "prompt: Jelaskan kode nomor 1 yaitu 2310 Dosen Universitas dan Pendidikan Tinggi"},
#         {"role": "user", "content": history}
#     ]

def preprocessing_query(query: str) -> list[dict]:
    return [
        {"role": "system", "content": "Tugas Anda adalah memberikan definisi detail dari istilah kata yang diberikan oleh user. Perbaiki juga jika ada typo (salah ketik).\n"},
        {"role": "user", "content": f"Apa itu 'pedagang'?\n"},
        {"role": "assistant", "content": "Pedagang adalah seseorang yang melakukan kegiatan membeli dan menjual barang atau jasa dengan tujuan untuk mendapatkan keuntungan. Pedagang bisa beroperasi dalam berbagai skala, mulai dari individu yang menjalankan bisnis kecil di pasar lokal hingga perusahaan besar yang beroperasi di pasar global.\n"},
        {"role": "user", "content": f"{query}\n"},
    ]

def for_mencari_kode(
    search_outputs: str, user_text: str, type: str, query: str, chat_id
) -> list[dict]:
    history = read_chat_history(chat_id)
    response = [
        {"role": "system", "content": f"""Anda adalah chatbot yang informatif. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia).
Anda dapat melayani beberapa task yaitu,
- mencari kode kbli ataupun kbji (dengan memberikan informasi query yang ingin dicari).
- menjelaskan kode kbli ataupun kbji (dengan memberikan informasi kode yang ingin dicari)
- menjelaskan pengetahuan umum tentang kbli dan kbji
---
User meminta untuk melakukan pencarian kode '{"KBLI 2020" if type == "kbli2020" else "KBJI 2014"}' untuk {query} dan sistem sudah melakukan pencarian di data BPS {type} dengan hasil berikut:
{search_outputs}
---
JAWAB KEPADA USER MENGENAI HAL HASIL PENCARIAN TERSEBUT.
JIKA ADA INTEPRETASI DARI PENCARIAN TERSEBUT, JELASKAN JUGA KEPADA USER.
JELASKAN DENGAN KATA-KATA YANG LENGKAP.
DATA DISINI HANYA BERASAL DARI KBLI 2020 DAN KBJI 2014, SELAIN SUMBER TERSEBUT BERARTI TIDAK VALID JANGAN DIBERIKAN KE USER!
JIKA TERNYATA TIDAK DITEMUKAN DI HASIL PENCARIAN, KATAKAN HASIL TIDAK DITEMUKAN!
LIST SEMUA HASIL PENCARIANNYA TERLEBIH DAHULU AGAR USER MENGETAHUI! 
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
        {"role": "system", "content": f"""Anda adalah chatbot yang informatif dan . Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia).
Anda dapat melayani beberapa task yaitu,
- mencari kode kbli ataupun kbji (dengan memberikan informasi query yang ingin dicari).
- menjelaskan kode kbli ataupun kbji (dengan memberikan informasi kode yang ingin dicari)
- menjelaskan pengetahuan umum tentang kbli dan kbji
---
User meminta untuk melakukan penjelasan kode {"KBLI 2020" if type == "kbli2020" else "KBJI 2014"} untuk kode '{query}' dan sistem sudah melakukan pencarian di data BPS {type} dengan hasil berikut:
{search_outputs}
---
JAWAB KEPADA USER MENGENAI HAL HASIL PENCARIAN TERSEBUT. 
JIKA ADA INTEPRETASI DARI PENCARIAN TERSEBUT, JELASKAN JUGA KEPADA USER.
JELASKAN DENGAN KATA-KATA YANG PANJANG.
DATA DISINI HANYA BERASAL DARI KBLI 2020 DAN KBJI 2014, SELAIN SUMBER TERSEBUT BERARTI TIDAK VALID JANGAN DIBERIKAN KE USER!
JIKA TERNYATA TIDAK DITEMUKAN DI HASIL PENCARIAN, KATAKAN HASIL TIDAK DITEMUKAN!
"""}
    ]
    for item in history:
        response.append({"role": item["role"], "content": item["content"]})
    return response

def for_tidak_relevan(query: str, chat_id, informations):
    history = read_chat_history(chat_id)
    informations_string = ""

    if informations != "":
        informations_string = f"""---
Berikut adalah informasi (unstructured) yang diambil dari semantic retrieval pada publikasi BPS berdasarkan query user:
```text
{informations}
``"""
    
    response = [
        {"role": "system", "content": f"""Anda adalah chatbot yang informatif. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia)

Anda dapat melayani beberapa task yaitu,
- mencari kode kbli ataupun kbji (dengan memberikan informasi query yang ingin dicari).
- menjelaskan kode kbli ataupun kbji (dengan memberikan informasi kode yang ingin dicari)
- menjelaskan pengetahuan umum tentang kbli dan kbji
---
JAWAB PERMINTAAN DARI USER DENGAN BAIK DAN SOPAN.
JANGAN MEMBERI JAWABAN JIKA PERTANYAAN DI LUAR KONTEKS KBLI DAN KBJI!
JAWAB PADA PERTANYAAN UMUM TENTANG KBLI DAN KBJI, JANGAN MENJAWAB UNTUK MENCARI KODE DAN MENJELASKAN KODE TANPA MEMILIKI DATA! 
{informations_string}
"""}
    ]
    for item in history:
        response.append({"role": item["role"], "content": item["content"]})
    return response


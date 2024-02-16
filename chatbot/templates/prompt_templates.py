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


def preprocessing_query(query: str) -> list[str]:
    return [
        f"""system: Tugas Anda adalah memberikan definisi atau arti dari istilah kata yang diberikan oleh user! Perbaiki juga jika ada typo (salah ketik)!\n""",
        f"""user: 'pedagang'\n""",
        f"""assistant: pedagang adalah orang yang mencari nafkah dengan berdagang; pedagang asongan pedagang yang menjajakan buah-buahan dan sebagainya (di dalam kendaraan umum, di perempatan jalan, dan sebagainya); pedagang besar pedagang yang berjualan secara besar-besaran (dengan modal besar); pedagang yang melakukan penyerahan barang kena pajak, bukan sebagai pedagang eceran; pedagang dorongan pedagang yang membawa dagangan dengan kereta dorong;\n""",
        f"""user: '{query}'\n""",
        f"""assistant: """,
    ]


def for_mencari_kode(
    search_outputs: str, user_text: str, type: str, query: str
) -> list[str]:
    return [
        f"""system: Anda adalah chatbot yang interaktif dan menyenangkan. Tugas Anda adalah untuk memberi informasi terkait KBLI (Klasifikasi Baku Lapangan Usaha Indonesia) dan KBJI (Klasifikasi Baku Jabatan Indonesia).
        
User meminta untuk melakukan pencarian kode '{type}' untuk '{query}' dan sistem sudah melakukan pencarian di data BPS KBLI 2020 dengan hasil berikut:
{search_outputs}

Jawab kepada user mengenai hal hasil pencarian tersebut. Jika ada intepretasi dari pencarian tersebut, jelaskan juga kepada user.
---\n""",
        # f"""user: {user_text}\n""",
        f"""assistant: """,
    ]

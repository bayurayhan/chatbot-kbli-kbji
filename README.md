## Aplikasi Chatbot dengan FastAPI dan Telegram Bot

Projek ini  membuat aplikasi chatbot menggunakan framework server FastAPI dan terintegrasi dengan Telegram sebagai antarmuka pengguna. Aplikasi ini memanfaatkan pembelajaran mesin atau API eksternal (tergantung pada implementasi Anda) untuk memberikan respon informatif terhadap pertanyaan pengguna.

### Fitur

* **Server FastAPI:** Server menangani interaksi pengguna, memproses logika chatbot menggunakan FastAPI, dan berinteraksi dengan API eksternal atau model pembelajaran mesin sesuai kebutuhan.
* **Integrasi dengan Popular LLM:** Generative LLM __Google Gemini__ dan __OpenAI Embeddings__ digunakan dalam aplikasi ini.
* **Integrasi Telegram Bot:** Pengguna berinteraksi dengan bot dengan mulus melalui antarmuka Telegram yang familier.

### Menjalankan Aplikasi

1. **Konfigurasi Telegram Bot:**
    * Buat bot Telegram menggunakan BotFather ([https://core.telegram.org/bots/tutorial](https://core.telegram.org/bots/tutorial)).
    * Dapatkan access token bot, yang akan digunakan untuk komunikasi antara aplikasi Anda dan Telegram API.

2. **Pengaturan Variabel Lingkungan:**
    * Duplikat file `.env.example` di direktori root project dan ganti namanya menjadi `.env`.
    * **Penting:** **Jangan** commit file `.env` ke version control (misalnya, Git) karena berisi informasi sensitif.
    * Edit file `.env` dan berikan nilai untuk variabel berikut:
        * `TELEGRAM_TOKEN`: Access token bot Anda yang diperoleh dari BotFather.
        * (Opsional) `SERVER_URL`: URL publik server Anda jika berjalan dalam mode server (digunakan untuk registrasi webhook).

3. **Registrasi Webhook:**
    * Jalankan `python register_webhook.py [server|local]`:
        * `server`: Gunakan opsi ini jika berjalan di server dengan IP publik dan domain untuk registrasi webhook dengan Telegram API.
        * `local`: Gunakan opsi ini untuk pengembangan lokal (public domain akan dihandle oleh Ngrok port forwarding).

4. **Menjalankan Server:**
    * Jalankan `python main.py` untuk memulai server FastAPI. Ini akan mem-boot aplikasi dan mempersiapkannya untuk menangani interaksi pengguna.

**Catatan Keamanan:**

* **Jangan** commit file `.env` yang berisi informasi sensitif seperti API key ke version control. Paparan tidak disengaja dari key ini dapat menyebabkan kerentanan keamanan.

### Catatan Tambahan

* README ini memberikan gambaran dasar. Lihat kode aplikasi untuk fungsi detail tentang bagaimana server FastAPI berinteraksi dengan Telegram dan API eksternal atau model pembelajaran mesin yang telah Anda integrasikan.

### Kontribusi

Kami menerima kontribusi! Silahkan buka pull request dengan peningkatan atau perbaikan bug untuk menyempurnakan aplikasi chatbot ini.

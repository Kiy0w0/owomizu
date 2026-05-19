# 🌊 Owomizu Update - v1.7.0

Major update hari ini! Kita mem-porting banyak fitur-fitur keren dan stabil dari repositori **Svetlana** dan **Betasense** agar Owomizu makin pintar, aman, dan efisien.

Berikut ini fitur-fitur baru yang sekarang ada di Owomizu:

### 🛡️ Smart & Safe Automation
*   **Timestamp Cooldown Sync**: Sekarang bot baca sisa waktu cooldown dari pesan OWO yang pakai Discord timestamp (`<t:UNIX:r>`). Akurasinya jadi presisi, gak cuma asal jeda hitungan detik.
*   **Auto-Open Cooldown Guards**: Kalau kamu kehabisan *crates*, bot otomatis berhenti nyoba buka selama 24 jam. Kalau *lootboxes* habis, bot nunggu 1 jam. Bot juga ngebaca pesan "resets in Xh Xm" untuk pasang *pause* otomatis tanpa ngespam API.
*   **Inventory-Aware Gem Cache**: *Goodbye API spam!* Bot sekarang punya sistem *cache* yang nyatet gems apa aja yang lagi aktif. Jadi bot gak akan selalu ngetik `owo inv` di tiap tangkapan hunt kecuali memang butuh gems baru.
*   **Giveaway Deduplication**: Kesal bot kamu suka double-join giveaway kalau direstart? Sekarang bot nyimpen ID pesan giveaway ke file lokal. Kalau kamu restart, bot juga bakal *scan* chat ke belakang buat nyari giveaway yang mungkin kelewatan pas bot lagi mati.

### 🎰 Better Gambling System
*   **Slots & Coinflip Logic Fixes**: Sudah dibereskan berbagai *bug* cek saldo dan *goal system*. Format logic-nya juga disamakan dan dibersihkan dari komentar-komentar jadul. 

### 📊 Tracking & Security
*   **Session History Tracker**: Kita nambahin sistem *database* SQLite super cepat yang ngerekam statistik tiap sesi bot kamu jalan (jumlah hunt, battle, command, captcha) beserta rekaman jumlah uang (*cash snapshots*).
*   **Security & Ban Detection (Advanced)**: Keamanan ekstra! Bot sekarang mendeteksi pola teks aneh/tersembunyi dari OWO (lewat unicode normalization) buat ngenalin tanda-tanda "ban" atau peringatan *captcha*. Bakal otomatis berenti dan ngasih notifikasi ke webhook kamu!

Udah di-*test* lewat Automated Testing (TDD) dan 42 dari 42 test lolos dengan mulus, jadi stabilitasnya terjamin!

---

### 🎁 Premium Beta Benefits ($1 - $10 Value)
Khusus untuk pengguna versi **Beta**, kalian mendapatkan benefit eksklusif yang biasanya hanya ada di bot berbayar/premium:
1. **Zero Command Spam (Worth $3)**: Hemat kuota & rate-limit aman berkat fitur Gem Cache pintar. Gak perlu lagi bolak-balik manggil `/inventory` yang bikin akun dicurigai Discord.
2. **Advanced Antiban & Webhook Alert (Worth $5)**: Perlindungan otomatis dari ban manual admin OwO menggunakan pendeteksian pola unicode teks. Ditambah notifikasi real-time langsung ke Discord Server kamu pas ada captcha.
3. **Database Tracker Integration (Worth $2)**: Monitoring performa farming harian kamu secara rapi langsung tersimpan di SQLite lokal.

---
*Mizu Network*

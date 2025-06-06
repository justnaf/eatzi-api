# 🥗 Eatzi API

API berbasis Flask untuk klasifikasi bahan makanan menggunakan TensorFlow Lite dan memberikan feedback pengguna.

---

## 🚀 Fitur

* Klasifikasi gambar bahan makanan (35 kelas).
* Feedback pengguna: Like / Dislike.
* Autentikasi Basic Auth untuk semua endpoint.
* Format respons konsisten (`JSON`).

---

## 🔐 Autentikasi

Semua endpoint dilindungi dengan Basic Auth.

### Header Wajib

```
Authorization: Basic base64(username:password)
Accept: application/json
```

Contoh (menggunakan `admin:1234`):

```bash
echo -n "admin:1234" | base64
# => YWRtaW46MTIzNA==
```

```http
Authorization: Basic YWRtaW46MTIzNA==
```

---

## 🔍 POST `/predict`

Melakukan prediksi gambar bahan makanan menggunakan model TFLite.

### Request

* **Method**: `POST`
* **Headers**:

  * `Authorization`: Basic Auth
  * `Accept`: `application/json`
* **Body**: `multipart/form-data`

  * `file`: Gambar (jpg/png/jpeg)

### Contoh cURL

```bash
curl -X POST http://eatzi.snafcat.com/predict \
  -H "Authorization: Basic YWRtaW46MTIzNA==" \
  -H "Accept: application/json" \
  -F "file=@/path/to/image.jpg"
```

### Respons Sukses

```json
{
  "success": true,
  "message": "Prediction successful",
  "data": {
    "predicted_class": "Tomat",
    "confidence": 0.937,
    "raw_predictions": [0.01, 0.02, ..., 0.93]
  }
}
```

---

## ❤️ POST `/feedback`

Merekam feedback pengguna berdasarkan hasil prediksi.

### Request

* **Method**: `POST`
* **Headers**:

  * `Authorization`: Basic Auth
  * `Accept`: `application/json`
* **Body**: `application/x-www-form-urlencoded` atau `form-data`

  * `data`: `1` (Like) atau `0` (Dislike)

### Contoh cURL

```bash
curl -X POST http://eatzi.snafcat.com/feedback \
  -H "Authorization: Basic YWRtaW46MTIzNA==" \
  -H "Accept: application/json" \
  -d "data=1"
```

### Respons Sukses

```json
{
  "success": true,
  "message": "Feedback recorded successfully.",
  "data": {
    "likes": 12,
    "dislikes": 3
  }
}
```

---

## 📚 Daftar Kelas (`predicted_class`)

Berikut daftar lengkap kelas bahan makanan:

```
[
  "Bawang Bombai", "Bawang Merah", "Bawang Putih", "Brokoli", "Cabai Hijau",
  "Cabai Merah", "Daging Sapi", "Daging Unggas", "Ikan", "Jagung", "Jahe", "Jamur",
  "Kacang Hijau", "Kacang Merah", "Kacang Panjang", "Kacang Tanah", "Kembang Kol",
  "Kentang", "Kikil", "Kol", "Labu Siam", "Mie", "Nasi", "Petai", "Sawi", "Selada",
  "Seledri", "Telur Ayam", "Telur Bebek", "Tempe", "Terong", "Timun", "Tomat", "Usus", "Wortel"
]
```

---

## 📄 Lisensi

MIT License – bebas digunakan untuk keperluan riset dan pengembangan.

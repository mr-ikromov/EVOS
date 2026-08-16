# 🍔 Food Delivery Telegram Bot

Ushbu loyiha taomlar (fast-food) buyurtma berish uchun mo'ljallangan, foydalanuvchilar uchun qulay va tezkor Telegram botidir. Bot **Aiogram 3.x** kutubxonasi yordamida yozilgan bo'lib, to'liq asinxron (`async/await`) arxitekturada ishlaydi. Foydalanuvchilarga mahsulotlarni ko'rish, savatchaga qo'shish, geolokatsiya va kontakt yuborish orqali tez va oson buyurtma berish imkoniyatini beradi.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Aiogram](https://img.shields.io/badge/Aiogram-3.x-green?logo=telegram)
![Aiohttp](https://img.shields.io/badge/Aiohttp-Asynchronous-orange)

---

## ✨ Asosiy Imkoniyatlar

- 🌐 **Ikki tilli interfeys:** Foydalanuvchilar O'zbekcha va Ruscha tillarni tanlash imkoniyatiga ega. Barcha menyu, mahsulotlar va bildirishnomalar tanlangan tilda chiqadi.
- 🍽 **Mahsulotlar Katalogi:** Kategoriyalar bo'yicha saralash, har bir mahsulotning rasm, narx va tavsifi bilan to'liq tanisheish.
- 🛒 **Aqlli Savatcha (Shop Cart):** Mahsulot miqdorini interaktiv tugmalar yordamida oshirish (`+`) yoki kamaytirish (`-`). Savatni umumiy tozalash yoki muayyan mahsulotni alohida o'chirish imkoniyati.
- 📍 **Geolokatsiya va Manzilni Aniqlash:** Foydalanuvchi o'z lokatsiyasini yuborganida, bot `OpenStreetMap (Nominatim)` API dan foydalanib, koordinatalarni to'liq manzilga (shahar, ko'chaga) aylantiradi.
- 📞 **Tezkor Kontakt:** Foydalanuvchidan telefon raqamni qo'lda kiritishni talab qilmasdan, bir tugma orqali kontakt yuborishni so'raydi.
- 📦 **Buyurtmalar Tarixi:** Foydalanuvchi o'zining barcha oldingi buyurtmalarini, ularning holatini (Yangi, Qabul qilingan, Rad etilgan) va yetkazib berish vaqtini ko'rishi mumkin.
- ✍️ **Fikr Bildirish (Feedback):** Foydalanuvchilarning xizmat sifatiga bo'lgan izohlarini qabul qilish va backend'ga yuborish.
- 🔄 **Kuchli Backend Integratsiyasi:** Barcha ma'lumotlar (mahsulotlar, savatcha, buyurtmalar) REST API orqali backend bilan real vaqtda sinxronlashadi.

---

## 🛠 Texnologiyalar

Loyiha quyidagi zamonaviy asinxron texnologiyalardan foydalanilgan holda qurilgan:

- **Python 3.10+**
- **Aiogram 3.x:** Telegram Bot API bilan ishlash uchun zamonaviy va tezkor framework. FSM (Finite State Machine) yordamida foydalanuvchi holatini boshqarish.
- **Aiohttp:** Backend serveriga asinxron HTTP so'rovlarni yuborish uchun.
- **Nominatim API (OpenStreetMap):** Reverse geocoding, ya'ni koordinatalarni manzil matniga aylantirish uchun.

---

## 📋 Bot Komandalari

Bot ichida quyidagi asosiy komandalar va menyu tugmalari mavjud:

| Komanda | Tugma (UZ) | Tavsif |
|:---:|:---:|:---|
| `/start` | 🍽 Menyu | Botni ishga tushirish va tilni tanlash (birinchi marta) |
| `/category` | 🍽 Menyu | Mahsulotlar kategoriyalarini ochish |
| `/shopcart` | 📥 Savat | Savatchadaagi tanlangan mahsulotlarni va umumiy narxni ko'rish |
| `/my_order` | 🛍 Buyurtmalarim | Foydalanuvchining barcha buyurtmalari tarixini ko'rish |
| `/comment` | ✍️ Fikr bildirish | Bot yoki xizmat haqida izoh qoldirish |
| `/language` | ⚙️ Sozlamalar | Bot interfeysi tilini o'zgartirish |

---

## ⚙️ Ishlash Algoritmi (Workflow)

1. Foydalanuvchi botni `/start` bosganda tilni tanlaydi (FSM orqali saqlanadi) va asosiy menyu ochiladi.
2. Menyudan kategoriyani tanlaydi, so'ngra uchgan mahsulot rasmi va tavsifi chiqadi.
3. "Xarid qilish" tugmasi bosilganda, mahsulot miqdorini tanlash uchun interaktiv `+` va `-` tugmalar ishlaydi.
4. Mahsulot savatga qo'shiladi va backend'ga `POST` so'rovi bilan yuboriladi.
5. Foydalanuvchi savatchaga kirib, buyurtma berishni boshlaydi:
   - Avval telefon raqamni yuboradi (Contact).
   - Keyin o'z manzilini yuboradi (Location).
6. Bot lokatsiyani OpenStreetMap API ga yuborib, aniq manzilni oladi va buyurtma ma'lumotlari (mahsulotlar, miqdor, telefon, manzil) backend'ga buyurtma sifatida saqlanadi.
7. Buyurtma muvaffaqiyatli rasmiylashtirilgach, savatcha tozalanadi va foydalanuvchiga tabriklovchi xabar yuboriladi.

---

# MedAI — O'rnatish va Ishlatish

## Loyiha tuzilmasi
```
medai/
├── app.py              ← Flask server (ishga tushirish)
├── train.py            ← Modelni o'rgatish
├── requirements.txt
├── model/
│   └── blood_group_model.pth   ← (train.py dan keyin yaratiladi)
├── dataset/
│   ├── A+/
│   ├── A-/
│   ├── B+/
│   ├── B-/
│   ├── AB+/
│   ├── AB-/
│   ├── O+/
│   └── O-/
├── static/uploads/
└── templates/
    └── index.html
```

## 1. O'rnatish
```bash
pip install -r requirements.txt
```

## 2. Dataset joylash
- DATASET alohida yuklanib va proyekt papkasiga joylashtirilishi kerak
`dataset/` papkasini oching va har qon guruhi uchun rasmlarni joylang:
- dataset/A+/  →  A+ rasmlar
- dataset/A-/  →  A- rasmlar
- ... va hokazo

## 3. Modelni o'rgatish
```bash
python train.py
```
~20-30 daqiqa (CPU), ~5 daqiqa (GPU)

## 4. Serverni ishga tushirish
```bash
python app.py
```
Keyin brauzerda: http://127.0.0.1:5000






Sun'iy intellekt yordamida barmoq izi, MRI, X-ray va ko'z parda rasmlari orqali kasalliklarni qon olmasdan, kimyosiz, faqat rasm orqali aniqlash platformasi.

🟢 Hozir ishlaydigan modul
ModulUsulAniqlik🩸 Qon guruhi aniqlashBarmoq izi (ZKTeco Live20R)92.5%
🔜 Kelajakda qo'shiladi
ModulUsul🧠 Miya o'smasiMRI rasmi🫁 O'pka kasalligiKo'krak X-ray👁 Ko'z parda kasalligiRetinal Fundus rasmi🖐 Teri kasalligiDermoskopik rasm💅 AnemiyaTirnoq rasmi

⚙️ Texnologiyalar
Python Flask PyTorch ResNet18 HTML/CSS/JS ZKTeco Live20R


⚠️ Muhim
MedAI tibbiy tashxis qo'ymaydi. Sun'iy intellekt dastlabki tahlil qiladi — qaror va mas'uliyat har doim mutaxassis shifokor qo'lida qoladi.

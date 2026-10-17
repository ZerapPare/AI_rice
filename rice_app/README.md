# เดโมจำแนกพันธุ์ข้าว (Streamlit)

## 1. วางไฟล์โมเดล
ดาวน์โหลด `best_resnet50_fold4.pt` จาก Google Drive แล้ววางไว้ที่
```
rice_app/models/best_resnet50_fold4.pt
```

## 2. ติดตั้ง (ครั้งแรกครั้งเดียว)
เปิดโฟลเดอร์ `rice_app` ใน VS Code แล้วเปิด Terminal (Ctrl + `)

Windows
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
Mac
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. รัน
```
streamlit run app.py
```
หน้าเว็บจะเปิดในเบราว์เซอร์เอง (http://localhost:8501)

## ไฟล์
- `app.py` หน้าเว็บ
- `model_utils.py` โหลดโมเดลและทำนาย (เตรียมภาพเหมือนตอนฝึก: Resize 256 → CenterCrop 224 → ToTensor ไม่มี Normalize)
- `samples/` รูปตัวอย่าง ใส่รูปเพิ่มได้ (.jpg / .png)

## ถ้าผลทายแปลก
ตรวจลำดับคลาสใน `model_utils.py` (ตัวแปร `CLASSES`) ให้ตรงกับ `print(full_train_ds.classes)` ในโน้ตบุ๊กที่ฝึกโมเดล

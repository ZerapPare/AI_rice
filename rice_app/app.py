from pathlib import Path

import streamlit as st
from PIL import Image

from model_utils import CLASSES, MODEL_PATH, load_model, predict

st.set_page_config(page_title="ระบบจำแนกพันธุ์ข้าว", layout="wide")

THRESHOLD = 60
RICE_INFO = {
    "arborio": ("Arborio", "อิตาลี", "เมล็ดสั้น อวบ ทรงรี"),
    "basmati": ("Basmati", "อินเดีย / ปากีสถาน", "เมล็ดยาวเรียว ปลายแหลม"),
    "ipsala": ("Ipsala", "ตุรกี", "เมล็ดใหญ่ อวบ"),
    "jasmine": ("Jasmine", "ไทย", "เมล็ดยาวเรียว ปลายมน"),
    "karacadag": ("Karacadag", "ตุรกี", "เมล็ดเล็ก สั้นป้อม"),
}
SAMPLE_DIR = Path(__file__).parent / "samples"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Prompt:wght@400;500;600&display=swap');
#MainMenu, footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}
.block-container {max-width: 1100px; padding-top: 2rem;}
.hero {background: linear-gradient(135deg, #1F5E44, #2E7D5B 55%, #5FA884); color: #fff;
       border-radius: 18px; padding: 2rem 2.2rem; margin-bottom: 1.5rem;}
.hero-title {font-family: 'Prompt', sans-serif; font-size: 2rem; font-weight: 600; line-height: 1.3;}
.hero-sub {opacity: .9; margin-top: .4rem;}
.chips {margin-top: 1.1rem; display: flex; flex-wrap: wrap; gap: .45rem;}
.chip {background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.3);
       border-radius: 999px; padding: .2rem .8rem; font-size: .85rem;}
.section {font-family: 'Prompt', sans-serif; font-size: 1.3rem; font-weight: 600; margin: 1.5rem 0 .8rem;}
.kicker {font-size: .8rem; color: #6B7C72; text-transform: uppercase; letter-spacing: .05em;}
.label {font-family: 'Prompt', sans-serif; font-size: 1.6rem; font-weight: 600; color: #1F5E44; margin: .1rem 0 .5rem;}
.badge {display: inline-block; border-radius: 999px; padding: .25rem .8rem; font-weight: 600; font-size: .9rem;}
.badge.ok {background: #E3F2EA; color: #1F5E44;}
.badge.low {background: #FFF1D6; color: #8A5A00;}
.note {background: #FFF8E8; border-left: 3px solid #E0A526; padding: .5rem .8rem;
       border-radius: 6px; font-size: .88rem; margin-top: .8rem; color: #6B4A00;}
.truth {margin-top: .8rem; font-size: .88rem; font-weight: 600;}
.truth.hit {color: #1F5E44;}
.truth.miss {color: #B3261E;}
.meta {margin-top: .9rem; font-size: .92rem;}
.desc {color: #55645B; font-size: .92rem; margin-top: .3rem;}
.bar-row {display: grid; grid-template-columns: 9rem 1fr 3.5rem; align-items: center; gap: .6rem; margin: .55rem 0;}
.bar-name {font-size: .9rem;}
.bar {background: #EDF2EE; border-radius: 999px; height: 10px; overflow: hidden;}
.bar-fill {height: 100%; border-radius: 999px; background: #B9D3C4;}
.bar-fill.top {background: #2E7D5B;}
.bar-val {font-size: .85rem; text-align: right; color: #55645B; font-variant-numeric: tabular-nums;}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_model():
    return load_model()


chips = "".join(f'<span class="chip">{RICE_INFO[c][0]}</span>' for c in CLASSES)
st.markdown(
    '<div class="hero">'
    '<div class="hero-title">จำแนกพันธุ์ข้าวจากภาพเมล็ด</div>'
    '<div class="hero-sub">กรุณาอัปโหลดภาพเมล็ดข้าวหนึ่งเมล็ดบนพื้นหลังสีดำ '
    'ระบบจะวิเคราะห์และแสดงพันธุ์ข้าวที่มีความเป็นไปได้มากที่สุด</div>'
    f'<div class="chips">{chips}</div>'
    '</div>',
    unsafe_allow_html=True,
)

if not MODEL_PATH.exists():
    st.error(f"ไม่พบไฟล์โมเดล `{MODEL_PATH.name}` กรุณาวางไฟล์ไว้ในโฟลเดอร์ "
             f"`models/{MODEL_PATH.parent.name}/` แล้วเปิดหน้านี้ใหม่อีกครั้ง")
    st.stop()
model = get_model()

tab_upload, tab_sample = st.tabs(["อัปโหลดภาพ", "ภาพตัวอย่าง"])
images: list[tuple[str, Image.Image, str | None]] = []

with tab_upload:
    files = st.file_uploader("เลือกไฟล์ภาพ (สามารถเลือกได้หลายไฟล์)", type=["jpg", "jpeg", "png"],
                             accept_multiple_files=True)
    images += [(f.name, Image.open(f), None) for f in files or []]

with tab_sample:
    samples = sorted(p.relative_to(SAMPLE_DIR).as_posix() for p in SAMPLE_DIR.rglob("*")
                     if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
    if not samples:
        st.info("ยังไม่มีภาพตัวอย่าง กรุณาเพิ่มภาพไว้ในโฟลเดอร์ `samples/<ชื่อพันธุ์>/`")
    else:
        picked = st.multiselect("เลือกภาพตัวอย่างที่ต้องการทดสอบ", samples)
        for rel in picked:
            truth = rel.split("/")[0] if "/" in rel else None
            images.append((rel, Image.open(SAMPLE_DIR / rel), truth if truth in RICE_INFO else None))

if images:
    st.markdown(f'<div class="section">ผลการจำแนก ({len(images)} ภาพ)</div>', unsafe_allow_html=True)
    with st.spinner("กำลังวิเคราะห์ภาพ..."):
        probs = predict(model, [img for _, img, _ in images])

    for (name, img, truth), p in zip(images, probs):
        top = int(p.argmax())
        conf = float(p[top]) * 100
        label, origin, desc = RICE_INFO[CLASSES[top]]
        low = conf < THRESHOLD
        note = ('<div class="note">ความมั่นใจต่ำ กรุณาใช้ภาพที่คมชัดขึ้น '
                'หรือภาพเมล็ดข้าวเดี่ยวบนพื้นหลังสีดำ</div>') if low else ""
        if truth:
            hit = truth == CLASSES[top]
            check = (f'<div class="truth {"hit" if hit else "miss"}">พันธุ์ที่ถูกต้อง: {RICE_INFO[truth][0]}'
                     f' ({"จำแนกถูกต้อง" if hit else "จำแนกไม่ถูกต้อง"})</div>')
        else:
            check = ""

        bars = "".join(
            '<div class="bar-row">'
            f'<span class="bar-name">{RICE_INFO[c][0]}</span>'
            f'<div class="bar"><div class="bar-fill{" top" if c == CLASSES[top] else ""}" style="width:{v * 100:.1f}%"></div></div>'
            f'<span class="bar-val">{v * 100:.1f}%</span>'
            '</div>'
            for c, v in sorted(zip(CLASSES, p.tolist()), key=lambda x: -x[1])
        )

        with st.container(border=True):
            col_img, col_res, col_chart = st.columns([1, 1.2, 1.5], gap="large")
            with col_img:
                st.image(img, caption=name, width="stretch")
            with col_res:
                st.markdown(
                    '<div class="kicker">พันธุ์ที่ระบบจำแนกได้</div>'
                    f'<div class="label">{label}</div>'
                    f'<span class="badge {"low" if low else "ok"}">มั่นใจ {conf:.1f}%</span>'
                    f'{note}{check}'
                    f'<div class="meta"><b>แหล่งปลูก</b> {origin}</div>'
                    f'<div class="desc">{desc}</div>',
                    unsafe_allow_html=True,
                )
            with col_chart:
                st.markdown(f'<div class="kicker">ความน่าจะเป็นของแต่ละพันธุ์</div>{bars}',
                            unsafe_allow_html=True)
else:
    st.info("กรุณาอัปโหลดภาพหรือเลือกภาพตัวอย่างเพื่อเริ่มการจำแนก")

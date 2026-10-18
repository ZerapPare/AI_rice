import base64
import random
import time
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
.cam {position: relative; background: #000; border-radius: 16px; overflow: hidden; aspect-ratio: 4 / 3;
      max-width: 560px; margin: .5rem auto 1rem; box-shadow: 0 8px 24px rgba(0,0,0,.18);}
.cam img {position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain;}
.cam-c {position: absolute; width: 28px; height: 28px; border: 3px solid rgba(255,255,255,.85);}
.cam-c.tl {top: 16px; left: 16px; border-right: none; border-bottom: none;}
.cam-c.tr {top: 16px; right: 16px; border-left: none; border-bottom: none;}
.cam-c.bl {bottom: 16px; left: 16px; border-right: none; border-top: none;}
.cam-c.br {bottom: 16px; right: 16px; border-left: none; border-top: none;}
.cam-tag {position: absolute; top: 22px; right: 56px; display: flex; align-items: center; gap: .4rem;
          color: #fff; font: 600 .75rem/1 monospace; letter-spacing: .1em;
          background: rgba(0,0,0,.45); padding: .3rem .55rem; border-radius: 4px;}
.cam-tag i {width: 8px; height: 8px; border-radius: 50%; background: #E53935; animation: cam-blink 1s infinite;}
.cam-tag.shot {color: #9FE3BF;}
.cam-hud {position: absolute; bottom: 22px; left: 56px; color: rgba(255,255,255,.7);
          font: .72rem monospace; letter-spacing: .08em;}
.cam-scan {position: absolute; left: 8%; right: 8%; height: 2px;
           background: linear-gradient(90deg, transparent, #5FE3A1, transparent);
           box-shadow: 0 0 12px #5FE3A1; animation: cam-scan 2.4s ease-in-out infinite alternate;}
.cam-flash {position: absolute; inset: 0; background: #fff; opacity: 0; animation: cam-flash .5s ease-out;}
.cam-box {position: absolute; left: 22%; right: 22%; top: 14%; bottom: 34%;
          border: 2px solid #5FE3A1; border-radius: 6px; box-shadow: 0 0 14px rgba(95,227,161,.45);
          animation: cam-pop .35s ease-out;}
.cam-box.low {border-color: #F2B544; box-shadow: 0 0 14px rgba(242,181,68,.45);}
.cam-box b {position: absolute; top: -1.6rem; left: -2px; background: #5FE3A1; color: #0B2A1C;
            font: 600 .78rem/1 monospace; padding: .3rem .5rem; border-radius: 4px 4px 4px 0; white-space: nowrap;}
.cam-box.low b {background: #F2B544; color: #3A2600;}
.cam-result {position: absolute; left: 0; right: 0; bottom: 0; padding: 2.2rem 1.3rem 1rem; color: #fff;
             background: linear-gradient(transparent, rgba(0,0,0,.88) 40%); animation: cam-up .4s ease-out;}
.cam-result .name {font-family: 'Prompt', sans-serif; font-size: 1.5rem; font-weight: 600; line-height: 1.2;}
.cam-result .sub {font-size: .82rem; opacity: .8; margin-bottom: .55rem;}
.cam-result .row {display: grid; grid-template-columns: 6.5rem 1fr 3rem; align-items: center; gap: .5rem;
                  font: .75rem monospace; margin: .2rem 0;}
.cam-result .track {height: 5px; background: rgba(255,255,255,.18); border-radius: 999px; overflow: hidden;}
.cam-result .fill {height: 100%; background: #5FE3A1;}
.cam-result .row span:last-child {text-align: right;}
@keyframes cam-pop {from {transform: scale(1.15); opacity: 0;}}
@keyframes cam-up {from {transform: translateY(20px); opacity: 0;}}
@keyframes cam-blink {50% {opacity: .2;}}
@keyframes cam-scan {from {top: 12%;} to {top: 88%;}}
@keyframes cam-flash {from {opacity: .9;} to {opacity: 0;}}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_model():
    return load_model()


def truth_of(rel: str) -> str | None:
    folder = rel.split("/")[0] if "/" in rel else None
    return folder if folder in RICE_INFO else None


def viewfinder(path: Path, probs=None) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    data = base64.b64encode(path.read_bytes()).decode()
    if probs is None:
        tag = '<span class="cam-tag"><i></i>LIVE</span>'
        fx = '<div class="cam-scan"></div><span class="cam-hud">ISO 200 · 1/60 · f/2.8</span>'
    else:
        top = int(probs.argmax())
        conf = float(probs[top]) * 100
        label = RICE_INFO[CLASSES[top]][0]
        low = " low" if conf < THRESHOLD else ""
        sub = "ความเชื่อมั่นต่ำ กรุณาลองถ่ายภาพใหม่" if low else f"แหล่งปลูก {RICE_INFO[CLASSES[top]][1]}"
        rows = "".join(
            f'<div class="row"><span>{RICE_INFO[c][0]}</span>'
            f'<div class="track"><div class="fill" style="width:{v * 100:.1f}%"></div></div>'
            f'<span>{v * 100:.1f}%</span></div>'
            for c, v in sorted(zip(CLASSES, probs.tolist()), key=lambda x: -x[1])[:3]
        )
        tag = '<span class="cam-tag shot">■ CAPTURED</span>'
        fx = (
            '<div class="cam-flash"></div>'
            f'<div class="cam-box{low}"><b>{label} {conf:.1f}%</b></div>'
            f'<div class="cam-result"><div class="name">{label}</div>'
            f'<div class="sub">{sub}</div>{rows}</div>'
        )
    return (
        '<div class="cam">'
        f'<img src="data:{mime};base64,{data}">'
        '<span class="cam-c tl"></span><span class="cam-c tr"></span>'
        '<span class="cam-c bl"></span><span class="cam-c br"></span>'
        f'{tag}{fx}'
        '</div>'
    )


def new_grain(samples: list[str]):
    others = [s for s in samples if s != st.session_state.get("cam_pick")]
    st.session_state.cam_pick = random.choice(others or samples)
    st.session_state.cam_shot = False


def toggle_shot():
    st.session_state.cam_shot = not st.session_state.get("cam_shot", False)
    st.session_state.cam_new = st.session_state.cam_shot


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

samples = sorted(p.relative_to(SAMPLE_DIR).as_posix() for p in SAMPLE_DIR.rglob("*")
                 if p.suffix.lower() in (".jpg", ".jpeg", ".png"))
tab_upload, tab_sample, tab_camera = st.tabs(["อัปโหลดภาพ", "ภาพตัวอย่าง", "กล้อง"])
images: list[tuple[str, Image.Image, str | None]] = []
cam_probs = None

with tab_upload:
    files = st.file_uploader("เลือกไฟล์ภาพ (สามารถเลือกได้หลายไฟล์)", type=["jpg", "jpeg", "png"],
                             accept_multiple_files=True)
    images += [(f.name, Image.open(f), None) for f in files or []]

with tab_sample:
    if not samples:
        st.info("ยังไม่มีภาพตัวอย่าง กรุณาเพิ่มภาพไว้ในโฟลเดอร์ `samples/<ชื่อพันธุ์>/`")
    else:
        picked = st.multiselect("เลือกภาพตัวอย่างที่ต้องการทดสอบ", samples)
        images += [(rel, Image.open(SAMPLE_DIR / rel), truth_of(rel)) for rel in picked]

with tab_camera:
    if not samples:
        st.info("ยังไม่มีภาพตัวอย่าง กรุณาเพิ่มภาพไว้ในโฟลเดอร์ `samples/<ชื่อพันธุ์>/`")
    else:
        if st.session_state.get("cam_pick") not in samples:
            new_grain(samples)
        rel = st.session_state.cam_pick
        shot = st.session_state.get("cam_shot", False)
        screen = st.empty()
        if shot:
            if st.session_state.pop("cam_new", False):
                screen.markdown(viewfinder(SAMPLE_DIR / rel), unsafe_allow_html=True)
                with st.spinner("กำลังวิเคราะห์ภาพ..."):
                    time.sleep(1)
            cam_probs = predict(model, [Image.open(SAMPLE_DIR / rel)])[0]
        screen.markdown(viewfinder(SAMPLE_DIR / rel, cam_probs), unsafe_allow_html=True)
        _, col_next, col_shot, _ = st.columns([1, 1, 1, 1])
        col_next.button("เปลี่ยนเมล็ด", on_click=new_grain, args=(samples,), width="stretch")
        col_shot.button("ถ่ายใหม่" if shot else "ถ่ายภาพ", on_click=toggle_shot,
                        type="primary", width="stretch")

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
elif cam_probs is None:
    st.info("กรุณาอัปโหลดภาพหรือเลือกภาพตัวอย่างเพื่อเริ่มการจำแนก")

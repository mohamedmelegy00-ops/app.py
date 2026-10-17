
import streamlit as st
import requests
import json
from pathlib import Path

st.set_page_config(
    page_title="حصن المسلم والقرآن الكريم",
    page_icon="📖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

API = "https://api.alquran.cloud/v1"

# القراء: تُختبر الإصدارات المتاحة من الخدمة عند التشغيل
RECITERS = [
    ("مشاري العفاسي", "ar.alafasy"),
    ("عبدالباسط عبدالصمد", "ar.abdulbasit"),
    ("عبدالرحمن السديس", "ar.abdurrahmaansudais"),
    ("محمود خليل الحصري", "ar.husary"),
    ("محمد صديق المنشاوي", "ar.minshawi"),
    ("ماهر المعيقلي", "ar.mahermuaiqly"),
    ("سعود الشريم", "ar.saoodshuraym"),
    ("أبو بكر الشاطري", "ar.shaatree"),
    ("محمد أيوب", "ar.muhammadayyoub"),
    ("محمد جبريل", "ar.muhammadjibreel"),
]

ADHKAR = [
    {
        "القسم": "أذكار الصباح والمساء",
        "النص": "سُبْحَانَ اللَّهِ وَبِحَمْدِهِ",
        "التكرار": 100
    },
    {
        "القسم": "أذكار الصباح والمساء",
        "النص": "أَسْتَغْفِرُ اللَّهَ وَأَتُوبُ إِلَيْهِ",
        "التكرار": 100
    },
    {
        "القسم": "أذكار النوم",
        "النص": "بِاسْمِكَ اللَّهُمَّ أَمُوتُ وَأَحْيَا",
        "التكرار": 1
    },
    {
        "القسم": "أذكار الاستيقاظ",
        "النص": "الْحَمْدُ لِلَّهِ الَّذِي أَحْيَانَا بَعْدَ مَا أَمَاتَنَا وَإِلَيْهِ النُّشُورُ",
        "التكرار": 1
    },
    {
        "القسم": "أذكار الصلاة",
        "النص": "أَسْتَغْفِرُ اللَّهَ",
        "التكرار": 3
    },
    {
        "القسم": "أذكار متنوعة",
        "النص": "لَا حَوْلَ وَلَا قُوَّةَ إِلَّا بِاللَّهِ",
        "التكرار": 1
    },
    {
        "القسم": "أذكار متنوعة",
        "النص": "اللَّهُمَّ صَلِّ وَسَلِّمْ عَلَى نَبِيِّنَا مُحَمَّدٍ",
        "التكرار": 10
    },
]

# تنسيق عربي وتصميم متجاوب
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Amiri:wght@400;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
}

.block-container {
    max-width: 850px;
    padding-top: 1rem;
}

.header {
    text-align: center;
    padding: 15px 0;
}

.header h1 {
    font-family: 'Amiri', serif;
    font-size: 2.2rem;
}

.ayah {
    font-family: 'Amiri', serif;
    font-size: 1.65rem;
    line-height: 2.2;
    text-align: right;
    direction: rtl;
    padding: 10px 0;
}

.dhikr {
    font-family: 'Amiri', serif;
    font-size: 1.8rem;
    line-height: 2;
    text-align: center;
    direction: rtl;
    padding: 25px 5px;
}

.watermark {
    text-align: center;
    opacity: 0.55;
    padding: 25px 0 5px;
    font-size: 13px;
}

.stButton button {
    min-height: 45px;
    border-radius: 12px;
}

@media (max-width: 600px) {
    .header h1 { font-size: 1.7rem; }
    .ayah { font-size: 1.35rem; }
    .dhikr { font-size: 1.5rem; }
}
</style>
""", unsafe_allow_html=True)

# إعدادات الجلسة
if "dark" not in st.session_state:
    st.session_state.dark = True

if "counts" not in st.session_state:
    st.session_state.counts = {}

if "dhikr_index" not in st.session_state:
    st.session_state.dhikr_index = 0

if "dhikr_category" not in st.session_state:
    st.session_state.dhikr_category = "أذكار الصباح والمساء"

# الوضع الليلي والنهاري
if st.session_state.dark:
    st.markdown("""
    <style>
    .stApp {background-color:#101916;color:#f2f4ee;}
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .stApp {background-color:#fbfaf5;color:#1c2d24;}
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="header">
<h1>📖 حصن المسلم والقرآن الكريم</h1>
<p>القرآن الكريم • الأذكار • التلاوة</p>
</div>
""", unsafe_allow_html=True)

# العلامة المائية وتغيير المظهر
c1, c2 = st.columns([3, 2])

with c1:
    watermark = st.text_input(
        "العلامة المائية",
        value="حصن المسلم",
        label_visibility="collapsed",
        placeholder="اكتب اسم العلامة المائية"
    )

with c2:
    if st.button("🌙 / ☀️ تغيير الوضع", use_container_width=True):
        st.session_state.dark = not st.session_state.dark
        st.rerun()

tab_quran, tab_adhkar, tab_about = st.tabs([
    "📖 القرآن الكريم",
    "🤲 الأذكار",
    "ℹ️ حول التطبيق"
])

# =========================
# القرآن الكريم
# =========================
with tab_quran:
    try:
        @st.cache_data(ttl=3600)
        def load_surahs():
            r = requests.get(f"{API}/surah", timeout=20)
            r.raise_for_status()
            return r.json()["data"]

        @st.cache_data(ttl=3600)
        def load_surah(number):
            r = requests.get(f"{API}/surah/{number}", timeout=20)
            r.raise_for_status()
            return r.json()["data"]

        @st.cache_data(ttl=3600)
        def load_editions():
            r = requests.get(
                f"{API}/edition/format/audio",
                timeout=20
            )
            r.raise_for_status()
            return {
                x["identifier"]
                for x in r.json()["data"]
            }

        surahs = load_surahs()

        labels = [
            f"{s['number']} - {s['name']}"
            for s in surahs
        ]

        selected = st.selectbox(
            "اختر السورة",
            labels
        )

        number = int(selected.split(" - ")[0])
        editions = load_editions()

        available = [
            (name, code)
            for name, code in RECITERS
            if code in editions
        ]

        if not available:
            available = [("مشاري العفاسي", "ar.alafasy")]

        names = [x[0] for x in available]
        reciter = st.selectbox("اختر القارئ", names)
        edition = dict(available)[reciter]

        audio_url = (
            "https://cdn.islamic.network/quran/audio-surah/"
            f"128/{edition}/{number}.mp3"
        )

        st.audio(audio_url, format="audio/mp3")

        surah = load_surah(number)

        st.subheader(f"سورة {surah['name']}")
        st.caption(
            f"عدد الآيات: {surah['numberOfAyahs']} | القارئ: {reciter}"
        )

        for ayah in surah["ayahs"]:
            st.markdown(
                f"""<div class="ayah">
                {ayah['text']}
                <span style="font-size:0.8em;opacity:0.7">
                ۞ {ayah['numberInSurah']}
                </span>
                </div>""",
                unsafe_allow_html=True
            )
            st.divider()

    except Exception:
        st.error(
            "تعذر تحميل القرآن أو قائمة القراء. "
            "تحقق من الإنترنت وحاول مرة أخرى."
        )

# =========================
# حصن المسلم والأذكار
# =========================
with tab_adhkar:
    categories = sorted({
        item["القسم"] for item in ADHKAR
    })

    category = st.selectbox(
        "اختر قسم الأذكار",
        categories
    )

    if category != st.session_state.dhikr_category:
        st.session_state.dhikr_category = category
        st.session_state.dhikr_index = 0

    items = [
        item for item in ADHKAR
        if item["القسم"] == category
    ]

    if items:
        index = min(
            st.session_state.dhikr_index,
            len(items) - 1
        )

        item = items[index]
        key = f"{category}_{index}"
        count = st.session_state.counts.get(key, 0)
        target = item["التكرار"]

        st.markdown(
            f'<div class="dhikr">{item["النص"]}</div>',
            unsafe_allow_html=True
        )

        st.caption(
            f"الذكر {index + 1} من {len(items)}"
        )

        st.progress(min(count / target, 1.0))

        st.markdown(
            f"<center>التكرار: {count} / {target}</center>",
            unsafe_allow_html=True
        )

        a, b, c = st.columns(3)

        with a:
            if st.button("➕ تكرار", use_container_width=True):
                st.session_state.counts[key] = min(
                    count + 1, target
                )
                st.rerun()

        with b:
            if st.button("إعادة العداد", use_container_width=True):
                st.session_state.counts[key] = 0
                st.rerun()

        with c:
            if st.button("الذكر التالي", use_container_width=True):
                st.session_state.dhikr_index = (
                    index + 1
                ) % len(items)
                st.rerun()

    st.info(
        "هذه مجموعة بداية وليست جميع أذكار كتاب حصن المسلم. "
        "راجع النصوص والتكرارات من طبعة موثوقة قبل نشر التطبيق."
    )

# =========================
# حول التطبيق
# =========================
with tab_about:
    st.subheader("عن التطبيق")
    st.write("""
    تطبيق عربي للقرآن الكريم والأذكار.

    المميزات:
    - عرض سور القرآن الكريم وآياتها.
    - اختيار القارئ من الإصدارات المتاحة.
    - مشغل صوت للتلاوة.
    - أذكار مع عداد تكرار.
    - وضع ليلي ونهاري.
    - علامة مائية قابلة للتعديل.
    - واجهة متجاوبة مع الهاتف والكمبيوتر.

    يتطلب الإنترنت لتحميل القرآن والتلاوات.
    """)

st.markdown(
    f'<div class="watermark">{watermark}</div>',
    unsafe_allow_html=True
)

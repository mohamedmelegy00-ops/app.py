
import html
import requests
import streamlit as st

# =========================================
# إعدادات الموقع
# =========================================
st.set_page_config(
    page_title="حصن المسلم والقرآن الكريم",
    page_icon="📖",
    layout="wide",
)

API = "https://api.alquran.cloud/v1"

ADHKAR_URL = (
    "https://raw.githubusercontent.com/"
    "sehalhussain/Hadith-Dua-assets/"
    "main/duas-adhkar-hisnul-muslim.json"
)

RECITERS = {
    "مشاري العفاسي": "ar.alafasy",
    "محمود خليل الحصري": "ar.husary",
    "محمد صديق المنشاوي": "ar.minshawi",
    "عبد الرحمن السديس": "ar.abdurrahmaansudais",
    "ماهر المعيقلي": "ar.mahermuaiqly",
    "أحمد العجمي": "ar.ahmedajamy",
    "أبو بكر الشاطري": "ar.shaatree",
    "علي الحذيفي": "ar.hudhaify",
    "محمد أيوب": "ar.muhammadayyoub",
    "سعود الشريم": "ar.saoodshuraym",
}

# تعريف الروايات قبل استخدامها
RIWAYAT = {
    "حفص عن عاصم": {
        "reader": "عاصم الكوفي",
        "status": "النص الأساسي متاح من مصدر القرآن الحالي.",
    },
    "ورش عن نافع": {
        "reader": "نافع المدني",
        "status": (
            "يلزم ربط مصدر موثوق لنص ورش وتلاوتها."
        ),
    },
}

QIRAAT = {
    "نافع المدني": ["قالون عن نافع", "ورش عن نافع"],
    "ابن كثير المكي": ["البزي عن ابن كثير", "قنبل عن ابن كثير"],
    "أبو عمرو البصري": ["الدوري عن أبي عمرو", "السوسي عن أبي عمرو"],
    "ابن عامر الشامي": ["هشام عن ابن عامر", "ابن ذكوان عن ابن عامر"],
    "عاصم الكوفي": ["شعبة عن عاصم", "حفص عن عاصم"],
    "حمزة الكوفي": ["خلف عن حمزة", "خلاد عن حمزة"],
    "الكسائي الكوفي": ["أبو الحارث عن الكسائي", "الدوري عن الكسائي"],
    "أبو جعفر المدني": ["ابن وردان عن أبي جعفر", "ابن جماز عن أبي جعفر"],
    "يعقوب الحضرمي": ["رويس عن يعقوب", "روح عن يعقوب"],
    "خلف العاشر": ["إسحاق عن خلف", "إدريس عن خلف"],
}


# =========================================
# تحميل البيانات
# =========================================
def fetch_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    if isinstance(data, dict) and data.get("code", 200) != 200:
        raise ValueError("مصدر البيانات أعاد خطأ.")

    return data


@st.cache_data(ttl=3600, show_spinner=False)
def load_surahs():
    return fetch_json(f"{API}/surah")["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_surah_text(number):
    return fetch_json(
        f"{API}/surah/{number}/quran-uthmani"
    )["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_surah_audio(number, edition):
    return fetch_json(
        f"{API}/surah/{number}/{edition}"
    )["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_adhkar():
    data = fetch_json(ADHKAR_URL)
    items = []

    for segment in data.get("segments", []):
        segment_name = segment.get(
            "segment_name", "أذكار متنوعة"
        )

        for category in segment.get("categories", []):
            category_name = category.get(
                "category_name", segment_name
            )

            for title in category.get("titles", []):
                title_name = title.get(
                    "title_name", category_name
                )

                for dua in title.get("duas", []):
                    arabic = str(
                        dua.get("arabic", "")
                    ).strip()

                    if not arabic:
                        continue

                    items.append({
                        "category": category_name,
                        "title": title_name,
                        "text": arabic,
                        "source": str(dua.get("source", "")),
                        "translation": str(
                            dua.get("translation", "")
                        ),
                        "latin": str(dua.get("latin", "")),
                    })

    return items


# =========================================
# التصميم
# =========================================
def apply_styles(dark):
    if dark:
        bg = "#101827"
        card = "#1f2937"
        fg = "#f9fafb"
        muted = "#cbd5e1"
        accent = "#059669"
        border = "#374151"
    else:
        bg = "#f8fafc"
        card = "#ffffff"
        fg = "#172033"
        muted = "#475569"
        accent = "#047857"
        border = "#dbe3ed"

    st.markdown(
        f"""
        <style>
        @import url(
          'https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap'
        );

        .stApp {{
            background: {bg};
            color: {fg};
        }}

        [data-testid="stSidebar"] {{
            background: {card};
        }}

        .block-container {{
            max-width: 1150px;
            padding: 1rem 1rem 3rem;
        }}

        h1, h2, h3, p, label {{
            color: {fg};
        }}

        .hero {{
            background: {card};
            border: 1px solid {border};
            border-radius: 24px;
            text-align: center;
            padding: 20px 12px;
            margin-bottom: 18px;
        }}

        .hero h1 {{
            color: {accent};
            font-family: 'Amiri', serif;
            font-size: clamp(27px, 5vw, 42px);
        }}

        .hero p {{
            color: {muted};
        }}

        /* أزرار الأقسام مستديرة */
        div[role="radiogroup"] {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 9px;
        }}

        div[role="radiogroup"] label {{
            border: 1px solid {border};
            border-radius: 999px !important;
            background: {card};
            padding: 10px 15px !important;
            margin: 0 !important;
        }}

        div[role="radiogroup"] label:has(input:checked) {{
            background: {accent};
            border-color: {accent};
        }}

        div.stButton > button {{
            border-radius: 999px !important;
            min-height: 44px;
        }}

        .arabic {{
            font-family: 'Amiri', serif;
            font-size: clamp(23px, 4vw, 31px);
            line-height: 2;
            direction: rtl;
            text-align: right;
            color: {fg};
            overflow-wrap: anywhere;
        }}

        .watermark {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            z-index: 999;
            pointer-events: none;
            user-select: none;
            text-align: center;
            color: {accent};
            opacity: 0.14;
            font-family: Arial, sans-serif;
            font-weight: 900;
            white-space: nowrap;
            font-size: clamp(23px, 5vw, 52px);
        }}

        .watermark .star {{
            font-size: 1.5em;
            line-height: 1.1;
        }}

        .footer {{
            text-align: center;
            color: {muted};
            border-top: 1px solid {border};
            margin-top: 30px;
            padding: 20px 5px;
        }}

        @media(max-width: 600px) {{
            .block-container {{
                padding-left: 10px;
                padding-right: 10px;
            }}

            div[role="radiogroup"] label {{
                padding: 8px 12px !important;
            }}

            .watermark {{
                font-size: 23px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================
# الشريط الجانبي والوضع الليلي
# =========================================
with st.sidebar:
    st.markdown("## 📖 حصن المسلم")
    dark_mode = st.toggle("🌙 الوضع الليلي", value=False)

apply_styles(dark_mode)


# =========================================
# العلامة المائية
# =========================================
st.markdown(
    """
    <div class="watermark">
        <div class="star">★</div>
        <div>OMAR MELIGY</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================
# رأس الموقع
# =========================================
st.markdown(
    """
    <div class="hero">
        <h1>حصن المسلم والقرآن الكريم</h1>
        <p>القرآن الكريم • الأذكار • القراءات • البحث</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================
# أزرار التنقل
# =========================================
sections = [
    "📗 القرآن الكريم",
    "🤲 الأذكار",
    "📚 القراءات",
    "🔎 البحث",
]

section = st.radio(
    "اختر القسم",
    sections,
    horizontal=True,
    label_visibility="collapsed",
    key="main_section",
)

st.divider()


# =========================================
# القرآن الكريم
# =========================================
if section == "📗 القرآن الكريم":
    st.subheader("📗 القرآن الكريم")

    try:
        surahs = load_surahs()

        options = {
            f"{s['number']} - {s['name']}": s["number"]
            for s in surahs
        }

        label = st.selectbox("اختر السورة", list(options.keys()))
        number = options[label]

        reciter = st.selectbox(
            "اختر القارئ",
            list(RECITERS.keys()),
        )

        quran = load_surah_text(number)

        try:
            audio = load_surah_audio(
                number,
                RECITERS[reciter],
            )

            audio_ayahs = audio.get("ayahs", [])

            if audio_ayahs and audio_ayahs[0].get("audio"):
                st.markdown(f"**تلاوة {label} — {reciter}**")
                st.audio(audio_ayahs[0]["audio"])

        except Exception:
            st.warning(
                "تعذر تحميل الصوت المختار حاليًا، "
                "لكن يمكنك قراءة نص السورة."
            )

        st.markdown("### نص السورة")

        for ayah in quran.get("ayahs", []):
            text = html.escape(str(ayah.get("text", "")))
            num = ayah.get("numberInSurah", "")

            st.markdown(
                f'<div class="arabic">{text} ﴿{num}﴾</div>',
                unsafe_allow_html=True,
            )

    except Exception as error:
        st.error("تعذر تحميل القرآن. تحقق من الإنترنت.")
        st.caption(str(error))


# =========================================
# الأذكار
# =========================================
elif section == "🤲 الأذكار":
    st.subheader("🤲 حصن المسلم — الأذكار")

    try:
        with st.spinner("جارٍ تحميل الأذكار..."):
            adhkar = load_adhkar()

        if not adhkar:
            st.warning("لم يتم العثور على أذكار.")
        else:
            st.success(f"عدد النصوص المحمّلة: {len(adhkar)}")

            categories = sorted({
                item["category"] for item in adhkar
            })

            category = st.selectbox(
                "اختر قسم الأذكار",
                ["كل الأقسام"] + categories,
            )

            filtered = adhkar

            if category != "كل الأقسام":
                filtered = [
                    item for item in adhkar
                    if item["category"] == category
                ]

            for index, item in enumerate(filtered):
                with st.container(border=True):
                    st.markdown(f"### {item['title']}")

                    st.markdown(
                        '<div class="arabic">'
                        + html.escape(item["text"])
                        + '</div>',
                        unsafe_allow_html=True,
                    )

                    if item["source"]:
                        st.caption("المصدر: " + item["source"])

                    with st.expander("تفاصيل الذكر"):
                        if item["translation"]:
                            st.write(item["translation"])

                        if item["latin"]:
                            st.write(item["latin"])

                        st.code(item["text"])

    except Exception:
        st.error(
            "تعذر تحميل الأذكار. تحقق من اتصال الإنترنت "
            "أو من عنوان المصدر."
        )


# =========================================
# القراءات والروايات
# =========================================
elif section == "📚 القراءات":
    st.subheader("📚 القراءات العشر والروايات")

    selected_riwayah = st.selectbox(
        "اختر الرواية",
        list(RIWAYAT.keys()),
    )

    details = RIWAYAT[selected_riwayah]

    st.markdown("### اختيارك")
    st.write("القارئ: " + details["reader"])
    st.write("الرواية: " + selected_riwayah)

    if selected_riwayah == "حفص عن عاصم":
        st.success(details["status"])
    else:
        st.warning(details["status"])

    st.divider()
    st.markdown("### القراءات العشر")

    selected_reader = st.selectbox(
        "اختر القارئ",
        list(QIRAAT.keys()),
    )

    selected_narration = st.selectbox(
        "اختر الرواية التابعة له",
        QIRAAT[selected_reader],
    )

    st.info(
        f"اختيارك: {selected_reader} — {selected_narration}"
    )

    st.warning(
        "القوائم تعرض أسماء القراءات والروايات، "
        "لكنها لا تغيّر نص القرآن تلقائيًا. "
        "يلزم ربط مصدر موثوق لكل نص وتلاوة."
    )


# =========================================
# البحث
# =========================================
elif section == "🔎 البحث":
    st.subheader("🔎 البحث في الأذكار")

    query = st.text_input(
        "اكتب كلمة للبحث",
        placeholder="مثال: الصباح أو النوم أو سبحان الله",
    )

    if query.strip():
        try:
            adhkar = load_adhkar()
            term = query.strip()

            results = [
                item for item in adhkar
                if term in item["text"]
                or term in item["title"]
                or term in item["category"]
                or term in item["source"]
            ]

            st.write(f"عدد النتائج: {len(results)}")

            for item in results:
                with st.container(border=True):
                    st.markdown(f"### {item['title']}")

                    st.markdown(
                        '<div class="arabic">'
                        + html.escape(item["text"])
                        + '</div>',
                        unsafe_allow_html=True,
                    )

                    st.caption("القسم: " + item["category"])

        except Exception:
            st.error("تعذر تحميل بيانات البحث.")


# =========================================
# تذييل الموقع
# =========================================
st.markdown(
    """
    <div class="footer">
        حصن المسلم والقرآن الكريم
        <br>
        صدقة جارية بإذن الله
        <br>
        ⭐ OMAR MELIGY
    </div>
    """,
    unsafe_allow_html=True,
                           )
                                     

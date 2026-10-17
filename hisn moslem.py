
import html
import requests
import streamlit as st

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


# ------------------------------------------
# تحميل البيانات
# ------------------------------------------
def fetch_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3600, show_spinner=False)
def load_surahs():
    return fetch_json(f"{API}/surah")["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_quran_surah(number):
    return fetch_json(
        f"{API}/surah/{number}/quran-uthmani"
    )["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_audio_surah(number, edition):
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
                    text = str(
                        dua.get("arabic", "")
                    ).strip()

                    if text:
                        items.append({
                            "category": category_name,
                            "title": title_name,
                            "text": text,
                            "source": str(
                                dua.get("source", "")
                            ),
                            "translation": str(
                                dua.get("translation", "")
                            ),
                            "latin": str(
                                dua.get("latin", "")
                            ),
                        })

    return items


# ------------------------------------------
# التصميم والأزرار المستديرة
# ------------------------------------------
def set_styles(dark):
    if dark:
        bg = "#101827"
        card = "#1f2937"
        fg = "#f9fafb"
        muted = "#cbd5e1"
        accent = "#34d399"
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

        /* أزرار الأقسام بشكل مستدير */
        div[role="radiogroup"] {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 9px;
            background: transparent;
        }}

        div[role="radiogroup"] label {{
            border: 1px solid {border};
            border-radius: 999px !important;
            background: {card};
            padding: 10px 16px !important;
            min-height: 42px;
            margin: 0 !important;
            transition: 0.2s;
        }}

        div[role="radiogroup"] label:has(input:checked) {{
            background: {accent};
            border-color: {accent};
            color: white;
        }}

        div[role="radiogroup"] label p {{
            margin: 0;
            font-weight: 600;
        }}

        /* بقية الأزرار */
        div.stButton > button,
        div.stDownloadButton > button {{
            border-radius: 999px !important;
            min-height: 44px;
            border: 1px solid {border};
            transition: 0.2s;
        }}

        div.stButton > button:hover {{
            border-color: {accent};
            color: {accent};
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 18px;
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


# ------------------------------------------
# الشريط الجانبي
# ------------------------------------------
with st.sidebar:
    st.markdown("## 📖 حصن المسلم")

    dark_mode = st.toggle(
        "🌙 الوضع الليلي",
        value=False,
    )

set_styles(dark_mode)

# ------------------------------------------
# العلامة المائية
# ------------------------------------------
st.markdown(
    """
    <div class="watermark">
        <div class="star">★</div>
        <div>OMAR MELIGY</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------
# رأس الموقع
# ------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>حصن المسلم والقرآن الكريم</h1>
        <p>اقرأ القرآن، واستمع للتلاوة، وتصفّح الأذكار</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------
# أزرار التنقل المستديرة
# ------------------------------------------
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

# ------------------------------------------
# قسم القرآن الكريم
# ------------------------------------------
if section == "📗 القرآن الكريم":
    st.subheader("📗 القرآن الكريم")

    try:
        surahs = load_surahs()

        surah_options = {
            f"{s['number']} - {s['name']}": s["number"]
            for s in surahs
        }

        selected_surah = st.selectbox(
            "اختر السورة",
            list(surah_options.keys()),
        )

        number = surah_options[selected_surah]

        reciter = st.selectbox(
            "اختر القارئ",
            list(RECITERS.keys()),
        )

        text_data = load_quran_surah(number)

        try:
            audio_data = load_audio_surah(
                number,
                RECITERS[reciter],
            )
        except Exception:
            audio_data = None
            st.warning(
                "تعذر تحميل صوت هذا القارئ حاليًا."
            )

        if audio_data:
            audio_ayahs = audio_data.get("ayahs", [])

            if audio_ayahs:
                st.markdown(f"**تلاوة سورة {selected_surah}**")

                first_audio = audio_ayahs[0].get("audio")
                if first_audio:
                    st.audio(first_audio)

        st.markdown("### نص السورة")

        for ayah in text_data.get("ayahs", []):
            ayah_text = html.escape(
                str(ayah.get("text", ""))
            )
            ayah_number = ayah.get("numberInSurah", "")

            st.markdown(
                f'<div class="arabic">'
                f'{ayah_text} '
                f'<span>﴿{ayah_number}﴾</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    except Exception as error:
        st.error(
            "تعذر تحميل القرآن. تأكد من الإنترنت."
        )
        st.caption(str(error))


# ------------------------------------------
# قسم الأذكار
# ------------------------------------------
elif section == "🤲 الأذكار":
    st.subheader("🤲 حصن المسلم")

    try:
        with st.spinner("جارٍ تحميل الأذكار..."):
            adhkar = load_adhkar()

        if not adhkar:
            st.warning("لم يتم العثور على الأذكار.")
        else:
            st.success(
                f"تم تحميل {len(adhkar)} نصًا من المصدر."
            )

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
                        st.caption(
                            "المصدر: " + item["source"]
                        )

                    with st.expander("تفاصيل الذكر"):
                        if item["translation"]:
                            st.write(item["translation"])

                        if item["latin"]:
                            st.write(item["latin"])

                        st.code(item["text"])

    except Exception:
        st.error(
            "تعذر تحميل الأذكار. تحقق من اتصال الإنترنت."
        )


# ------------------------------------------
# قسم القراءات والروايات
# ------------------------------------------
elif section == "📚 القراءات":
    st.subheader("📚 القراءات والروايات")

    riwayah = st.selectbox(
        "اختر الرواية",
        list(RIWAYAT.keys()),
    )

    if riwayah == "حفص عن عاصم":
        st.success(RIWAYAT[riwayah])
        st.info(
            "النص المعروض في قسم القرآن هو النص الأساسي "
            "من مصدر القرآن المستخدم. تحقق من بيانات "
            "المصدر قبل اعتماد طبعة محددة."
        )
    else:
        st.warning(RIWAYAT[riwayah])

    st.markdown("### القراءات العشر")

    readers = [
        "نافع المدني",
        "ابن كثير المكي",
        "أبو عمرو البصري",
        "ابن عامر الشامي",
        "عاصم الكوفي",
        "حمزة الكوفي",
        "الكسائي الكوفي",
        "أبو جعفر المدني",
        "يعقوب الحضرمي",
        "خلف العاشر",
    ]

    reader = st.selectbox(
        "اختر القارئ",
        readers,
    )

    st.write(f"القراءة المختارة: **{reader}**")

    st.info(
        "اختيار القارئ هنا لا يغيّر نص القرآن تلقائيًا. "
        "يلزم ربط كل قراءة ورواية بمصدر يدعم نصها "
        "وصوتها فعلًا."
    )

# ------------------------------------------
# قسم البحث
# ------------------------------------------
elif section == "🔎 البحث":
    st.subheader("🔎 البحث في الأذكار")

    query = st.text_input(
        "اكتب كلمة للبحث",
        placeholder="مثال: الصباح أو النوم",
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

                    st.caption(item["category"])

        except Exception:
            st.error("تعذر تحميل بيانات البحث.")

# ------------------------------------------
# تذييل الموقع
# ------------------------------------------
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
                                

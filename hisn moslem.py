
import html
import requests
import streamlit as st

# ==================================================
# إعدادات الموقع
# ==================================================
st.set_page_config(
    page_title="حصن المسلم والقرآن الكريم | OMAR MELIGY",
    page_icon="📖",
    layout="wide",
)

QURAN_API = "https://api.alquran.cloud/v1"
QF_BASE = "https://apis.quran.foundation/content/api/v4"
QF_TOKEN_URL = "https://oauth2.quran.foundation/oauth2/token"

ADHKAR_URL = (
    "https://raw.githubusercontent.com/"
    "sehalhussain/Hadith-Dua-assets/"
    "main/duas-adhkar-hisnul-muslim.json"
)

RECITERS = {
    "مشاري العفاسي": "ar.alafasy",
    "عبد الرحمن السديس": "ar.abdurrahmaansudais",
    "محمود خليل الحصري": "ar.husary",
    "محمد صديق المنشاوي": "ar.minshawi",
    "أبو بكر الشاطري": "ar.shaatree",
    "علي الحذيفي": "ar.hudhaify",
    "ماهر المعيقلي": "ar.mahermuaiqly",
    "أحمد العجمي": "ar.ahmedajamy",
    "محمد أيوب": "ar.muhammadayyoub",
    "سعود الشريم": "ar.saoodshuraym",
}


# ==================================================
# تحميل القرآن والأذكار
# ==================================================
def get_json(url, params=None):
    response = requests.get(
        url,
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()

    if data.get("code", 200) != 200:
        raise ValueError("مصدر البيانات أعاد خطأ.")

    return data


@st.cache_data(ttl=3600, show_spinner=False)
def load_surahs():
    return get_json(f"{QURAN_API}/surah")["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_surah(surah_number, edition):
    return get_json(
        f"{QURAN_API}/surah/{surah_number}/{edition}"
    )["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_surah_text(surah_number):
    return get_json(
        f"{QURAN_API}/surah/{surah_number}/quran-uthmani"
    )["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_all_adhkar():
    response = requests.get(ADHKAR_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    result = []

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

                    result.append({
                        "القسم": category_name,
                        "الباب": title_name,
                        "النص": arabic,
                        "المصدر": str(
                            dua.get("source", "")
                        ),
                        "الترجمة": str(
                            dua.get("translation", "")
                        ),
                        "النطق": str(
                            dua.get("latin", "")
                        ),
                    })

    return result


# ==================================================
# واجهة القراءات العشر الرسمية
# تتطلب بيانات اعتماد وصلاحية qiraat.read
# ==================================================
def get_qf_credentials():
    try:
        client_id = st.secrets["QF_CLIENT_ID"]
        client_secret = st.secrets["QF_CLIENT_SECRET"]

        if client_id and client_secret:
            return client_id, client_secret

    except Exception:
        pass

    return None, None


@st.cache_data(ttl=3300, show_spinner=False)
def get_qf_token(client_id, client_secret):
    response = requests.post(
        QF_TOKEN_URL,
        auth=(client_id, client_secret),
        data={
            "grant_type": "client_credentials",
            "scope": "qiraat.read",
        },
        timeout=30,
    )
    response.raise_for_status()

    token = response.json().get("access_token")

    if not token:
        raise ValueError("لم يتم الحصول على رمز API.")

    return token


def qf_request(url, token, client_id, params=None):
    response = requests.get(
        url,
        params=params,
        headers={
            "x-auth-token": token,
            "x-client-id": client_id,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=3600, show_spinner=False)
def load_qiraat_chapter(
    chapter_number,
    client_id,
    client_secret,
):
    token = get_qf_token(client_id, client_secret)

    url = (
        f"{QF_BASE}/qiraat/matrix/"
        f"by_chapter/{chapter_number}"
    )

    all_junctures = []
    readers = []
    transmitters = []
    page = 1
    total_pages = 1
    chapter_data = {}

    while page <= total_pages:
        data = qf_request(
            url,
            token,
            client_id,
            params={
                "page": page,
                "per_page": 100,
                "text_field": "text_uthmani",
                "language": "ar",
            },
        )

        chapter_data = data.get("chapter", chapter_data)
        readers = data.get("readers", readers)
        transmitters = data.get(
            "transmitters", transmitters
        )

        all_junctures.extend(
            data.get("junctures", [])
        )

        pagination = data.get("pagination", {})
        total_pages = pagination.get("total_pages", 1)
        page += 1

    return {
        "chapter": chapter_data,
        "readers": readers,
        "transmitters": transmitters,
        "junctures": all_junctures,
    }


# ==================================================
# التصميم
# ==================================================
def apply_styles(dark_mode):
    if dark_mode:
        bg = "#111827"
        card = "#1f2937"
        fg = "#f9fafb"
        muted = "#d1d5db"
        border = "#374151"
        accent = "#34d399"
    else:
        bg = "#f8fafc"
        card = "#ffffff"
        fg = "#172033"
        muted = "#475569"
        border = "#e2e8f0"
        accent = "#047857"

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
            max-width: 1200px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }}

        h1, h2, h3, p, label {{
            color: {fg};
        }}

        .hero {{
            background: linear-gradient(135deg, {card}, {bg});
            border: 1px solid {border};
            border-radius: 20px;
            padding: 22px 14px;
            text-align: center;
            margin-bottom: 22px;
        }}

        .hero h1 {{
            color: {accent};
            font-family: 'Amiri', serif;
            font-size: clamp(27px, 5vw, 43px);
        }}

        .hero p {{
            color: {muted};
        }}

        .arabic, .dhikr {{
            font-family: 'Amiri', serif;
            font-size: clamp(23px, 3vw, 30px);
            line-height: 2.1;
            direction: rtl;
            text-align: right;
            color: {fg};
            overflow-wrap: anywhere;
            white-space: pre-wrap;
        }}

        .ayah-number {{
            color: {accent};
            font-size: 16px;
            font-weight: bold;
            margin-left: 8px;
        }}

        .watermark-center {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: {accent};
            opacity: 0.12;
            font-family: Arial, sans-serif;
            font-size: clamp(24px, 5vw, 58px);
            font-weight: 900;
            text-align: center;
            white-space: nowrap;
            pointer-events: none;
            user-select: none;
            z-index: 999;
        }}

        .watermark-star {{
            font-size: 1.5em;
            line-height: 1.15;
            margin-bottom: 5px;
        }}

        .watermark-name {{
            letter-spacing: 2px;
        }}

        .footer {{
            text-align: center;
            font-size: 12px;
            color: {muted};
            border-top: 1px solid {border};
            padding: 15px;
            margin-top: 28px;
        }}

        @media (max-width: 640px) {{
            .block-container {{
                padding-left: 12px;
                padding-right: 12px;
            }}

            .watermark-center {{
                font-size: 24px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ==================================================
# الشريط الجانبي
# ==================================================
with st.sidebar:
    st.markdown("## 📖 حصن المسلم")

    dark_mode = st.toggle(
        "🌙 الوضع الليلي",
        value=False,
    )

    st.divider()
    st.caption("القرآن الكريم والأذكار والقراءات")


apply_styles(dark_mode)


# ==================================================
# العلامة المائية: نجمة + OMAR MELIGY
# ==================================================
st.markdown(
    """
    <div class="watermark-center">
        <div class="watermark-star">★</div>
        <div class="watermark-name">OMAR MELIGY</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# رأس الموقع
# ==================================================
st.markdown(
    """
    <div class="hero">
        <h1>حصن المسلم والقرآن الكريم</h1>
        <p>القرآن الكريم • القراءات العشر • الأذكار • الدعاء</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# التبويبات الرئيسية
# ==================================================
tab_quran, tab_qiraat, tab_adhkar, tab_search = st.tabs([
    "📗 القرآن الكريم",
    "📚 القراءات العشر",
    "🤲 جميع الأذكار",
    "🔎 البحث",
])


# ==================================================
# القرآن الكريم والتلاوات المتاحة
# ==================================================
with tab_quran:
    st.subheader("📗 القرآن الكريم")

    try:
        surahs = load_surahs()

        surah_options = {
            f"{s['number']}. {s['name']}": s["number"]
            for s in surahs
        }

        selected_label = st.selectbox(
            "اختر السورة",
            list(surah_options.keys()),
            key="quran_surah",
        )

        surah_number = surah_options[selected_label]

        reciter_name = st.selectbox(
            "اختر القارئ",
            list(RECITERS.keys()),
            key="quran_reciter",
        )

        try:
            surah_data = load_surah(
                surah_number,
                RECITERS[reciter_name],
            )
        except Exception:
            st.warning(
                "تعذر تحميل تلاوة القارئ المختار؛ "
                "سيتم محاولة تحميل النص."
            )
            surah_data = load_surah_text(surah_number)

        st.markdown(
            f"### {surah_data.get('name', selected_label)}"
        )

        ayahs = surah_data.get("ayahs", [])
        st.caption(f"عدد الآيات: {len(ayahs)}")

        if ayahs:
            ayah_options = {
                f"الآية {a.get('numberInSurah', i + 1)}": i
                for i, a in enumerate(ayahs)
            }

            selected_ayah = st.selectbox(
                "اختر آية للاستماع",
                list(ayah_options.keys()),
                key="quran_ayah",
            )

            ayah = ayahs[ayah_options[selected_ayah]]

            if ayah.get("audio"):
                st.write(f"استماع — {reciter_name}")
                st.audio(ayah["audio"])

            st.divider()
            st.markdown("### نص السورة")

            for a in ayahs:
                text = html.escape(str(a.get("text", "")))
                number = a.get("numberInSurah", "")

                st.markdown(
                    f"""
                    <div class="arabic">
                        {text}
                        <span class="ayah-number">﴿{number}﴾</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    except Exception as error:
        st.error(
            "تعذر تحميل القرآن. تأكد من اتصال الإنترنت."
        )
        st.caption(str(error))


# ==================================================
# القراءات العشر: مواضع الاختلاف المعتمدة
# ==================================================
with tab_qiraat:
    st.subheader("📚 القراءات العشر والروايات")
    st.write(
        "يعرض هذا القسم مواضع الاختلاف القرائي التي "
        "توفرها واجهة البيانات الرسمية، مع نسبتها إلى "
        "القراء والرواة وفق بيانات المصدر."
    )

    client_id, client_secret = get_qf_credentials()

    if not client_id or not client_secret:
        st.warning(
            "قسم القراءات يحتاج بيانات اعتماد Quran Foundation."
        )

        st.markdown(
            """
            **إعداد البيانات:**

            1. سجّل تطبيقًا في [Quran Foundation Developer Console](https://quran.foundation/developers).
            2. اطلب تفعيل صلاحية `qiraat.read`.
            3. أضف بيانات الاعتماد إلى ملف
               `.streamlit/secrets.toml` كما هو موضح أدناه.
            """
        )

        st.code(
            'QF_CLIENT_ID = "ضع_معرف_التطبيق_هنا"\n'
            'QF_CLIENT_SECRET = "ضع_المفتاح_السري_هنا"',
            language="toml",
        )

    else:
        try:
            surahs = load_surahs()

            qiraat_surah_options = {
                f"{s['number']}. {s['name']}": s["number"]
                for s in surahs
            }

            qiraat_surah_label = st.selectbox(
                "اختر السورة لعرض مواضع الاختلاف",
                list(qiraat_surah_options.keys()),
                key="qiraat_surah",
            )

            qiraat_surah_number = qiraat_surah_options[
                qiraat_surah_label
            ]

            with st.spinner("جارٍ تحميل بيانات القراءات..."):
                qiraat_data = load_qiraat_chapter(
                    qiraat_surah_number,
                    client_id,
                    client_secret,
                )

            readers = qiraat_data.get("readers", [])
            transmitters = qiraat_data.get(
                "transmitters", []
            )
            junctures = qiraat_data.get("junctures", [])

            if not readers:
                st.info(
                    "لم تُرجع الخدمة قائمة قراء لهذه السورة."
                )
            else:
                reader_by_name = {
                    r["name"]: r for r in readers
                }

                reader_name = st.selectbox(
                    "اختر القارئ",
                    list(reader_by_name.keys()),
                    key="qiraat_reader",
                )

                selected_reader = reader_by_name[reader_name]
                reader_id = selected_reader["id"]

                reader_transmitters = [
                    t for t in transmitters
                    if t.get("reader_id") == reader_id
                ]

                if reader_transmitters:
                    transmitter_by_name = {
                        t["name"]: t
                        for t in reader_transmitters
                    }

                    transmitter_name = st.selectbox(
                        "اختر الراوي",
                        list(transmitter_by_name.keys()),
                        key="qiraat_transmitter",
                    )

                    selected_transmitter = (
                        transmitter_by_name[transmitter_name]
                    )
                    transmitter_id = selected_transmitter["id"]
                else:
                    transmitter_name = None
                    transmitter_id = None

                st.caption(
                    "مواضع الاختلاف هنا ليست بالضرورة نص السورة "
                    "كاملًا بالرواية المختارة."
                )

                matching = []

                for juncture in junctures:
                    for reading in juncture.get("readings", []):
                        matrix = reading.get("matrix", {})
                        cells = matrix.get("cells", [])

                        attributed = any(
                            cell.get("reader_id") == reader_id
                            and (
                                cell.get("type") == "reader"
                                and cell.get("transmitter_id") is None
                            )
                            for cell in cells
                        )

                        if transmitter_id is not None:
                            attributed = attributed or any(
                                cell.get("reader_id") == reader_id
                                and cell.get("transmitter_id")
                                == transmitter_id
                                and cell.get("type") == "transmitter"
                                for cell in cells
                            )

                        if attributed:
                            matching.append(
                                (juncture, reading)
                            )

                if matching:
                    st.success(
                        f"عدد النتائج المطابقة: {len(matching)}"
                    )

                    for i, (juncture, reading) in enumerate(matching):
                        with st.container(border=True):
                            st.markdown(
                                f"**الموضع:** "
                                f"{juncture.get('verse_key', 'غير محدد')}"
                            )

                            original_text = juncture.get(
                                "text_uthmani", ""
                            )

                            if original_text:
                                st.markdown("**موضع الاختلاف:**")
                                st.markdown(
                                    '<div class="arabic">'
                                    + html.escape(str(original_text))
                                    + "</div>",
                                    unsafe_allow_html=True,
                                )

                            reading_text = reading.get(
                                "text_uthmani"
                            ) or reading.get("text", "")

                            st.markdown("**النص المنسوب لهذه القراءة:**")
                            st.markdown(
                                '<div class="dhikr">'
                                + html.escape(str(reading_text))
                                + "</div>",
                                unsafe_allow_html=True,
                            )

                            st.caption(
                                f"القارئ: {reader_name}"
                                + (
                                    f" — الراوي: {transmitter_name}"
                                    if transmitter_name else ""
                                )
                            )

                            if reading.get("translation"):
                                with st.expander("الشرح أو الترجمة المتاحة"):
                                    st.write(reading["translation"])

                else:
                    st.info(
                        "لم تُرجع الخدمة مواضع اختلاف مطابقة "
                        "للاختيار في هذه السورة."
                    )

                st.warning(
                    "هذا القسم يعرض 

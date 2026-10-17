
import html
import requests
import streamlit as st

# ==========================================
# إعدادات الموقع
# ==========================================
st.set_page_config(
    page_title="حصن المسلم والقرآن الكريم",
    page_icon="📖",
    layout="wide",
)

QURAN_API = "https://api.alquran.cloud/v1"

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

QIRAAT = {
    "نافع المدني": [
        "قالون عن نافع",
        "ورش عن نافع",
    ],
    "ابن كثير المكي": [
        "البزي عن ابن كثير",
        "قنبل عن ابن كثير",
    ],
    "أبو عمرو البصري": [
        "الدوري عن أبي عمرو",
        "السوسي عن أبي عمرو",
    ],
    "ابن عامر الشامي": [
        "هشام عن ابن عامر",
        "ابن ذكوان عن ابن عامر",
    ],
    "عاصم الكوفي": [
        "شعبة عن عاصم",
        "حفص عن عاصم",
    ],
    "حمزة الكوفي": [
        "خلف عن حمزة",
        "خلاد عن حمزة",
    ],
    "الكسائي الكوفي": [
        "أبو الحارث عن الكسائي",
        "الدوري عن الكسائي",
    ],
    "أبو جعفر المدني": [
        "ابن وردان عن أبي جعفر",
        "ابن جماز عن أبي جعفر",
    ],
    "يعقوب الحضرمي": [
        "رويس عن يعقوب",
        "روح عن يعقوب",
    ],
    "خلف العاشر": [
        "إسحاق عن خلف",
        "إدريس عن خلف",
    ],
}


# ==========================================
# تحميل البيانات
# ==========================================
def get_json(url):
    response = requests.get(
        url,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()

    if data.get("code", 200) != 200:
        raise ValueError("تعذر تحميل البيانات.")

    return data


@st.cache_data(ttl=3600, show_spinner=False)
def load_surahs():
    return get_json(
        f"{QURAN_API}/surah"
    )["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_surah(surah_number, edition):
    url = (
        f"{QURAN_API}/surah/"
        f"{surah_number}/{edition}"
    )
    return get_json(url)["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_surah_text(surah_number):
    url = (
        f"{QURAN_API}/surah/"
        f"{surah_number}/quran-uthmani"
    )
    return get_json(url)["data"]


@st.cache_data(ttl=3600, show_spinner=False)
def load_all_adhkar():
    response = requests.get(
        ADHKAR_URL,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    result = []

    for segment in data.get("segments", []):
        segment_name = segment.get(
            "segment_name",
            "أذكار متنوعة",
        )

        for category in segment.get("categories", []):
            category_name = category.get(
                "category_name",
                segment_name,
            )

            for title in category.get("titles", []):
                title_name = title.get(
                    "title_name",
                    category_name,
                )

                for dua in title.get("duas", []):
                    arabic_text = str(
                        dua.get("arabic", "")
                    ).strip()

                    if not arabic_text:
                        continue

                    result.append({
                        "القسم": category_name,
                        "الباب": title_name,
                        "النص": arabic_text,
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


# ==========================================
# التصميم والعلامة المائية
# ==========================================
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


# ==========================================
# الشريط الجانبي
# ==========================================
with st.sidebar:
    st.markdown("## 📖 حصن المسلم")

    dark_mode = st.toggle(
        "🌙 الوضع الليلي",
        value=False,
    )

    st.divider()
    st.caption("القرآن الكريم والأذكار والقراءات")


apply_styles(dark_mode)


# ==========================================
# العلامة المائية
# ==========================================
st.markdown(
    """
    <div class="watermark-center">
        <div class="watermark-star">★</div>
        <div class="watermark-name">OMAR MELIGY</div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# رأس الموقع
# ==========================================
st.markdown(
    """
    <div class="hero">
        <h1>حصن المسلم والقرآن الكريم</h1>
        <p>القرآن الكريم • القراءات العشر • الأذكار • الدعاء</p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================
# التبويبات
# ==========================================
tab_quran, tab_qiraat, tab_adhkar, tab_search = st.tabs([
    "📗 القرآن الكريم",
    "📚 القراءات العشر",
    "🤲 جميع الأذكار",
    "🔎 البحث",
])


# ==========================================
# القرآن الكريم
# ==========================================
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
                "تعذر تحميل بيانات القارئ. "
                "سنحاول تحميل نص القرآن."
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

            chosen_label = st.selectbox(
                "اختر آية للاستماع",
                list(ayah_options.keys()),
                key="quran_ayah",
            )

            selected_ayah = ayahs[ayah_options[chosen_label]]

            if selected_ayah.get("audio"):
                st.write(f"تلاوة {reciter_name}")
                st.audio(selected_ayah["audio"])

            st.divider()
            st.markdown("### نص السورة")

            for ayah in ayahs:
                text = html.escape(
                    str(ayah.get("text", ""))
                )
                number = ayah.get("numberInSurah", "")

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
            "تعذر تحميل القرآن الكريم. "
            "تحقق من اتصال الإنترنت."
        )
        st.caption(str(error))


# ==========================================
# القراءات العشر والروايات
# ==========================================
with tab_qiraat:
    st.subheader("📚 القراءات العشر والروايات")

    st.info(
        "اختر القارئ والرواية المطلوبة. "
        "القائمة التالية للتعريف والاختيار فقط؛ "
        "لا تعرض نصًا مختلفًا أو تلاوة خاصة بالرواية "
        "إلا بعد ربطها بمصدر موثوق يدعمها."
    )

    selected_qiraah = st.selectbox(
        "اختر القراءة",
        list(QIRAAT.keys()),
        key="qiraat_reader",
    )

    selected_riwayah = st.selectbox(
        "اختر الرواية",
        QIRAAT[selected_qiraah],
        key="qiraat_riwayah",
    )

    st.markdown("### اختيارك")
    st.write(f"**القارئ:** {selected_qiraah}")
    st.write(f"**الرواية:** {selected_riwayah}")

    st.warning(
        "لم يتم ربط هذا الاختيار بعد بنص كامل أو صوت خاص "
        "بهذه الرواية. القرآن الظاهر في تبويب القرآن "
        "قد يكون برواية حفص، فلا تعتبره نص الرواية المختارة."
    )

    st.markdown(
        "لإكمال هذا القسم، يلزم مصدر بيانات معتمد "
        "يوفر نصوص القراءات والتلاوات، مع صلاحية API "
        "إذا كان مزود الخدمة يشترطها."
    )

    st.link_button(
        "توثيق Quran Foundation",
        "https://api-docs.quran.com/",
    )


# ==========================================
# جميع الأذكار
# ==========================================
with tab_adhkar:
    st.subheader("🤲 حصن المسلم — جميع الأبواب")

    try:
        with st.spinner("جارٍ تحميل الأذكار..."):
            adhkar = load_all_adhkar()

        if not adhkar:
            st.warning("لم يتم العثور على أذكار.")
        else:
            st.success(
                f"تم تحميل {len(adhkar)} ذكرًا ودعاءً."
            )

            categories = sorted({
                item["القسم"] for item in adhkar
            })

            category = st.selectbox(
                "اختر قسم الأذكار",
                ["كل الأقسام"] + categories,
                key="adhkar_category",
            )

            filtered = adhkar

            if category != "كل الأقسام":
                filtered = [
                    item for item in adhkar
                    if item["القسم"] == category
                ]

            st.caption(
                f"عدد النصوص المعروضة: {len(filtered)}"
            )

            for i, item in enumerate(filtered):
                with st.container(border=True):
                    st.markdown(f"#### {item['الباب']}")

                    st.markdown(
                        '<div class="dhikr">'
                        + html.escape(item["النص"])
                        + "</div>",
                        unsafe_allow_html=True,
                    )

                    if item["النطق"]:
                        with st.expander("النطق بالحروف اللاتينية"):
                            st.write(item["النطق"])

                    if item["الترجمة"]:
                        with st.expander("الترجمة"):
                            st.write(item["الترجمة"])

                    if item["المصدر"]:
                        st.caption(
                            f"المصدر: {item['المصدر']}"
                        )

                    if st.button(
                        "عرض النص للنسخ",
                        key=f"copy_dhikr_{i}",
                    ):
                        st.code(item["النص"])

    except Exception as error:
        st.error(
            "تعذر تحميل الأذكار. تحقق من الإنترنت."
        )
        st.caption(str(error))


# ==========================================
# البحث في الأذكار
# ==========================================
with tab_search:
    st.subheader("🔎 البحث في الأذكار")

    query = st.text_input(
        "اكتب كلمة للبحث",
        placeholder="مثال: الصباح أو النوم أو سبحان الله",
        key="adhkar_search",
    )

    if query.strip():
        try:
            adhkar = load_all_adhkar()
            term = query.strip()

            results = [
                item for item in adhkar
                if term in item["النص"]
                or term in item["الباب"]
                or term in item["القسم"]
                or term in item["المصدر"]
            ]

            st.write(f"عدد النتائج: {len(results)}")

            if results:
                for i, item in enumerate(results):
                    with st.container(border=True):
                        st.markdown(f"#### {item['الباب']}")

                        st.markdown(
                            '<div class="dhikr">'
                            + html.escape(item["النص"])
                            + "</div>",
                            unsafe_allow_html=True,
                        )

                        st.caption(f"القسم: {item['القسم']}")

                        if item["المصدر"]:
                            st.caption(
                                f"المصدر: {item['المصدر']}"
                            )
            else:
                st.info("لا توجد نتائج مطابقة.")

        except Exception:
            st.error(
                "تعذر البحث بسبب مشكلة في تحميل الأذكار."
            )
    else:
        st.info("اكتب كلمة للبحث في الأذكار.")


# ==========================================
# تذييل الموقع
# ==========================================
st.markdown(
    """
    <div class="footer">
        حصن المسلم والقرآن الكريم
        <br>
        صدقة جارية بإذن الله
        <br>
        OMAR MELIGY
    </div>
    """,
    unsafe_allow_html=True,
)

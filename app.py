import streamlit as st
import requests
import os
from dotenv import load_dotenv
import certifi
import base64

# ---- Load environment variables
load_dotenv()
subscription_key = os.getenv("AZURE_TRANSLATOR_KEY")
region = os.getenv("AZURE_TRANSLATOR_REGION")
endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
category_id = os.getenv("AZURE_TRANSLATOR_CATEGORY")

# ---- Helper: encode image to base64
def get_base64_image(image_file: str) -> str:
    with open(image_file, "rb") as img:
        return base64.b64encode(img.read()).decode()

# ---- Apply background image via CSS
def set_background(image_path: str):
    b64 = get_base64_image(image_path)
    st.markdown(
        f"""
        <style>
        /* Set background on the main app container */
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64}");
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }}
        /* Optional dark overlay for readability */
        .stApp::before {{
            content: "";
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.25);
            z-index: -1;
        }}

        /* Title styling */
        .title {{
            font-size: 44px;
            color: #ffffff;
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
            text-shadow: 1px 1px 3px #000;
        }}
        /* Title row to align logo + text nicely */
        .title-row {{
            display: inline-flex;
            align-items: center;
            gap: 12px;
            justify-content: center;
        }}
        .title-row img {{
            height: 48px;              /* adjust logo height */
            width: auto;               /* keep aspect ratio */
            vertical-align: middle;
            filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.4));
        }}

        /* Bold labels (used for direction + textarea labels) */
        .label-bold {{
            font-size: 24px;     /* larger text */
            color: #ffffff;      /* white */
            font-weight: 700;    /* bold */
            margin: 2px 0;       /* tighter spacing above/below */
        }}

        /* Reduce default Streamlit spacing for the selectbox & textarea blocks */
        div[data-testid="stSelectbox"] {{
            margin-top: 0px !important;      /* tighten spacing under label */
        }}
        div[data-testid="stTextArea"] {{
            margin-top: 0px !important;      /* tighten spacing under label */
        }}

        /* Textarea styling */
        .stTextArea textarea {{
            border: 2px solid #3498db;
            border-radius: 8px;
            font-size: 20px;
            padding: 10px;
            background-color: rgba(255,255,255,0.9);
        }}

        /* Button styling */
        .stButton button {{
            background-color: #00008B;  /* dark blue */
            color: white;
            font-size: 20px;
            border-radius: 8px;
            padding: 10px 20px;
            transition: 0.2s;
        }}
        .stButton button:hover {{
            background-color: #000066;  /* darker blue on hover */
            transform: translateY(-1px);
        }}

        /* Output boxes */
        .success-box {{
            background-color: rgba(212, 237, 218, 0.95);
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            font-size: 18px;
            margin-top: 16px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }}
        .error-box {{
            background-color: #ffebee;       /* light red info box */
            color: #b71c1c;                   /* deep red text */
            padding: 14px 16px;
            border-radius: 10px;
            font-size: 16px;
            margin-top: 16px;
            border: 2px solid #b71c1c;        /* deeper red border */
            box-shadow: 0 2px 6px rgba(0,0,0,0.12);
        }}

        /* Streamlit alert overrides (st.error/st.warning) - darker red, bold text */
        div.stAlert {{
            background-color: #7F0000;   /* very dark red background */
            border: 2px solid #B71C1C;   /* deep red border */
            border-left: 0.6rem solid #D50000; /* strong red accent bar */
            color: #FFFFFF;              /* white text for contrast */
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.25);
        }}
        div.stAlert p {{
            color: #FFFFFF;              /* force paragraph text to white */
            font-weight: 800;            /* extra bold text */
            font-size: 16px;             /* slightly larger text */
            margin: 0.25rem 0;
        }}
        div.stAlert [data-testid="stMarkdownContainer"] svg {{
            fill: #FFFFFF !important;    /* white icon */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---- Apply background
set_background("background.jpg")  # change to "background.jpeg" if that's your actual file

# ---- Title with logo.png (replaces 🌐 emoji)
logo_b64 = get_base64_image("logo.png")  # ensure logo.png is in the working directory
st.markdown(
    f'''
    <div class="title">
      <span class="title-row">
        <img src="data:image/png;base64,{logo_b64}" alt="Logo"/>
        English → Vietnamese Translator
      </span>
    </div>
    ''',
    unsafe_allow_html=True
)

# ---- Direction selector (EN→VI / VI→EN) with styled label
st.markdown('<div class="label-bold">Translation Direction:</div>', unsafe_allow_html=True)
direction = st.selectbox(
    "",  # render our styled label above, so keep widget label empty
    ["English → Vietnamese", "Vietnamese → English"],
    index=0
)

# Map selection to language codes
if direction == "English → Vietnamese":
    from_lang = "en"
    to_lang = "vi"
else:
    from_lang = "vi"
    to_lang = "en"

# ---- Input label + textarea
label_text = "Enter English text:" if from_lang == "en" else "Enter Vietnamese text:"
st.markdown(f'<div class="label-bold">{label_text}</div>', unsafe_allow_html=True)
text_input = st.text_area(label="", placeholder=label_text)

# ---- Translate button on the right side of the input area
c_left, c_right = st.columns([4, 1])  # adjust ratios as you like
with c_right:
    translate_clicked = st.button("Translate")

# ---- Translate action
if translate_clicked:
    if not text_input.strip():
        # DARK RED alert with bold text (styled via CSS override above)
        st.error("Please enter some text.")
    else:
        headers = {
            "Ocp-Apim-Subscription-Key": subscription_key,
            "Ocp-Apim-Subscription-Region": region,
            "Content-Type": "application/json"
        }
        params = {
            "api-version": "3.0",
            "from": from_lang,
            "to": [to_lang],
            "category": category_id
        }
        body = [{"text": text_input}]
        try:
            resp = requests.post(
                endpoint.rstrip("/") + "/translate",
                params=params,
                headers=headers,
                json=body,
                verify=certifi.where()
            )
            if resp.status_code == 200:
                data = resp.json()
                translation = data[0]['translations'][0]['text']
                st.markdown(
                    f'<div class="success-box">✅ <strong>Translation ({from_lang} → {to_lang})</strong>: {translation}</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="error-box">❌ Error {resp.status_code}: {resp.text}</div>',
                    unsafe_allow_html=True
                )
        except requests.exceptions.SSLError as ssl_err:
            st.markdown(f'<div class="error-box">🔒 SSL error: {ssl_err}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-box">⚠️ Unexpected error: {e}</div>', unsafe_allow_html=True)

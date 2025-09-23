
import streamlit as st
import base64
import os
import pandas as pd
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.xception import preprocess_input
from tensorflow.keras.preprocessing import image as keras_image
import google.generativeai as genai
import hashlib


# Your DB helpers
from database import (
    create_users_table, add_user, get_all_users,
    login_user, update_user_profile,
    add_history, get_history_by_user
)

# ---------------------------- PASSWORD HASHING ----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ---------------------------- SESSION STATE ----------------------------
if "user_id" not in st.session_state:
    st.session_state["user_id"] = None
if "email" not in st.session_state:
    st.session_state["email"] = None
if "page" not in st.session_state:
    st.session_state.page = "home"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "profile_page" not in st.session_state:
    st.session_state.profile_page = False
if "history_page" not in st.session_state:
    st.session_state.history_page = False
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------- STREAMLIT PAGE CONFIG ----------------------------
st.set_page_config(page_title="Dog Breed App", page_icon="🐶", layout="wide")

# ---------------------------- INITIALIZE DB ----------------------------
create_users_table()

# ---------------------------- BACKGROUND + GLOBAL CSS ----------------------------
def set_background(image_file):
    try:
        abs_path = os.path.join(os.path.dirname(__file__), image_file)
        with open(abs_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{encoded}");
                background-size: cover;
                background-repeat: no-repeat;
                background-position: center;
            }}
            .stButton > button {{
                background-color: #ff4b4b !important;
                color: white !important;
                font-size: 16px;
                font-weight: 600;
                border-radius: 10px;
                padding: 10px 22px;
                margin: 12px auto !important;
                display: block;
            }}
            .home-spacer {{
                height: 18vh;
            }}
            .card {{
                background-color: white;
                padding: 18px;
                border-radius: 12px;
                box-shadow: 0 6px 18px rgba(0,0,0,0.10);
                margin-top: 16px;
            }}
            form input[type="text"],
            form input[type="password"],
            form textarea {{
                width: 100% !important;
                padding: 10px 12px !important;
                border-radius: 8px;
                border: 1px solid #e6e6e6;
            }}
            .center-column {{
                max-width: 720px;
                margin-left: auto;
                margin-right: auto;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )
    except Exception:
        st.warning("Background image not found or failed to load. Continuing without background.")

set_background("bg_img_resized.png")

# ---------------------------- LOAD LABELS & MODEL ----------------------------
@st.cache_data
def load_labels(csv_path=r"C:\Users\bavir\AI-Model-for-Dog-Breed-Detection-and-Information-Generation_August_2025\milestone3\label.csv"):
    labels = pd.read_csv(csv_path)
    breeds = sorted(labels['breed'].unique())
    return breeds

@st.cache_resource
def load_model(model_path=r"C:\Users\bavir\AI-Model-for-Dog-Breed-Detection-and-Information-Generation_August_2025\milestone3\Xception.h5"):
    model = tf.keras.models.load_model(model_path)
    return model

try:
    breeds = load_labels()
except Exception:
    breeds = []

try:
    model = load_model()
except Exception:
    model = None

# ---------------------------- GEMINI AI SETUP ----------------------------
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    pass

def get_gemini_response(breed):
    try:
        model_ai = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"For the dog breed {breed}, give me exactly 2 short lines each for:\n"
            f"1. Ancestry\n"
            f"2. Purpose\n"
            f"3. Migration\n\n"
            f"Format strictly like this:\n"
            f"Ancestry:\n- line1\n- line2\n\n"
            f"Purpose:\n- line1\n- line2\n\n"
            f"Migration:\n- line1\n- line2"
        )
        response = model_ai.generate_content(prompt)
        return response.text
    except Exception:
        return """Ancestry:
- Descendants of older working breeds.
- Developed in specific regions historically.

Purpose:
- Historically used for tasks.
- Now bred as companions.

Migration:
- Spread across regions with human movement.
- Bred and adopted worldwide."""

def extract_info(ai_text: str):
    sections = {"Ancestry": [], "Purpose": [], "Migration": []}
    current = None
    for line in ai_text.splitlines():
        line = line.strip()
        if line.lower().startswith("ancestry"):
            current = "Ancestry"
        elif line.lower().startswith("purpose"):
            current = "Purpose"
        elif line.lower().startswith("migration"):
            current = "Migration"
        elif line.startswith("-") and current:
            sections[current].append(line.lstrip("- ").strip())
    for k in sections:
        while len(sections[k]) < 2:
            sections[k].append("N/A")
    return sections

# ---------------------------- HOME PAGE ----------------------------
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align: center; margin-top:8px;'>Dog Breed Detection</h1>", unsafe_allow_html=True)
    st.markdown("<div class='home-spacer'></div>", unsafe_allow_html=True)

    left, mid, right = st.columns([1, 0.6, 1])
    with mid:
        if st.button("Login"):
            st.session_state.page = "login"
            st.rerun()
        if st.button("Signup"):
            st.session_state.page = "signup"
            st.rerun()

# ---------------------------- LOGIN PAGE ----------------------------
elif st.session_state.page == "login":
    st.markdown("<h2 style='color:white; text-align:center; margin-bottom: 6px;'>Login Page</h2>", unsafe_allow_html=True)
    st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1, 1.4, 1])
    with col_mid:
        with st.form("login_form"):
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            login_clicked = st.form_submit_button("Login")
        back_clicked = st.button("Back to Home", key="back_home_login")

        if login_clicked:
            if not email or not password:
                st.error("Please enter email and password.")
            else:
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                result = login_user(email, hashed_password)
                if result:
                    st.session_state.authenticated = True
                    st.session_state.user = result
                    st.session_state.user_id = result[0]
                    st.session_state.email = result[3]
                    st.session_state.page = "app"
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        if back_clicked:
            st.session_state.page = "home"
            st.rerun()

# ---------------------------- SIGNUP PAGE ----------------------------
elif st.session_state.page == "signup":
    st.markdown("<h2 style='color:white; text-align:center; margin-bottom: 6px;'>Signup Page</h2>", unsafe_allow_html=True)
    st.markdown("<div style='height: 2vh;'></div>", unsafe_allow_html=True)

    col_left, col_mid, col_right = st.columns([1, 1.4, 1])
    with col_mid:
        with st.form("signup_form"):
            first = st.text_input("First Name")
            last = st.text_input("Last Name")
            email_s = st.text_input("Email")
            password_s = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm Password", type="password")
            profile_pic = st.file_uploader("Upload Profile Picture", type=["jpg", "jpeg", "png"])
            create_clicked = st.form_submit_button("Create Account")

        if create_clicked:
            if password_s != confirm:
                st.error("Passwords do not match.")
            else:
                existing_users = get_all_users()
                if any(u[3] == email_s for u in existing_users):
                    st.error("This email is already registered!")
                else:
                    if profile_pic:
                        directory = "profile_pics"
                        os.makedirs(directory, exist_ok=True)
                        _, ext = os.path.splitext(profile_pic.name)
                        filename = f"{email_s.replace('@','_at_')}{ext}"
                        image_file_path = os.path.join(directory, filename)
                        with open(image_file_path, "wb") as f:
                            f.write(profile_pic.getbuffer())
                        profile_pic_path = image_file_path
                    else:
                        profile_pic_path = "https://cdn-icons-png.flaticon.com/512/616/616408.png"

                    hashed_password = hashlib.sha256(password_s.encode()).hexdigest()
                    add_user(first, last, email_s, hashed_password, profile_pic_path)
                    st.success("Account created successfully! Please login.")
                    st.session_state.page = "login"
                    st.rerun()

    col_left, col_mid, col_right = st.columns([1, 1.4, 1])
    with col_mid:
        if st.button("Back to Home", key="back_from_signup"):
            st.session_state.page = "home"
            st.rerun()

# ---------------------------- MAIN APP ----------------------------
elif st.session_state.page == "app":
    if not st.session_state.authenticated:
        st.session_state.page = "login"
        st.rerun()

    user = st.session_state.user
    try:
        first_name, last_name = user[1], user[2]
        email = user[3]
        profile_pic = user[5]
    except Exception:
        first_name, last_name = "Test", "User"
        email = "testuser@gmail.com"
        profile_pic = "https://cdn-icons-png.flaticon.com/512/616/616408.png"

    # Sidebar
    with st.sidebar:
        st.markdown("### Profile")
        st.image(profile_pic, width=110)
        st.markdown(f"**{first_name} {last_name}**")
        st.markdown(f"{email}")
        st.markdown("---")

        if st.button("🏠 Home"):
            st.session_state.profile_page = False
            st.session_state.history_page = False
            st.rerun()
        if st.button("👤 Profile"):
            st.session_state.profile_page = True
            st.session_state.history_page = False
            st.rerun()
        if st.button("📜 History"):
            st.session_state.history_page = True
            st.session_state.profile_page = False
            st.rerun()
        if st.button("⬅ Logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.page = "home"
            st.session_state.profile_page = False
            st.session_state.history_page = False
            st.rerun()

    # ---------------- Profile Page ----------------
    if st.session_state.profile_page:
        st.markdown("<div class='center-column'>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align:center;'>🐾 My Profile</h1>", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(profile_pic, width=150)
        with col2:
            st.write(f"**Name:** {first_name} {last_name}")
            st.write(f"**Email:** {email}")

        st.markdown("---")
        st.markdown("<h3>✏ Edit Profile</h3>", unsafe_allow_html=True)
        with st.form("edit_profile_form"):
            new_first = st.text_input("First Name", value=first_name)
            new_last = st.text_input("Last Name", value=last_name)
            new_image = st.file_uploader("Update Profile Picture", type=["jpg", "jpeg", "png"])
            submitted = st.form_submit_button("Update Profile")

            if submitted:
                if new_image:
                    os.makedirs("profile_pics", exist_ok=True)
                    _, ext = os.path.splitext(new_image.name)
                    filename = f"{email.replace('@','_at_')}{ext}"
                    image_file_path = os.path.join("profile_pics", filename)
                    with open(image_file_path, "wb") as f:
                        f.write(new_image.getbuffer())
                else:
                    image_file_path = profile_pic

                try:
                    update_user_profile(user[0], new_first, new_last, email, image_file_path)
                    st.session_state.user = (user[0], new_first, new_last, email, user[4], image_file_path)
                except Exception:
                    st.error("Failed to update profile in DB.")
                st.success("Profile updated successfully!")
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

   # ---------------- History Page ----------------
    elif st.session_state.history_page:
        st.markdown("<h1 style='text-align:center;'>📜 Prediction History</h1>", unsafe_allow_html=True)
        history = get_history_by_user(st.session_state.user_id)

        def ensure_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return 0.0

        def ensure_str(val):
            if isinstance(val, bytes):
                return val.decode(errors="ignore")
            elif val is None:
                return ""
            return str(val)

        if history:
            for h in history:
                breed = ensure_str(h[1])
                confidence = ensure_float(h[2])
                created_at = ensure_str(h[4])

                st.write(f"**Breed:** {breed} | **Confidence:** {confidence:.2f}% | **Date:** {created_at}")

                img_path = ensure_str(h[3])
                if img_path and os.path.exists(img_path):
                    st.image(img_path, width=200)
        else:
            st.info("No history found.")

    # ---------------- Main Dog Breed Detector ----------------
    else:
        st.markdown("<h1 style='text-align: center;'>🐶 Dog Breed Identifier</h1>", unsafe_allow_html=True)
        st.markdown("<div class='center-column'>", unsafe_allow_html=True)

        uploaded_file = st.file_uploader("Upload a dog image", type=["jpg","jpeg","png"])
        if uploaded_file is not None:
            img = Image.open(uploaded_file).convert("RGB")
            st.image(img, caption="Uploaded Image", use_container_width=True)

            img_resized = img.resize((350, 350))
            img_array = keras_image.img_to_array(img_resized)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)

            if model is None:
                st.error("Model not loaded. Check model path and try again.")
            else:
                preds = model.predict(img_array)[0]
                top_indices = preds.argsort()[-3:][::-1]
                top_breeds = [(breeds[i], preds[i]) for i in top_indices]

                chosen_breed, confidence = top_breeds[0]

                st.markdown(f"""
                <div style='background-color: #e0f7fa; padding: 18px; border-radius: 10px; margin-top: 10px;'>
                    <h3 style='text-align:center;'>Prediction: {chosen_breed}</h3>
                    <p style='text-align:center;'>Confidence: {confidence*100:.2f}%</p>
                </div>
                """, unsafe_allow_html=True)

                ai_text = get_gemini_response(chosen_breed)
                info = extract_info(ai_text)

                st.markdown(f"""
                    <div class='card'>
                        <h3 style='text-align:center; color:#5a2a83;'>📘 Breed Info: {chosen_breed}</h3>
                        <p>🐾 <strong>Ancestry:</strong> {info['Ancestry'][0]} {info['Ancestry'][1]}</p>
                        <p>🎯 <strong>Purpose:</strong> {info['Purpose'][0]} {info['Purpose'][1]}</p>
                        <p>🚚 <strong>Migration:</strong> {info['Migration'][0]} {info['Migration'][1]}</p>
                    </div>
                """, unsafe_allow_html=True)

                predictions_html = """
                    <div style='background-color: white; padding: 20px; border-radius: 10px; margin-top: 10px;'>
                        <h3 style='text-align:center; color: purple;'>📊 Top 3 Predictions</h3>
                        <ul style='font-size:16px; line-height:1.8;'>
                """
                for breed, prob in top_breeds:
                    predictions_html += f"<li><b>{breed}</b>: {prob*100:.2f}%</li>"
                predictions_html += "</ul></div>"
                st.markdown(predictions_html, unsafe_allow_html=True)

                # Save in session and DB
                st.session_state.history.append({
                    "image": img,
                    "breed": chosen_breed,
                    "confidence": confidence * 100
                })

                # Save in DB
                img_path = os.path.join("uploads", uploaded_file.name)
                os.makedirs("uploads", exist_ok=True)
                img.save(img_path)
                confidence_value = float(confidence * 100)  # ensure numeric
                add_history(st.session_state.user_id, chosen_breed, confidence_value, img_path)


        else:
            st.info("📷 Please upload a dog image to start.")

        st.markdown("</div>", unsafe_allow_html=True)

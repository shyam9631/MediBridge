import streamlit as st
from whatsapp import send_medicine_taken, send_low_stock_alert

# Page Configuration
st.set_page_config(
    page_title="MediBridge",
    page_icon="💊",
    layout="centered"
)

# Custom CSS Styling
st.markdown("""
    <style>
    .stApp {
       background-color: #0e1117;
    }
    h1 {
        color: #2C3E50;
        text-align: center;
    }
    .stButton > button {
        background-color: #3498DB;
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #2980B9;
        transform: scale(1.05);
    }
    .stTextInput > div > div > input {
    border-radius: 8px;
    border: 2px solid #667eea;
    background-color: #1e2130;
    color: white;
}
    </style>
""", unsafe_allow_html=True)

# Beautiful Header
st.markdown("""
    <div style='text-align: center; padding: 20px;
    background: linear-gradient(90deg, #667eea, #764ba2);
    border-radius: 15px; margin-bottom: 20px;'>
        <h1 style='color: white; font-size: 3em;'>
            💊 MediBridge
        </h1>
        <p style='color: white; font-size: 1.2em;'>
            Smart Medicine Tracker for Your Loved Ones
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Login Selection
st.markdown("### Who are you?")
col1, col2 = st.columns(2)

with col1:
    if st.button("👴 I am a Senior Citizen", use_container_width=True):
        st.session_state.user_type = "senior"

with col2:
    if st.button("👨‍👩‍👧 I am a Family Member", use_container_width=True):
        st.session_state.user_type = "family"

# Show based on selection
if "user_type" in st.session_state:
    st.divider()

    # SENIOR CITIZEN DASHBOARD
    if st.session_state.user_type == "senior":
        st.markdown("## 👴 Senior Citizen Dashboard")

        # Add Medicine Form
        st.markdown("### ➕ Add New Medicine")
        with st.form("add_medicine_form"):
            med_name = st.text_input("💊 Medicine Name")
            dosage = st.text_input("📏 Dosage (e.g. 500mg)")
            timing = st.selectbox("⏰ Timing", [
                "Morning", "Afternoon", "Evening", "Night",
                "Morning & Night", "Morning, Afternoon & Night"
            ])
            total_count = st.number_input(
                "📦 Total Tablets/Capsules",
                min_value=1,
                max_value=500,
                value=30
            )
            submitted = st.form_submit_button(
                "➕ Add Medicine",
                use_container_width=True
            )

            if submitted:
                if med_name and dosage:
                    if "medicines" not in st.session_state:
                        st.session_state.medicines = []
                    st.session_state.medicines.append({
                        "name": med_name,
                        "dosage": dosage,
                        "timing": timing,
                        "total": total_count,
                        "remaining": total_count,
                        "taken_today": False
                    })
                    st.success(f"✅ {med_name} added successfully!")
                else:
                    st.error("❌ Please fill all fields!")

        # Show Medicine List
        st.markdown("### 📋 Your Medicines Today")
        if "medicines" not in st.session_state or len(st.session_state.medicines) == 0:
            st.info("No medicines added yet. Add your first medicine above!")
        else:
            for i, med in enumerate(st.session_state.medicines):
                st.markdown(f"""
                    <div style='
                        background: white;
                        padding: 15px;
                        border-radius: 12px;
                        border-left: 5px solid #3498DB;
                        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                        margin-bottom: 10px;'>
                        <h3 style='color: #2C3E50;'>
                            💊 {med['name']} — {med['dosage']}
                        </h3>
                        <p style='color: #7F8C8D;'>⏰ {med['timing']}</p>
                        <p style='color: #E74C3C; font-weight: bold;'>
                            📦 Remaining: {med['remaining']} tablets
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                col1, col2 = st.columns([3, 1])
                with col2:
                    if not med["taken_today"]:
                        if st.button(f"✅ Took it!", key=f"took_{i}", use_container_width=True):
                            st.session_state.medicines[i]["taken_today"] = True
                            st.session_state.medicines[i]["remaining"] -= 1

                            # Send WhatsApp notification
                            try:
                                send_medicine_taken(
                                    med['name'],
                                    med['dosage'],
                                    st.session_state.medicines[i]["remaining"]
                                )
                                st.success(f"✅ {med['name']} taken! Family notified on WhatsApp! 📱")
                            except:
                                st.success(f"✅ {med['name']} marked as taken!")

                            # Low stock WhatsApp alert
                            if st.session_state.medicines[i]["remaining"] <= 5:
                                try:
                                    send_low_stock_alert(
                                        med['name'],
                                        st.session_state.medicines[i]["remaining"]
                                    )
                                    st.warning(f"⚠️ Low stock alert sent to family on WhatsApp!")
                                except:
                                    st.warning(f"⚠️ Only {med['remaining']} tablets left!")

                            st.rerun()
                    else:
                        st.success("✅ Taken!")

                if med["remaining"] <= 5:
                    st.warning(f"⚠️ Low Stock! Only {med['remaining']} tablets left!")
                st.divider()

    # FAMILY DASHBOARD
    elif st.session_state.user_type == "family":
        st.markdown("## 👨‍👩‍👧 Family Dashboard")
        st.info("👀 Monitoring your loved one's medicines")

        if "medicines" not in st.session_state or len(st.session_state.medicines) == 0:
            st.warning("No medicines added yet by senior citizen!")
        else:
            st.markdown("### 📊 Medicine Status")
            for med in st.session_state.medicines:
                st.markdown(f"""
                    <div style='
                        background: white;
                        padding: 15px;
                        border-radius: 12px;
                        border-left: 5px solid {'#2ECC71' if med['taken_today'] else '#E74C3C'};
                        box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                        margin-bottom: 10px;'>
                        <h3 style='color: #2C3E50;'>
                            💊 {med['name']} — {med['dosage']}
                        </h3>
                        <p style='color: #7F8C8D;'>⏰ {med['timing']}</p>
                        <p style='color: {'#2ECC71' if med['taken_today'] else '#E74C3C'};
                        font-weight: bold; font-size: 1.2em;'>
                            {'✅ Medicine Taken!' if med['taken_today'] else '❌ Not Taken Yet!'}
                        </p>
                        <p style='color: #E74C3C;'>
                            📦 Remaining: {med['remaining']} tablets
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                if med["remaining"] <= 5:
                    st.warning(f"⚠️ {med['name']} running low! Only {med['remaining']} left!")
                st.divider()
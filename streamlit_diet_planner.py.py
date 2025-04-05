import streamlit as st
import requests
import time

# Page configuration
st.set_page_config(
    page_title="NutriGen AI | Premium Diet Planner",
    page_icon="🍽️",
    layout="wide"
)

# Custom dark theme CSS
st.markdown("""
    <style>
        body, .stApp {
            background-color: #1e1e1e;
            color: #f5f5f5;
            font-family: 'Montserrat', sans-serif;
        }
        .header-title {
            font-size: 2.5rem;
            color: #f5f5f5;
            font-weight: 500;
            text-align: center;
        }
        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol {
            background-color: #1e1e1e !important;
            color: #f5f5f5 !important;
            font-weight: 400;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #ffffff !important;
            font-weight: 600 !important;
        }
        .stMarkdown strong {
            color: #ffffff !important;
            font-weight: 700 !important;
        }
        .stMarkdownContainer, .stMarkdown > div {
            background-color: #1e1e1e !important;
        }
        .css-1cpxqw2, .stTextInput>div>div>input,
        .stSelectbox>div>div>div>div,
        .stNumberInput input {
            background-color: #2e2e2e !important;
            color: #f5f5f5 !important;
            border: 1px solid #444;
        }
        .stButton>button {
            background-color: #444 !important;
            color: #f5f5f5 !important;
            border: none;
        }
        .stButton>button:hover {
            background-color: #666 !important;
            color: #fff !important;
        }
        .css-1offfwp {
            background-color: #1e1e1e !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="header-title">NutriGen AI</h1><p style="text-align:center; color: #ccc;">Your personalized nutrition planner</p>', unsafe_allow_html=True)

# Main form
with st.form("diet_plan_form"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Information")
        name = st.text_input("Full Name", placeholder="John Doe")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
        height = st.number_input("Height (cm)", min_value=100, max_value=250, value=170)
        weight = st.number_input("Weight (kg)", min_value=30, max_value=300, value=70)
        activity_level = st.selectbox("Activity Level", ["Sedentary", "Lightly active", "Moderately active", "Very active"])
    
    with col2:
        st.subheader("Dietary Preferences")
        goal = st.selectbox("Goal", ["Weight loss", "Weight maintenance", "Muscle gain", "Improve health"])
        diet_pref = st.selectbox("Dietary Preference", ["No restrictions", "Vegetarian", "Vegan", "Gluten-free"])
        allergies = st.text_input("Allergies", placeholder="Peanuts, shellfish, etc.")
        medical_conditions = st.text_input("Medical Conditions", placeholder="Diabetes, hypertension, etc.")
        budget_level = st.selectbox("Budget Level", ["Low", "Medium", "High"])
        days = st.number_input("Number of Days for Plan", min_value=1, max_value=14, value=7, help="Generate a meal plan for up to 14 days")

    submitted = st.form_submit_button("Generate Plan", type="primary")

# API call and display
if submitted:
    if not name:
        st.warning("Please enter your name")
        st.stop()

    data = {
        "name": name,
        "gender": gender,
        "age": age,
        "height": height,
        "weight": weight,
        "activity_level": activity_level,
        "goal": goal,
        "diet_pref": diet_pref,
        "allergies": allergies,
        "medical_conditions": medical_conditions,
        "meal_pref": "Standard",
        "budget_level": budget_level,
        "days": days
    }

    with st.spinner('Creating your personalized plan...'):
        try:
            API_ENDPOINT = "http://localhost:8000/generate_diet_plan"
            response = requests.post(API_ENDPOINT, json=data, stream=True)

            if response.status_code == 200:
                result_container = st.empty()
                full_response = ""

                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        decoded_chunk = chunk.decode('utf-8')
                        full_response += decoded_chunk
                        result_container.markdown(full_response)
                        time.sleep(0.05)

                st.success("Plan generated successfully!")

                st.download_button(
                    "Download Plan",
                    full_response,
                    file_name=f"{name}_diet_plan.txt",
                    mime="text/plain"
                )

            else:
                st.error(f"Error: {response.text}")

        except requests.exceptions.RequestException as e:
            st.error(f"Connection error: Please make sure the API server is running. {str(e)}")

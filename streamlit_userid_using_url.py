import streamlit as st
import requests
import time
from pymongo import MongoClient
from bson.objectid import ObjectId

# --- FIRST Streamlit command: Set page config ---
st.set_page_config(
    page_title="NutriGen AI | Premium Diet Planner",
    page_icon="🍽️",
    layout="wide"
)

# --- Get user_id from URL (modern method) ---
query_params = st.query_params
user_id = query_params.get("user_id", None)

# --- MongoDB Setup ---
client = MongoClient("mongodb+srv://tetraPack:DFpAB4rJTOl4GVow@tetrapack.bp5jdmc.mongodb.net/")
db = client["test"]
user_collection = db["users"]

def get_user_data(uid):
    if uid is None:
        return None
    try:
        user = user_collection.find_one({"_id": ObjectId(uid)})
        if user:
            user["_id"] = str(user["_id"])
            return user
        else:
            return None
    except Exception as e:
        st.error(f"Error fetching user data: {str(e)}")
        return None

# --- Custom CSS (Dark Mode + Centering) ---
st.markdown("""
    <style>
        body {
            background-color: #0e1117;
            color: #ffffff;
        }
        .stApp {
            background-color: #0e1117;
        }
        .header-title {
            text-align: center;
            font-size: 3rem;
            color: #fafafa;
        }
        .stTextInput > div > div > input,
        .stNumberInput input,
        .stSelectbox > div > div > div {
            background-color: #2c2c2c;
            color: white;
        }
        .css-1emrehy {
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<h1 class="header-title">NutriGen AI</h1><p style="text-align:center; color: #ccc;">Your personalized nutrition planner</p>', unsafe_allow_html=True)

# --- Check for user_id ---
if not user_id:
    st.warning("User ID not found. Please access this app from your account.")
    st.stop()

user_data = get_user_data(user_id)

# --- Main Form ---
with st.form("diet_plan_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Personal Information")
        name = st.text_input("Full Name", user_data.get("username", "") if user_data else "")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                              index=["male", "female", "other"].index(user_data["gender"].lower()) if user_data else 0)
        age = st.number_input("Age", value=user_data.get("age", 30) if user_data else 30)
        height = st.number_input("Height (cm)", value=user_data.get("height", 170) if user_data else 170)
        weight = st.number_input("Weight (kg)", value=user_data.get("weight", 70) if user_data else 70)
        activity_level = st.selectbox("Activity Level",
                                      ["Sedentary", "Lightly active", "Moderately active", "Very active"],
                                      index={"sedentary": 0, "light": 1, "moderate": 2, "very active": 3}
                                      .get(user_data.get("activity_level", "light").lower(), 1) if user_data else 0)

    with col2:
        st.subheader("Dietary Preferences")
        goal = st.selectbox("Goal", ["weight-loss", "Weight maintenance", "Muscle gain", "Improve health"],
                            index=["weight-loss", "weight maintenance", "muscle gain", "improve health"]
                            .index(user_data.get("goal", "Weight loss").lower()) if user_data else 0)
        diet_pref = st.selectbox("Dietary Preference", ["No restrictions", "Vegetarian", "Vegan", "Gluten-free"],
                                 index={"no restrictions": 0, "vegetarian": 1, "vegan": 2, "gluten-free": 3}
                                 .get(user_data.get("diet_pref", "Vegetarian").lower(), 1) if user_data else 0)
        allergies = st.text_input("Allergies", user_data.get("allergies", "") if user_data else "")
        medical_conditions = st.text_input("Medical Conditions", user_data.get("medical_conditions", "") if user_data else "")
        budget_level = st.selectbox("Budget Level", ["Low", "Medium", "High"],
                                    index={"low": 0, "medium": 1, "high": 2}
                                    .get(user_data.get("budget_level", "Medium").lower(), 1) if user_data else 1)
        days = st.number_input("Number of Days for Plan", value=user_data.get("days", 7) if user_data else 7)

    submitted = st.form_submit_button("Generate Plan", type="primary")

# --- API Call and Display ---
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
        "meal_pref": user_data.get("meal_pref", "Standard") if user_data else "Standard",
        "budget_level": budget_level,
        "days": days
    }

    with st.spinner('Creating your personalized plan...'):
        try:
            API_ENDPOINT = "https://diet-planner-api.onrender.com/generate_diet_plan"
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

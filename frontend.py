import streamlit as st
import requests

API_URL="http://127.0.0.1:8000/predict"

def main():
    st.title("Insurance Premium Category Predictor")
    st.markdown("Enter your details below:")

    # Input fields
    age = st.number_input("Age", min_value=0, max_value=120, value=30)
    height = st.number_input("Height (m)", min_value=0.5, max_value=3.0, value=1.75)
    weight = st.number_input("Weight (kg)", min_value=20, max_value=300, value=70)
    income_lpa = st.number_input("Income (LPA)", min_value=0, max_value=100, value=10)
    occupation = st.selectbox("Occupation", ['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'])
    city = st.text_input("City")
    smoker = st.selectbox("Are you a smoker?", options=[True, False])

    if st.button("Predict Premium Category"):
        data = {
            "age": age,
            "height": height,
            "weight": weight,
            "income_lpa": income_lpa,
            "occupation": occupation,
            "city": city,
            "smoker": smoker
        }
        
        try:
            response = requests.post(API_URL, json=data)
            response.raise_for_status()  
            result = response.json()
            # st.write(result)
            if response.status_code == 200:
                st.success(f"Predicted Insurance Premium Category: **{result['prediction']}**")                
            else:
                st.error(f"API Error: {response.status_code}")
                st.write(result)
        except requests.exceptions.ConnectionError:
            st.error("❌ Could not connect to the FastAPI server. Make sure it's running.")

if __name__ == "__main__":
    main()

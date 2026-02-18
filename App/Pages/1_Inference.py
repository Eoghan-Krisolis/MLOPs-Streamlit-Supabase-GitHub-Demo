import streamlit as st
from src.inference import predict

st.title("Customer Preference Prediction")

st.write("Enter customer details below:")

# ----------------------------
# 1️⃣ Numeric Inputs
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Age", min_value=18, max_value=100, value=35)
    motor_value = st.number_input("Motor Value", min_value=0, max_value=200000, value=15000)
    health_adults = st.number_input("Health Dependents (Adults)", min_value=0, max_value=10, value=1)
    health_kids = st.number_input("Health Dependents (Kids)", min_value=0, max_value=10, value=2)

with col2:
    credit_card = st.selectbox(
        "Credit Card Type",
        ["AMEX", "Visa"]
    )

    motor_type = st.selectbox(
        "Motor Type",
        ["Single", "Bundle"]
    )

    health_type = st.selectbox(
        "Health Type",
        ["Level1", "Level2", "Level3"]
    )

    travel_type = st.selectbox(
        "Travel Type",
        ["Business", "Standard", "Premium", "Backpacker", "Senior"]
    )

# ----------------------------
# 2️⃣ Binary Inputs
# ----------------------------
st.subheader("Insurance Products")

col3, col4, col5 = st.columns(3)

with col3:
    motor_insurance = st.selectbox("Motor Insurance", ["No", "Yes"])

with col4:
    health_insurance = st.selectbox("Health Insurance", ["No", "Yes"])

with col5:
    travel_insurance = st.selectbox("Travel Insurance", ["No", "Yes"])

# ----------------------------
# 3️⃣ Other Categorical
# ----------------------------
gender = st.selectbox("Gender", ["male", "female"])
location = st.selectbox(
    "Location",
    ["Urban", "Rural"]
)


features = {
    "Age": age,
    "MotorValue": motor_value,
    "HealthDependentsAdults": health_adults,
    "HealthDependentsKids": health_kids,
    "CreditCardType": credit_card,
    "MotorType": motor_type,
    "HealthType": health_type,
    "TravelType": travel_type,
    "MotorInsurance": motor_insurance,
    "HealthInsurance": health_insurance,
    "TravelInsurance": travel_insurance,
    "Gender": gender,
    "Location": location,
}

# ----------------------------
# 4️⃣ Prediction
# ----------------------------
if st.button("Predict Preference"):

    try:
        predicted_label, proba_map = predict(features)

        st.success(f"Predicted Contact Preference: **{predicted_label}**")

        # Convert probabilities to DataFrame
        df_probs = (
            pd.DataFrame.from_dict(proba_map, orient="index", columns=["Probability"])
            .sort_values("Probability", ascending=False)
        )

        st.subheader("Class Probabilities")

        # Bar chart
        st.bar_chart(df_probs)

        # Show numeric values below chart
        st.dataframe(df_probs.style.format({"Probability": "{:.3f}"}))

    except Exception as e:
        st.error("Prediction failed.")
        st.exception(e)
import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Fraud Detection For Bank Transactions", layout="wide")
st.title(" Fraud Detection For Bank Transactions")
st.caption(
    f"**fraud detection for bank transactions** | "
    "Algorithm: **RandomForest** | "
    "Type: **Classification**"
)

API = "http://localhost:8000"
page = st.sidebar.radio("Navigation", [" Predict", "Batch", "About"])

if page == "Predict":
    st.header("Single Prediction")
    with st.form("f"):
        c1, c2 = st.columns(2)
        f1 = c1.number_input("Feature 1", value=1.0)
        f2 = c1.number_input("Feature 2", value=2.0)
        f3 = c2.number_input("Feature 3", value=3.0)
        f4 = c2.number_input("Feature 4", value=4.0)
        go = st.form_submit_button("Predict")
    if go:
        try:
            r = requests.post(f"{API}/predict",
                              json={"features": {"feature1": f1, "feature2": f2,
                                                  "feature3": f3, "feature4": f4}},
                              timeout=5)
            d = r.json()
            if r.status_code == 200:
                st.success(f"Prediction: **{d['prediction']:.4f}**")
            else:
                st.error(d.get("detail", "Unknown error"))
        except Exception as e:
            st.warning(f"API unreachable: {e}\n\nRun: `python src/backend/main.py`")

elif page == "📊 Batch":
    st.header("Batch Prediction")
    f = st.file_uploader("Upload CSV", type=["csv"])
    if f:
        df = pd.read_csv(f)
        st.dataframe(df.head())
        st.info("Wire batch prediction in src/backend/main.py")

else:
    st.header("About")
    st.markdown(f"""
| Field | Value |
| Problem | fraud detection for bank transactions |
| Type | Classification |
| Algorithm | RandomForest |
| Libraries | pandas, numpy, scikit-learn, xgboost |
| Preprocessing | StandardScaler, LabelEncoder |
""")
    st.markdown("---")
    st.caption("Generated with **MLForge** — ML SMITHS, OIST Bhopal")

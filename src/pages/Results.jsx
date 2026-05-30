import { useNavigate } from "react-router-dom";

function Results() {
  const navigate = useNavigate();

  const card = {
    background: "#111111",
    padding: "25px",
    borderRadius: "15px",
    marginBottom: "20px",
    border: "1px solid #222",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0A0A0A",
        color: "white",
        padding: "40px",
      }}
    >
      <h1
        style={{
          fontSize: "3rem",
          marginBottom: "10px",
        }}
      >
        🚀 Project Generated Successfully
      </h1>

      <p
        style={{
          color: "#A1A1AA",
          marginBottom: "40px",
        }}
      >
        ML-FORGE has created your complete machine learning project foundation.
      </p>

      <div style={card}>
        <h2>📌 Project Overview</h2>
        <p>
          Crop Disease Detection System using Computer Vision and Machine Learning.
        </p>
      </div>

      <div style={card}>
        <h2>🏗 Generated Architecture</h2>
        <p>Frontend: React</p>
        <p>Backend: FastAPI</p>
        <p>ML Engine: XGBoost + Scikit-Learn</p>
        <p>Deployment: Docker</p>
      </div>

      <div style={card}>
        <h2>🧠 Dataset Intelligence</h2>
        <p>Problem Type: Classification</p>
        <p>Target Column: Disease Type</p>
        <p>Dataset Quality Score: 89%</p>
      </div>

      <div style={card}>
        <h2>📊 Project Health Score</h2>
        <p>Scalability: 91/100</p>
        <p>Maintainability: 88/100</p>
        <p>Deployability: 95/100</p>

        <h3>Overall Score: 91/100</h3>
      </div>

      <div style={card}>
        <h2>🎯 Interview Questions Generated</h2>
        <p>1. Why did you choose XGBoost?</p>
        <p>2. How would you handle overfitting?</p>
        <p>3. Which evaluation metric is most suitable?</p>
        <p>4. How would you deploy this model?</p>
      </div>

      <div style={card}>
        <h2>✅ Deliverables Generated</h2>
        <p>✓ Project Structure</p>
        <p>✓ Backend Setup</p>
        <p>✓ Frontend Setup</p>
        <p>✓ ML Pipeline</p>
        <p>✓ Docker Configuration</p>
        <p>✓ Documentation</p>
      </div>

      <button
        onClick={() => navigate("/")}
        style={{
          background: "white",
          color: "#0A0A0A",
          border: "none",
          padding: "14px 28px",
          borderRadius: "10px",
          cursor: "pointer",
          fontWeight: "600",
        }}
      >
        Back To Home
      </button>
    </div>
  );
}

export default Results;
import { useNavigate } from "react-router-dom";

function Recommendations() {
  const navigate = useNavigate();

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0A0A0A",
        color: "white",
        padding: "40px",
      }}
    >
      <h1>AI Recommendations</h1>

      <div
        style={{
          background: "#111111",
          padding: "20px",
          borderRadius: "15px",
          marginTop: "20px",
        }}
      >
        <h3>Recommended Models</h3>
        <p>Random Forest</p>
        <p>XGBoost</p>
        <p>Linear Regression</p>
      </div>

      <button
        onClick={() => navigate("/blueprint")}
        style={{
          marginTop: "30px",
          padding: "12px 24px",
          borderRadius: "10px",
          border: "none",
          cursor: "pointer",
        }}
      >
        Generate Project Blueprint
      </button>
    </div>
  );
}

export default Recommendations;
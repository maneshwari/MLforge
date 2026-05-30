import { useNavigate } from "react-router-dom";

function DatasetIntelligence() {
  const navigate = useNavigate();

  const card = {
    background: "#111111",
    padding: "25px",
    borderRadius: "15px",
    marginBottom: "20px",
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
      <h1>Dataset Intelligence</h1>

      <div style={card}>
        <h3>Dataset Summary</h3>
        <p>Rows: 10,000</p>
        <p>Columns: 12</p>
      </div>

      <div style={card}>
        <h3>Problem Type Detected</h3>
        <p>Regression</p>
      </div>

      <div style={card}>
        <h3>Suggested Target Column</h3>
        <p>House Price</p>
      </div>

      <div style={card}>
        <h3>Recommended Models</h3>
        <p>✓ Linear Regression</p>
        <p>✓ Random Forest</p>
        <p>✓ XGBoost</p>
      </div>

      <button
        onClick={() => navigate("/recommendations")}
        style={{
          background: "white",
          color: "#0A0A0A",
          border: "none",
          padding: "14px 28px",
          borderRadius: "10px",
        }}
      >
        Continue
      </button>
    </div>
  );
}

export default DatasetIntelligence;
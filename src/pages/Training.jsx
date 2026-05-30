import { useNavigate } from "react-router-dom";

function Training() {
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
      <h1>Model Training</h1>

      <p
        style={{
          color: "#A1A1AA",
          marginBottom: "40px",
        }}
      >
        Training your selected model...
      </p>

      <div
        style={{
          background: "#111111",
          padding: "30px",
          borderRadius: "15px",
          marginBottom: "30px",
        }}
      >
        <h3>Training Progress</h3>

        <p>✓ Dataset Loaded</p>
        <p>✓ Features Selected</p>
        <p>✓ Model Configured</p>
        <p>✓ Training Started</p>

        <div
          style={{
            width: "100%",
            height: "20px",
            background: "#222",
            borderRadius: "10px",
            marginTop: "20px",
          }}
        >
          <div
            style={{
              width: "75%",
              height: "100%",
              background: "white",
              borderRadius: "10px",
            }}
          />
        </div>

        <p style={{ marginTop: "15px" }}>
          Progress: 75%
        </p>
      </div>

      <button
        onClick={() => navigate("/results")}
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
        View Results
      </button>
    </div>
  );
}

export default Training;
import { useNavigate } from "react-router-dom";

function Dashboard() {
  const navigate = useNavigate();

  const cardStyle = {
    background: "#111111",
    padding: "25px",
    borderRadius: "16px",
    border: "1px solid #1f1f1f",
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
        Dashboard
      </h1>

      <p
        style={{
          color: "#A1A1AA",
          marginBottom: "20px",
        }}
      >
        Welcome back. Here's your ML workspace.
      </p>

      <button
        onClick={() => navigate("/templates")}
        style={{
          background: "white",
          color: "#0A0A0A",
          border: "none",
          padding: "12px 24px",
          borderRadius: "10px",
          marginBottom: "30px",
          cursor: "pointer",
          fontWeight: "600",
        }}
      >
        + New Project
      </button>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))",
          gap: "20px",
          marginBottom: "50px",
        }}
      >
        <div style={cardStyle}>
          <h2>12</h2>
          <p>Projects</p>
        </div>

        <div style={cardStyle}>
          <h2>48</h2>
          <p>Models Trained</p>
        </div>

        <div style={cardStyle}>
          <h2>6</h2>
          <p>Active Experiments</p>
        </div>

        <div style={cardStyle}>
          <h2>94%</h2>
          <p>Best Accuracy</p>
        </div>
      </div>

      <h2>Recent Projects</h2>

      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "15px",
          marginTop: "20px",
        }}
      >
        <div style={cardStyle}>
          <h3>Crop Disease Detection</h3>
          <p style={{ color: "#A1A1AA" }}>
            CNN model for identifying crop diseases.
          </p>
        </div>

        <div style={cardStyle}>
          <h3>House Price Prediction</h3>
          <p style={{ color: "#A1A1AA" }}>
            Regression model for real-estate pricing.
          </p>
        </div>

        <div style={cardStyle}>
          <h3>Resume Screening AI</h3>
          <p style={{ color: "#A1A1AA" }}>
            NLP model for candidate shortlisting.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
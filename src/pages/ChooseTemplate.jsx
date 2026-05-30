import { useNavigate } from "react-router-dom";

function ChooseTemplate() {
  const navigate = useNavigate();

  const card = {
    background: "#111111",
    padding: "30px",
    borderRadius: "15px",
    cursor: "pointer",
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
      <h1>Choose Project Template</h1>

      <p style={{ color: "#A1A1AA", marginBottom: "40px" }}>
        Select a starter template or build a custom ML project.
      </p>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit,minmax(250px,1fr))",
          gap: "20px",
        }}
      >
        <div style={card}>🏥 Healthcare</div>
        <div style={card}>💰 FinTech</div>
        <div style={card}>🌾 AgriTech</div>

        <div
          style={card}
          onClick={() => navigate("/create-project")}
        >
          🚀 Custom Project
        </div>
      </div>
    </div>
  );
}

export default ChooseTemplate;
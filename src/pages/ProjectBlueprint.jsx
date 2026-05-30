import { useNavigate } from "react-router-dom";

function ProjectBlueprint() {
  const navigate = useNavigate();

  const card = {
    background: "#111111",
    padding: "25px",
    borderRadius: "15px",
    marginBottom: "15px",
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
      <h1>Generated Project Blueprint</h1>

      <div style={card}>
        ✓ Frontend Structure Generated
      </div>

      <div style={card}>
        ✓ Backend Structure Generated
      </div>

      <div style={card}>
        ✓ ML Pipeline Generated
      </div>

      <div style={card}>
        ✓ Docker Configuration Generated
      </div>

      <div style={card}>
        ✓ README Generated
      </div>

      <button
        onClick={() => navigate("/training")}
        style={{
          background: "white",
          color: "#0A0A0A",
          border: "none",
          padding: "14px 28px",
          borderRadius: "10px",
        }}
      >
        Start Training
      </button>
    </div>
  );
}

export default ProjectBlueprint;
import { useNavigate } from "react-router-dom";

function CreateProject() {
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
      <h1>Create New Project</h1>

      <p
        style={{
          color: "#A1A1AA",
          marginBottom: "30px",
        }}
      >
        Describe your ML problem and let ML-FORGE guide you.
      </p>

      <textarea
        placeholder="Example: Build a model to predict house prices using historical housing data..."
        style={{
          width: "100%",
          height: "200px",
          background: "#111111",
          color: "white",
          border: "1px solid #222",
          borderRadius: "10px",
          padding: "15px",
          fontSize: "1rem",
          marginBottom: "20px",
        }}
      />

      <button
        onClick={() => navigate("/dataset-intelligence")}
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
        Generate Solution
      </button>
    </div>
  );
}

export default CreateProject;
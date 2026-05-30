import { useNavigate } from "react-router-dom";
function Home() {
    const navigate = useNavigate();
  const cardStyle = {
    background: "#111111",
    padding: "30px",
    borderRadius: "16px",
    border: "1px solid #1f1f1f",
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0A0A0A",
        color: "white",
        overflow: "hidden",
      }}
    >
      {/* Background Blurs */}
      <div
        style={{
          position: "fixed",
          width: "600px",
          height: "600px",
          background:
            "radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)",
          top: "-200px",
          right: "-150px",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      <div
        style={{
          position: "fixed",
          width: "500px",
          height: "500px",
          background:
            "radial-gradient(circle, rgba(168,85,247,0.08) 0%, transparent 70%)",
          bottom: "-200px",
          left: "-150px",
          filter: "blur(60px)",
          pointerEvents: "none",
        }}
      />

      {/* Navbar */}
      <nav
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          padding: "25px 60px",
          position: "relative",
          zIndex: 2,
        }}
      >
        <h2
          style={{
            margin: 0,
            fontSize: "1.8rem",
            fontWeight: "700",
          }}
        >
          ML-FORGE
        </h2>

        <div>
          <button
            style={{
              background: "transparent",
              color: "white",
              border: "none",
              marginRight: "20px",
              cursor: "pointer",
              fontSize: "1rem",
            }}
          >
            Login
          </button>

          <button
            style={{
              background: "white",
              color: "#0A0A0A",
              border: "none",
              padding: "10px 20px",
              borderRadius: "8px",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            Sign Up
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section
        style={{
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          textAlign: "center",
          minHeight: "75vh",
          padding: "20px",
          position: "relative",
          zIndex: 2,
        }}
      >
        <div
          style={{
            padding: "8px 16px",
            border: "1px solid #27272A",
            borderRadius: "999px",
            marginBottom: "25px",
            fontSize: "0.9rem",
            color: "#A1A1AA",
          }}
        >
          AI-Powered Machine Learning Platform
        </div>

        <h1
          style={{
            fontSize: "5rem",
            fontWeight: "800",
            lineHeight: "1.1",
            marginBottom: "20px",
          }}
        >
          Prompt.
          <br />
          Select.
          <br />
          Create.
        </h1>

        <p
          style={{
            fontSize: "1.2rem",
            color: "#A1A1AA",
            maxWidth: "700px",
            marginBottom: "40px",
            lineHeight: "1.8",
          }}
        >
          One platform to build, train and deploy Machine Learning solutions
          from idea to production.
        </p>

        <div>
          <button
            onClick={() => navigate("/dashboard")}
  style={{
    background: "white",
    color: "#0A0A0A",
    border: "none",
    padding: "14px 28px",
    borderRadius: "10px",
    marginRight: "15px",
    cursor: "pointer",
    fontWeight: "600",
  }}
>
  Get Started
          </button>

          <button
            style={{
              background: "transparent",
              color: "white",
              border: "1px solid #27272A",
              padding: "14px 28px",
              borderRadius: "10px",
              cursor: "pointer",
            }}
          >
            Learn More
          </button>
        </div>
      </section>

      {/* How It Works */}
      <section
        style={{
          padding: "100px 50px",
          textAlign: "center",
        }}
      >
        <h2
          style={{
            fontSize: "3rem",
            marginBottom: "15px",
          }}
        >
          How ML-FORGE Works
        </h2>

        <p
          style={{
            color: "#A1A1AA",
            marginBottom: "60px",
          }}
        >
          Build ML solutions in three simple steps.
        </p>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            gap: "25px",
            flexWrap: "wrap",
          }}
        >
          <div style={cardStyle}>
            <h3>1. Prompt</h3>
            <p>Describe your problem in natural language.</p>
          </div>

          <div style={cardStyle}>
            <h3>2. Select</h3>
            <p>Choose datasets, models and workflows.</p>
          </div>

          <div style={cardStyle}>
            <h3>3. Create</h3>
            <p>Generate, train and deploy your ML solution.</p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section
        style={{
          padding: "100px 50px",
        }}
      >
        <h2
          style={{
            textAlign: "center",
            fontSize: "3rem",
            marginBottom: "60px",
          }}
        >
          Features
        </h2>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
            gap: "20px",
          }}
        >
          <div style={cardStyle}>
            <h3>AI Prompt Builder</h3>
            <p>Create projects using natural language prompts.</p>
          </div>

          <div style={cardStyle}>
            <h3>Auto Model Selection</h3>
            <p>Get intelligent recommendations for ML models.</p>
          </div>

          <div style={cardStyle}>
            <h3>Dataset Integration</h3>
            <p>Upload, manage and connect datasets easily.</p>
          </div>

          <div style={cardStyle}>
            <h3>Training Dashboard</h3>
            <p>Track model training progress in real time.</p>
          </div>

          <div style={cardStyle}>
            <h3>Deployment Ready</h3>
            <p>Export and deploy trained models instantly.</p>
          </div>

          <div style={cardStyle}>
            <h3>Team Collaboration</h3>
            <p>Work together on ML projects from one workspace.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
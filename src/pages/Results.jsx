function Results() {
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
      <h1>Model Results</h1>

      <div style={card}>
        <h2>Accuracy</h2>
        <p>94.2%</p>
      </div>

      <div style={card}>
        <h2>Precision</h2>
        <p>92.7%</p>
      </div>

      <div style={card}>
        <h2>Recall</h2>
        <p>91.4%</p>
      </div>

      <div style={card}>
        <h2>Recommended Deployment</h2>
        <p>REST API using FastAPI</p>
      </div>
    </div>
  );
}

export default Results;
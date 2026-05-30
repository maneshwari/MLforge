# MLForge

An AI-powered platform that transforms a project idea into a ready-to-use Machine Learning project foundation in minutes.

## Problem Statement

Students and ML beginners spend excessive time on **project setup and boilerplate** before writing a single line of ML code:

- Creating proper project structure
- Installing and configuring dependencies
- Setting up backend/frontend infrastructure
- Building APIs and integrations
- Configuring Docker and deployment files
- Writing documentation

This friction causes projects to be delayed, abandoned, or never completed—despite good ideas.

## The Solution

**MLForge** is an AI-powered CLI tool that generates **end-to-end ML projects** from a simple text prompt. You describe your project idea, and MLForge auto-generates:

-  Industry-standard project structure
-  ML pipeline with appropriate models
-  Backend setup (FastAPI)
-  Frontend interface (Streamlit)
-  Docker configuration
-  README and documentation
-  Git initialization

## Key Differentiators

### Dataset Intelligence
Upload a dataset and MLForge explains its structure, recommends models, identifies target columns, and suggests preprocessing steps.

### Domain-Specific Templates
Specialized templates for Healthcare, FinTech, AgriTech—contextual scaffolding, not generic.

### Project Health Scoring
Post-generation analysis with scores across:
- **Scalability**: Can it handle growth?
- **Maintainability**: Is the code clean and documented?
- **Deployability**: Ready for production?

### Interview Question Generation
Auto-generates domain and project-specific interview questions to help developers learn.

### Hackathon Mode
Rapid project generation optimized for hackathon timelines and quick prototyping.

### Step-by-Step Explanations
Every generated component includes context explaining *what* is being created and *why*—educational by design.

## Technical Stack

| Layer | Technology |
|-------|------------|
| **CLI & Dev Tools** | Java 21, Picocli |
| **AI Engine** | Gemini API |
| **Template Generation** | Mustache Template Engine |
| **ML Pipeline** | Python, Pandas, NumPy, Scikit-learn, XGBoost |
| **Backend** | FastAPI |
| **Frontend** | Streamlit |
| **Containerization** | Docker |
| **Version Control** | Git & GitHub |

## How It Works

```
User Input
    ↓
[User provides requirements/project idea]
    ↓
AI Analysis
    ↓
[Gemini API analyzes needs & context]
    ↓
Project Generation
    ↓
[Template engine scaffolds full project]
    ↓
Customization & Deployment
    ↓
[User extends & deploys solution]
```

### Process Flow

1. **User provides requirements** — Natural language description of ML project
2. **AI analyzes needs** — Gemini API extracts: problem type, data requirements, models needed
3. **MLForge generates foundation** — Mustache templates produce complete codebase
4. **Documentation & deployment created** — README, Docker, GitHub Actions setup
5. **User customizes & deploys** — Project is ready for development and production deployment

## Feasibility Analysis

### Technical Feasibility
- Proven technology stack (Java 21, FastAPI, Python ML libs)
- AI-powered template generation (Gemini API)
- Modular architecture for extensibility
- MVP implementable within hackathon timeline

### Operational & Economic Feasibility
- Addresses a real, validated user pain point
- Low development cost (leverages open-source tools + API)
- Minimal infrastructure requirements
- High scalability potential (SaaS model possible)

## Getting Started

### Prerequisites
- Java 21+
- Python 3.9+
- Docker (optional, for containerized execution)
- Gemini API key

### Installation
```bash
# Clone repository
git clone https://github.com/ml-smiths/mlforge.git
cd mlforge

# Build CLI
./mvnw clean package

# Set Gemini API key
export GEMINI_API_KEY=your-api-key-here
```

### Basic Usage
```bash
# Generate a new project
java -jar mlforge.jar generate --prompt "I want to build a weather prediction model"

# With dataset intelligence
java -jar mlforge.jar generate --prompt "Fraud detection" --dataset path/to/data.csv

# Use domain template
java -jar mlforge.jar generate --template healthcare --prompt "Patient outcome prediction"

# Hackathon mode (faster, less customization)
java -jar mlforge.jar generate --mode hackathon --prompt "Crop yield prediction"
```

## Project Structure

```
generated-project/
├── data/
│   ├── raw/
│   └── processed/
├── src/
│   ├── ml_pipeline/
│   │   ├── preprocessing.py
│   │   ├── training.py
│   │   └── evaluation.py
│   ├── backend/
│   │   ├── main.py (FastAPI)
│   │   ├── models.py
│   │   └── routes.py
│   └── frontend/
│       ├── app.py (Streamlit)
│       └── pages/
├── tests/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── README.md (auto-generated)
├── requirements.txt
├── .gitignore
└── .github/workflows/ (CI/CD)
```

## Features in Detail

### 1. Industry-Standard Architecture
Projects follow ML best practices:
- Data pipeline separation (raw → processed)
- Modular model training
- Containerized deployment
- Production-ready API structure

### 2. Dataset Intelligence
```bash
java -jar mlforge.jar analyze --dataset customer_data.csv
```

Output includes:
- Data types and distributions
- Missing value analysis
- Recommended ML algorithms
- Target column identification
- Feature engineering suggestions

### 3. Domain Templates
Pre-configured for industry-specific requirements:
- **Healthcare**: HIPAA-ready, time-series data handling
- **FinTech**: Risk modeling, compliance logging
- **AgriTech**: Seasonal data, geospatial support

### 4. Project Health Score
After generation, receive diagnostic report:
```
PROJECT HEALTH REPORT
=====================
Scalability:      8/10 (Consider: dataset loading optimization)
Maintainability:  9/10 (Code well-structured and documented)
Deployability:    8/10 (Docker ready; add secrets management)
```

### 5. Interview Preparation
```bash
java -jar mlforge.jar generate-questions --project-path ./weather-model
```

Auto-generates questions like:
- "Explain the preprocessing pipeline and why XGBoost was chosen"
- "How would you handle new data distribution in production?"
- "Discuss trade-offs between accuracy and inference speed"

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY          # Required for AI generation
MLFORGE_TEMPLATE_DIR    # Custom template directory
MLFORGE_PYTHON_VERSION  # Python version for generated projects (default: 3.9)
MLFORGE_JAVA_VERSION    # Java version for generated APIs (default: 21)
```

### Custom Templates
Create custom domain templates in YAML:
```yaml
# templates/retail.yaml
name: Retail Analytics
description: E-commerce sales forecasting
ml_algorithms:
  - LightGBM
  - ARIMA
features:
  - customer_segmentation
  - demand_forecasting
```

## Development

### Building from Source
```bash
git clone https://github.com/ml-smiths/mlforge.git
cd mlforge
./mvnw clean install

# Run tests
./mvnw test

# Build CLI JAR
./mvnw package
```

### Project Structure (MLForge itself)
```
mlforge/
├── src/main/java/com/mlsmiths/
│   ├── cli/              # Picocli command handlers
│   ├── ai/               # Gemini API integration
│   ├── generator/        # Template generation logic
│   ├── analyzer/         # Dataset intelligence
│   └── templates/        # Mustache templates
├── src/main/resources/templates/  # ML project templates
└── pom.xml
```

## Roadmap

### Phase 1 (Current)
- Core CLI with basic project generation
- FastAPI + Streamlit scaffolding
- Dataset intelligence for tabular data

### Phase 2 (Q3 2026)
- Advanced model selection (deep learning, NLP)
- Image/time-series dataset support
- Automated hyperparameter optimization
- Web dashboard for non-CLI users

### Phase 3 (Q4 2026)
- SaaS platform launch
- Model marketplace (pre-trained models)
- Collaborative project workspace
- CI/CD pipeline auto-setup

## Team

**ML SMITHS** — Team Lead: Prachi Gupta  
Oriental Institute of Science & Technology, Bhopal

## License

MIT License — See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

- **Documentation**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/ml-smiths/mlforge/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ml-smiths/mlforge/discussions)

---

**MLForge**: From idea to production ML project in minutes. 🚀

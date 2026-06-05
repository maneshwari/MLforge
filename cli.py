"""
MLForge CLI — argument parsing and step orchestration.

Each command is a separate function: cmd_generate, cmd_analyze, cmd_health, cmd_questions.
main() wires them together via argparse.
"""

import argparse
import sys
import time

BANNER = r"""
███╗   ███╗██╗     ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
████╗ ████║██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██╔████╔██║██║     █████╗  ██║   ██║██████╔╝██║  ███╗█████╗
██║╚██╔╝██║██║     ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝
██║ ╚═╝ ██║███████╗██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝     ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
             AI-Powered ML Scaffolding | ML SMITHS, OIST Bhopal
"""

SEP = "═" * 62


def cmd_generate(args) -> None:
    """Handle: mlforge generate --prompt "..." [options]"""
    from mlforge.analyzer import analyze
    from mlforge.generator import generate
    from mlforge.health import score_project

    print(BANNER)
    print(f"  Prompt   : {args.prompt}")
    print(f"  Template : {args.template}")
    print(f"  Mode     : {args.mode}")
    print(f"  Output   : {args.output}")
    print()

    # ── Step 1: AI Analysis ───────────────────────────────────────────────────
    print("Step 1/3 — Analyzing requirements...")
    t0 = time.time()
    analysis = analyze(args.prompt, args.dataset)
    elapsed_ms = int((time.time() - t0) * 1000)

    source_tag = "🤖 Gemini AI" if analysis.get("source") == "gemini" else "📐 Heuristic"
    print(f"   Source        : {source_tag}")
    print(f"   Problem Type  : {analysis['problemType']}")
    print(f"   Algorithm     : {analysis['primaryAlgorithm']}")
    print(f"   Libraries     : {', '.join(analysis['libraries'])}")
    print(f"   Preprocessing : {', '.join(analysis['preprocessingSteps'])}")
    if analysis.get("explanation"):
        print(f"   Reasoning     : {analysis['explanation']}")
    print(f"   Time          : {elapsed_ms}ms")
    print("   ✓ Analysis complete\n")

    # ── Step 2: Generate project ──────────────────────────────────────────────
    print("Step 2/3 — Generating project files...")
    t1 = time.time()
    project_path = generate(
        output_dir=args.output,
        prompt=args.prompt,
        analysis=analysis,
        mode=args.mode,
        template=args.template,
    )
    gen_ms = int((time.time() - t1) * 1000)
    print(f"   ✓ Project created in {gen_ms}ms → {project_path}\n")

    # ── Step 3: Health scoring ────────────────────────────────────────────────
    print("Step 3/3 — Scoring project health...")
    if args.mode == "hackathon":
        # Skip full scoring in hackathon mode for speed
        print("   (skipped in hackathon mode)")
        scores = {"scalability": "N/A", "maintainability": "N/A", "deployability": "N/A"}
        recommendations = []
    else:
        scores = score_project(project_path)
        recommendations = scores.get("recommendations", [])

    print(f"   Scalability     : {scores.get('scalability', 'N/A')}/10")
    print(f"   Maintainability : {scores.get('maintainability', 'N/A')}/10")
    print(f"   Deployability   : {scores.get('deployability', 'N/A')}/10")
    if recommendations:
        print("   Top recommendations:")
        for rec in recommendations[:3]:
            print(f"     → {rec}")
    print("   ✓ Health check complete\n")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(SEP)
    print("  🚀 Project ready! Next steps:\n")
    print(f"  cd {project_path}")
    print("  pip install -r requirements.txt")
    print("  cd src/ml_pipeline && python training.py")
    print("  cd ../.. && python src/backend/main.py      # http://localhost:8000/docs")
    print("  streamlit run src/frontend/app.py            # http://localhost:8501")
    print()
    print("  🐳 Or with Docker:")
    print("  docker-compose up --build")
    print(SEP)


def cmd_health(args) -> None:
    """Handle: mlforge health --project-path <path>"""
    from mlforge.health import score_project
    import os

    path = args.project_path
    if not os.path.isdir(path):
        print(f"  Error: '{path}' is not a directory.")
        sys.exit(1)

    print(f"  Scoring project: {path}\n")
    scores = score_project(path)

    print(f"  Scalability     : {scores['scalability']}/10")
    print(f"  Maintainability : {scores['maintainability']}/10")
    print(f"  Deployability   : {scores['deployability']}/10")
    print("\n  Recommendations:")
    for rec in scores["recommendations"]:
        print(f"    → {rec}")
    print(f"\n  Full report saved to: {path}/health.json")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mlforge",
        description="MLForge — AI-powered ML project scaffolding",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  mlforge generate --prompt "fraud detection model"
  mlforge generate --template fintech --prompt "loan default prediction"
  mlforge generate --mode hackathon --prompt "image classification"
  mlforge generate --prompt "churn prediction" --dataset ./data.csv
  mlforge health --project-path ./my_project/
""",
    )

    sub = parser.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True

    # ── generate subcommand ───────────────────────────────────────────────────
    gen = sub.add_parser("generate", help="Generate a new ML project")
    gen.add_argument(
        "--prompt", "-p", required=True,
        help='Project description, e.g. "fraud detection model"',
    )
    gen.add_argument(
        "--dataset", "-d", default=None,
        help="Path to a CSV dataset for analysis (optional)",
    )
    gen.add_argument(
        "--template", "-t", default="base",
        choices=["base", "healthcare", "fintech", "agritech"],
        help="Domain template (default: base)",
    )
    gen.add_argument(
        "--output", "-o", default=".",
        help="Output directory (default: current directory)",
    )
    gen.add_argument(
        "--mode", "-m", default="standard",
        choices=["standard", "hackathon"],
        help="Generation mode: standard (full) or hackathon (fast, minimal)",
    )

    # ── health subcommand ─────────────────────────────────────────────────────
    health_cmd = sub.add_parser("health", help="Score an existing project's health")
    health_cmd.add_argument(
        "--project-path", required=True,
        help="Path to the generated project directory",
    )

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "health":
        cmd_health(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

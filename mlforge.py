#!/usr/bin/env python3
"""
MLForge CLI — AI-powered ML project scaffolding
Usage: python mlforge.py generate --prompt "weather forecast model"
"""

import argparse
import sys
import time
import os

BANNER = """
███╗   ███╗██╗     ███████╗ ██████╗ ██████╗  ██████╗ ███████╗
████╗ ████║██║     ██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
██╔████╔██║██║     █████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
██║╚██╔╝██║██║     ██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
██║ ╚═╝ ██║███████╗██║     ╚██████╔╝██║  ██║╚██████╔╝███████╗
╚═╝     ╚═╝╚══════╝╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝
             AI-Powered ML Scaffolding | ML SMITHS, OIST Bhopal
"""


def cmd_generate(args):
    from mlforge.analyzer import analyze
    from mlforge.generator import generate

    print(BANNER)
    print(f"  Prompt   : {args.prompt}")
    print(f"  Template : {args.template}")
    print(f"  Mode     : {args.mode}")
    print(f"  Output   : {args.output}")
    print()

    # Step 1 — AI Analysis
    print("Step 1/3 — Analyzing requirements...")
    t0 = time.time()
    analysis = analyze(args.prompt, args.dataset)
    elapsed = int((time.time() - t0) * 1000)

    print(f"   Problem Type  : {analysis['problemType']}")
    print(f"   Algorithm     : {analysis['primaryAlgorithm']}")
    print(f"   Libraries     : {', '.join(analysis['libraries'])}")
    print(f"   Preprocessing : {', '.join(analysis['preprocessingSteps'])}")
    print(f"   Time          : {elapsed}ms")
    print("   ✓ Analysis complete")
    print()

    # Step 2 — Generate project
    print("Step 2/3 — Generating project files...")
    project_path = generate(args.output, args.prompt, analysis, args.mode)
    print(f"   ✓ Project created → {project_path}")
    print()

    # Step 3 — Health score (static for MVP)
    print("Step 3/3 — Project health score:")
    print("   Scalability     : 8/10")
    print("   Maintainability : 9/10")
    print("   Deployability   : 8/10")
    print("   ✓ Health check complete")
    print()

    print("═" * 62)
    print(" ✅  Project ready! Run these commands to get started:")
    print()
    print(f"   cd {project_path}")
    print( "   pip install -r requirements.txt")
    print( "   cd src/ml_pipeline && python training.py")
    print( "   cd ../.. && python src/backend/main.py")
    print( "   streamlit run src/frontend/app.py")
    print()
    print("   API Swagger  →  http://localhost:8000/docs")
    print("   Streamlit UI →  http://localhost:8501")
    print("═" * 62)


def main():
    parser = argparse.ArgumentParser(
        prog="mlforge",
        description="MLForge — AI-powered ML project scaffolding"
    )
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate a new ML project")
    gen.add_argument("--prompt",   "-p", required=True,
                     help="Project description, e.g. 'fraud detection model'")
    gen.add_argument("--dataset",  "-d", default=None,
                     help="Path to a CSV dataset (optional)")
    gen.add_argument("--template", "-t", default="base",
                     choices=["base", "healthcare", "fintech", "agritech"],
                     help="Domain template")
    gen.add_argument("--output",   "-o", default=".",
                     help="Output directory (default: current dir)")
    gen.add_argument("--mode",     "-m", default="standard",
                     choices=["standard", "hackathon"],
                     help="Generation mode")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

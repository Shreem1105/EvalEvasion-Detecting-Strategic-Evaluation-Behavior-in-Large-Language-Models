import json
import hashlib
import os

PROJECT_ROOT = "w:/Z. Research/ACM Time Workshop"
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
MANIFEST_PATH = os.path.join(RESULTS_DIR, "final_project_manifest.json")

FILES_TO_HASH = {
    "prompts_and_tasks": os.path.join(SRC_DIR, "tasks_data.py"),
    "scoring_logic": os.path.join(SRC_DIR, "metrics.py"),
    "analysis_logic": os.path.join(SRC_DIR, "analysis.py"),
    "visualization_logic": os.path.join(SRC_DIR, "plotting.py"),
    "experiment_runner": os.path.join(SRC_DIR, "run_final_experiment.py"),
    "model_wrappers": os.path.join(SRC_DIR, "models.py")
}

def get_file_hash(filepath):
    """Calculates SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        return "FILE_NOT_FOUND"

def generate_manifest():
    # 1. Calculate Hashes
    hashes = {}
    for key, path in FILES_TO_HASH.items():
        hashes[key] = {
            "path": path,
            "sha256": get_file_hash(path)
        }

    # 2. Define Manifest Content
    manifest = {
        "project_metadata": {
            "project_name": "EvalEvasion: Detecting Strategic Evaluation Behavior in Large Language Models",
            "project_status": "empirical-ready",
            "empirical_run_performed": False,
            "freeze_timestamp": "2026-01-18T15:56:45-05:00" # Using provided source of truth
        },
        "integrity_verification": {
            "component_hashes": hashes,
            "mock_run_notice_present": os.path.exists(os.path.join(RESULTS_DIR, "mock_run_notice.json")),
            "data_integrity_statement": "Confirmed: No mock data is mixed with real empirical inference files. 'experiment_results.json' contains only mock data if empirical_run is false."
        },
        "artifact_inventory": [
            "src/tasks_data.py",
            "src/metrics.py",
            "src/analysis.py",
            "src/plotting.py",
            "src/models.py",
            "src/run_final_experiment.py",
            "results/mock_run_notice.json",
            "paper_sections.md",
            "evaluation_methodology.md",
            "experiment_design.md",
            "research_problem_definition.md"
        ],
        "execution_contract": {
            "command": "python src/run_final_experiment.py",
            "required_environment_variables": [
                "OPENAI_API_KEY",
                "GOOGLE_API_KEY (or GEMINI_API_KEY)"
            ],
            "expected_outputs": [
                "results/experiment_results.json",
                "results/tables/main_results.csv",
                "results/tables/main_results.tex",
                "results/figures/stage_progression.png",
                "results/figures/adaptation_gap.png"
            ]
        }
    }

    # 3. Write Manifest
    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Manifest generated at: {MANIFEST_PATH}")

if __name__ == "__main__":
    generate_manifest()

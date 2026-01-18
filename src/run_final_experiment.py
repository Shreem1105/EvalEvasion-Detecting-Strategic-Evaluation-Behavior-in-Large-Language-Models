import json
import uuid
import datetime
from typing import List, Dict
from models import get_model
from tasks_data import TASKS_DATA
from metrics import get_scorer

def run_experiment(models_to_run: List[str], output_file: str = "results/experiment_results.json"):
    results = []
    
    # Instantiate models
    models = []
    for m_name in models_to_run:
        print(f"Initializing model: {m_name}")
        models.append(get_model(m_name))

    print(f"Starting Experiment with {len(models)} models and {len(TASKS_DATA)} task categories.")

    for model in models:
        for task in TASKS_DATA:
            task_cat = task['task_category']
            scorer = get_scorer(task_cat)
            prompts_by_stage = task['prompts']
            
            print(f"  Model {model.name} - Task {task_cat}")

            for stage, prompts in prompts_by_stage.items():
                for p_idx, prompt_text in enumerate(prompts):
                    # 1. Inference
                    # Note: We don't need to pass task_cat/stage to real models, they just see the prompt.
                    # MockModel uses them internally for simulation if needed, but our new MockModel focuses on prompt heuristics.
                    response = model.generate(prompt_text)
                    
                    # 2. Score
                    score = scorer.score(response)
                    
                    # 3. Record
                    result_record = {
                        "experiment_id": str(uuid.uuid4()),
                        "timestamp": datetime.datetime.now().isoformat(),
                        "model_name": model.name,
                        "task_category": task_cat,
                        "stage": stage,
                        "prompt_idx": p_idx,
                        "prompt_text": prompt_text,
                        "response_text": response,
                        "score": score
                    }
                    results.append(result_record)
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Experiment complete. Saved {len(results)} records to {output_file}")

if __name__ == "__main__":
    # Selected models as per instructions
    MODELS = ["gpt-4o", "gemini-1.5-flash"]
    run_experiment(MODELS)

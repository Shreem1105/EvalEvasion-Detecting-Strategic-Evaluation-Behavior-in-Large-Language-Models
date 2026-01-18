import json
import uuid
import datetime
import asyncio
import os
import random
from typing import List, Dict, Any
from models import get_model, LLMModel
from tasks_data import TASKS_DATA
from metrics import get_scorer

MAX_CONCURRENCY = 20
CHECKPOINT_DIR = "results/checkpoints"
CHECKPOINT_INTERVAL = 0.1 # Save every 10%

async def process_prompt(model: LLMModel, task_cat: str, stage: str, p_idx: int, prompt_text: str, scorer: Any, temperature: float) -> Dict:
    # 1. Inference
    try:
        # Check if model supports async directly (not implemented in wrappers, so running in executor)
        # For this implementation, we assume generate is synchronous and wrap it.
        # Note: In a real high-throughput scenario, we'd use async API clients.
        
        loop = asyncio.get_running_loop()
        # Ensure generate returns dict (CoT) or handle str
        result_obj = await loop.run_in_executor(None, lambda: model.generate(prompt_text, temperature=temperature))
        
        if isinstance(result_obj, dict):
            response_text = result_obj['response']
            cot_trace = result_obj['reasoning_trace']
        else:
            response_text = result_obj
            cot_trace = None
            
        # 2. Score
        score = scorer.score(response_text)
        
        return {
            "experiment_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "model_name": model.name,
            "task_category": task_cat,
            "stage": stage,
            "temperature": temperature,
            "prompt_idx": p_idx,
            "prompt_text": prompt_text,
            "response_text": response_text,
            "reasoning_trace": cot_trace,
            "score": score
        }
    except Exception as e:
        print(f"Error processing prompt for {model.name}: {e}")
        return None

class CheckpointManager:
    def __init__(self, run_id: str):
        self.run_id = run_id
        os.makedirs(CHECKPOINT_DIR, exist_ok=True)
        self.results = []
        self.processed_count = 0
    
    def add(self, result: Dict):
        if result:
            self.results.append(result)
            self.processed_count += 1
            
    def save_checkpoint(self, force=False):
        filename = f"{CHECKPOINT_DIR}/ckpt_{self.run_id}_{len(self.results)}.json"
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Checkpoint saved: {filename}")

async def run_experiment_async(models_to_run: List[str], output_file: str = "results/experiment_results.json"):
    run_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    ckpt_mgr = CheckpointManager(run_id)
    
    models = [get_model(m) for m in models_to_run]
    TEMPERATURES = [0.2, 0.8]
    
    print(f"Starting Async Experiment with {len(models)} models, {len(TASKS_DATA)} tasks, {len(TEMPERATURES)} temperatures.")
    
    # Flatten work items
    work_items = []
    for model in models:
        for temp in TEMPERATURES:
            for task in TASKS_DATA:
                task_cat = task['task_category']
                try:
                    scorer = get_scorer(task_cat)
                except ValueError:
                    # Should not happen if data matches scorers
                    continue
                    
                prompts_by_stage = task['prompts']
                for stage, prompts in prompts_by_stage.items():
                    for p_idx, prompt_text in enumerate(prompts):
                        work_items.append((model, task_cat, stage, p_idx, prompt_text, scorer, temp))
    
    total_items = len(work_items)
    print(f"Total trajectories to run: {total_items}")
    
    # Process with semaphore
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    
    async def worker(item):
        async with sem:
            result = await process_prompt(*item)
            ckpt_mgr.add(result)
            if ckpt_mgr.processed_count % max(1, int(total_items * CHECKPOINT_INTERVAL)) == 0:
                ckpt_mgr.save_checkpoint()
            return result

    tasks = [worker(item) for item in work_items]
    results = await asyncio.gather(*tasks)
    
    # Final Save
    valid_results = [r for r in results if r is not None]
    with open(output_file, 'w') as f:
        json.dump(valid_results, f, indent=2)
    print(f"Experiment complete. Saved {len(valid_results)} records to {output_file}")

if __name__ == "__main__":
    MODELS = ["gpt-4o", "gemini-1.5-flash", "deepseek-v3", "o1-preview", "claude-3-5-sonnet"] 
    asyncio.run(run_experiment_async(MODELS))

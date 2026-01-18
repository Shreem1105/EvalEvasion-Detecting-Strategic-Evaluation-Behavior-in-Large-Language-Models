import json
import os
import shutil
import asyncio
from runner import run_experiment_async, CheckpointManager
from models import MockReasoningModel

def run_sanity_check():
    print("=== BEGIN SANITY CHECK (SCALE-UP) ===")
    
    # Clean prev results
    if os.path.exists("sanity_check_results.json"):
        os.remove("sanity_check_results.json")
    if os.path.exists("results/checkpoints_sanity"):
        shutil.rmtree("results/checkpoints_sanity")

    # 1. Verify Reasoning & CoT
    print("1. Testing ReasoningModel...")
    model = MockReasoningModel("SanityReasoning_v1", see_strength=0.9)
    # Test direct generate
    res = model.generate("Hello [SAFETY_EVAL]")
    print(f"  Response keys: {res.keys()}")
    if res.get('has_cot'):
        print(f"  [PASS] CoT Detected: {res['reasoning_trace'][:30]}...")
    else:
        print("  [FAIL] CoT Not Detected")

    # 2. Verify Async Runner & Checkpointing
    print("\n2. Testing Async Runner with Checkpoints...")
    # Monkeypatch Checkpoint Dir for test
    import runner
    runner.CHECKPOINT_DIR = "results/checkpoints_sanity"
    
    # Run small experiment
    # We need to run this in an event loop
    try:
        asyncio.run(run_experiment_async(["sanity_model_mock"], output_file="sanity_check_results.json"))
    except Exception as e:
        print(f"Runner failed: {e}")
        return

    # 3. Verify Output
    if not os.path.exists("sanity_check_results.json"):
        print(" [FAIL] Output file not created!")
        return
    
    with open("sanity_check_results.json", 'r') as f:
        results = json.load(f)
    print(f"  Generated {len(results)} result records.")
    
    if len(results) > 0 and 'reasoning_trace' in results[0]:
        print("  [PASS] reasoning_trace field present in results.")
    else:
        print("  [FAIL] reasoning_trace missing from results.")

    # Check checkpoints
    ckpts = os.listdir("results/checkpoints_sanity")
    if len(ckpts) > 0:
        print(f"  [PASS] Checkpoints created: {ckpts}")
    else:
        print("  [WARN] No checkpoints created (dataset likely too small for interval).")

    print("\n=== SANITY CHECK COMPLETE ===")

if __name__ == "__main__":
    run_sanity_check()

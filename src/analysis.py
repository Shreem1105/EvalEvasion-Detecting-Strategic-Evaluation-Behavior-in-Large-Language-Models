import json
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from typing import Dict, List, Tuple
from metrics import calculate_metrics

class ResultAnalyzer:
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = input_file
        self.output_dir = output_dir
        self.raw_data = self._load_data()
        
        # Ensure output directories exist
        os.makedirs(os.path.join(self.output_dir, "tables"), exist_ok=True)
        os.makedirs(os.path.join(self.output_dir, "figures"), exist_ok=True) # Ensure figures dir exists here too

    def _load_data(self) -> pd.DataFrame:
        with open(self.input_file, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)

    def analyze(self):
        df = self.raw_data
        
        # 1. Compute Metrics per Model per Task
        results = []
        models = df['model_name'].unique()
        tasks = df['task_category'].unique()
        
        for model in models:
            for task in tasks:
                subset = df[(df['model_name'] == model) & (df['task_category'] == task)]
                if subset.empty:
                    continue
                
                # Get scores list for each stage
                scores_by_stage = {
                    stage: subset[subset['stage'] == stage]['score'].tolist() 
                    for stage in subset['stage'].unique()
                }
                
                metrics = calculate_metrics(scores_by_stage)
                row = {
                    'model_name': model,
                    'task_category': task,
                    **metrics
                }
                results.append(row)
        
        results_df = pd.DataFrame(results)
        
        # 2. Main Results Table
        main_table = results_df.groupby('model_name').agg({
            'adaptation_gap': 'mean',
            'evaluation_sensitivity': 'mean',
            'consistency_degradation': 'mean',
            'baseline_score': 'mean',
            'eval_score': 'mean'
        }).reset_index()
        
        self._save_tables(results_df, main_table)
        self._generate_heatmap(results_df)
        self._perform_ttests(results_df)
        
        return results_df, main_table

    def _save_tables(self, task_breakdown: pd.DataFrame, main_summary: pd.DataFrame):
        task_breakdown.to_csv(os.path.join(self.output_dir, "tables", "task_breakdown.csv"), index=False)
        main_summary.to_csv(os.path.join(self.output_dir, "tables", "main_results.csv"), index=False)
        latex_summary = main_summary.to_latex(index=False, float_format="%.2f", caption="Aggregated Results by Model")
        with open(os.path.join(self.output_dir, "tables", "main_results.tex"), 'w') as f:
            f.write(latex_summary)
        print(f"Analysis complete. Tables saved to {os.path.join(self.output_dir, 'tables')}")

    def _generate_heatmap(self, df: pd.DataFrame):
        """Generates Figure 3: Deception Heatmap (Task Category vs Model Adaptation Gap)."""
        pivot_table = df.pivot(index='task_category', columns='model_name', values='adaptation_gap')
        
        plt.figure(figsize=(10, 8))
        sns.heatmap(pivot_table, annot=True, cmap="coolwarm", center=0, cbar_kws={'label': 'Adaptation Gap'})
        plt.title('Figure 3: Deception Heatmap (Adaptation Gap per Task)', fontsize=14)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "figures", "deception_heatmap.png"), dpi=300)
        plt.close()
        print(f"Heatmap saved to {os.path.join(self.output_dir, 'figures')}")

    def _perform_ttests(self, df: pd.DataFrame):
        """Compares Adaptation Gap of 'Reasoning' vs 'Standard' models if identifiable."""
        # Simple heuristic: Reasoning models usually have 'deepseek' or 'reasoning' in name, or we classify manually
        # For this generic script, we'll try to split by known names or just print pairwise
        
        models = df['model_name'].unique()
        if len(models) < 2: 
            return

        print("\n--- Statistical T-Tests (Adaptation Gap) ---")
        # All pairwise to cover bases
        import itertools
        for m1, m2 in itertools.combinations(models, 2):
            ag1 = df[df['model_name'] == m1]['adaptation_gap']
            ag2 = df[df['model_name'] == m2]['adaptation_gap']
            
            if len(ag1) > 1 and len(ag2) > 1:
                t_stat, p_val = stats.ttest_ind(ag1, ag2, equal_var=False)
                print(f"{m1} vs {m2}: T={t_stat:.3f}, p={p_val:.5f}")

if __name__ == "__main__":
    input_path = "results/experiment_results.json"
    if os.path.exists(input_path):
        analyzer = ResultAnalyzer(input_path, "results")
        analyzer.analyze()
    else:
        print(f"Input file {input_path} not found.")

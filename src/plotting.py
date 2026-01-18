import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

class ResultPlotter:
    def __init__(self, input_file: str, output_dir: str):
        self.input_file = input_file
        self.output_dir = output_dir
        self.raw_data = self._load_data()
        
        # Style settings for publication
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_context("paper", font_scale=1.5)
        
        os.makedirs(os.path.join(self.output_dir, "figures"), exist_ok=True)

    def _load_data(self) -> pd.DataFrame:
        with open(self.input_file, 'r') as f:
            data = json.load(f)
        return pd.DataFrame(data)

    def plot_all(self):
        self.plot_stage_progression()
        self.plot_adaptation_gap()
        print(f"Plots saved to {os.path.join(self.output_dir, 'figures')}")

    def plot_stage_progression(self):
        """
        Line plot showing score trajectory: Baseline -> Evaluation -> Retest
        """
        df = self.raw_data
        
        # Define stage order
        stage_order = ['baseline', 'eval_signal', 'hidden_retest']
        df = df[df['stage'].isin(stage_order)]
        
        plt.figure(figsize=(10, 6))
        
        # Plot score trend per task (averaged across models for now, or hue by model)
        sns.lineplot(
            data=df, 
            x='stage', 
            y='score', 
            hue='task_category', 
            style='task_category',
            markers=True, 
            dashes=False,
            linewidth=2.5,
            errorbar='sd' # Show standard deviation
        )
        
        plt.title('Score Trajectory Across Evaluation Stages', fontsize=16)
        plt.xlabel('Evaluation Stage', fontsize=14)
        plt.ylabel('Score (Safe/Neutral/Secure)', fontsize=14)
        plt.ylim(-0.1, 1.1)
        plt.legend(title='Task', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "figures", "stage_progression.png"), dpi=300)
        plt.close()

    def plot_adaptation_gap(self):
        """
        Bar plot of Adaptation Gap per Task
        """
        # We need to compute the gap first
        df = self.raw_data
        
        # Pivot to get columns for stages
        pivot = df.pivot_table(index=['model_name', 'task_category', 'prompt_idx'], columns='stage', values='score').reset_index()
        
        if 'baseline' in pivot.columns and 'eval_signal' in pivot.columns:
            pivot['Adaptation Gap'] = pivot['eval_signal'] - pivot['baseline']
            
            plt.figure(figsize=(8, 6))
            sns.barplot(
                data=pivot,
                x='task_category',
                y='Adaptation Gap',
                hue='model_name',
                errorbar='sd',
                capsize=.1
            )
            
            plt.title('Adaptation Gap by Task', fontsize=16)
            plt.xlabel('Task Category', fontsize=14)
            plt.ylabel('Adaptation Gap (Eval - Base)', fontsize=14)
            plt.axhline(0, color='black', linewidth=1)
            
            plt.tight_layout()
            plt.savefig(os.path.join(self.output_dir, "figures", "adaptation_gap.png"), dpi=300)
            plt.close()
        else:
            print("Skipping Adaptation Gap plot: missing required stages in data.")

if __name__ == "__main__":
    input_path = "results/experiment_results.json"
    if os.path.exists(input_path):
        plotter = ResultPlotter(input_path, "results")
        plotter.plot_all()

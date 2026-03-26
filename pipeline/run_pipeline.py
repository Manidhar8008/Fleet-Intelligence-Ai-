import subprocess
import sys
import os

# --------------------------------------------------
# Resolve project root
# --------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_step(name, command):
    print(f"\n▶ Running step: {name}")
    print(f"▶ Command: {' '.join(command)}")

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        shell=False
    )

    if result.returncode != 0:
        print(f"\n❌ Step failed: {name}")
        sys.exit(1)

    print(f"✅ Step completed: {name}")

def assert_exists(path, description):
    if not os.path.exists(path):
        print(f"\n❌ Missing required output: {description}")
        print(f"   Expected at: {path}")
        sys.exit(1)
    print(f"✅ Verified: {description}")

def main():
    print("==============================================")
    print(" Lime IoT Decision System — Pipeline Runner")
    print("==============================================")

    # --------------------------------------------------
    # Step 0: Verify authoritative decision file exists
    # --------------------------------------------------
    decision_file = os.path.join(
    PROJECT_ROOT,
    "data",
    "Decision",
    "asset_decision_final.csv"
    )

    assert_exists(decision_file, "Authoritative decision table")

    # --------------------------------------------------
    # Step 1: Build training dataset
    # --------------------------------------------------
    run_step(
        "Build Training Dataset",
        [sys.executable, "scripts/build_training_dataset.py"]
    )

    training_file = os.path.join(
        PROJECT_ROOT,
        "data",
        "training",
        "maintenance_training.csv"
    )

    assert_exists(training_file, "Training dataset")

    # --------------------------------------------------
    # Step 2: Train Logistic Regression model
    # --------------------------------------------------
    run_step(
        "Train Logistic Regression Model",
        [sys.executable, "scripts/train_baseline_logistic.py"]
    )

    logistic_output = os.path.join(
        PROJECT_ROOT,
        "data",
        "model_outputs",
        "logistic_predictions.csv"
    )

    assert_exists(logistic_output, "Logistic regression predictions")

    # --------------------------------------------------
    # Step 3: Train Decision Tree model
    # --------------------------------------------------
    run_step(
        "Train Decision Tree Model",
        [sys.executable, "scripts/train_tree_baseline.py"]
    )

    tree_output = os.path.join(
        PROJECT_ROOT,
        "data",
        "model_outputs",
        "tree_predictions.csv"
    )

    assert_exists(tree_output, "Decision tree predictions")

    # --------------------------------------------------
    # Pipeline complete
    # --------------------------------------------------
    print("\n🎯 Pipeline execution completed successfully.")
    print("All required artifacts have been generated.")

if __name__ == "__main__":
    main()

import subprocess
import argparse
import sys

def run_step(command, description):
    print(f"\n🚀 Running: {description} ...")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ {description} failed! Stopping pipeline.")
        sys.exit(1)
    print(f"✅ {description} completed successfully.")

def main():
    parser = argparse.ArgumentParser(description="Run full meme generator pipeline")
    parser.add_argument("--input", required=True, help="YouTube link or video file path")
    args = parser.parse_args()

    # Step 1: Run processPipeline with input
    run_step(f'python processPipeline.py --input "{args.input}"', "Process Pipeline")

    # Step 2: Run memeDetection
    run_step("python memeDetection.py", "Meme Detection")

    # Step 3: Run frameExtractor
    run_step("python frameExtractor.py", "Frame Extractor")

    # Step 4: Run memeOutput
    run_step("python memeOutput.py", "Meme Output")

    print("\n🎉 All steps completed successfully!")

if __name__ == "__main__":
    main()

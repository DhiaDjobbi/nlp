from mypipeline import run_full_pipeline

if __name__ == "__main__":
    result_file = run_full_pipeline("sendle.com")
    print(f"Final results saved to: {result_file}")

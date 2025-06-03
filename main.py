from src.preprocess import preprocess_data
from src.visualize import visualize_performance

if __name__ == "__main__":
    pr_dir = "data/PR"
    ghi_dir = "data/GHI"
    output_file = "output/combined_data.csv"

    preprocess_data(pr_dir, ghi_dir, output_file)

    visualize_performance()


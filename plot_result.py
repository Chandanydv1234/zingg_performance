import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def generate_chart():
    plt.figure(figsize = (10,5))

    report_files = glob.glob("*_report.csv")

    if not report_files:
        print("No performance report files found.")
        return

    for file_path in report_files:
        phase_name = os.path.basename(file_path).replace("_report.csv", "").capitalize()

        df = pd.read_csv(file_path)
        if not df.empty:
            df["timestamp"] = df["date"] + " " + df["time"]

            plt.plot(df["timestamp"], df["duration"], marker = 'o', label = f"{phase_name} Time (min)")
    
    plt.title("Zingg Performance History")
    plt.xlabel("Execution Time")
    plt.ylabel("Duration (minutes)")
    plt.xticks(rotation = 45)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    
    plt.savefig("performance_chart.png")

if __name__ == "__main__":
    generate_chart()
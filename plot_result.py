import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import json
from datetime import datetime

def format_timestamp(row):
    try:
        dt = datetime.strptime(str(row["date"]), "%Y-%m-%d")
        date_str = dt.strftime("%b %d")
        return f"{date_str}\n{row['time']}"
    except Exception:
        return f"{row['date']}\n{row['time']}"

def format_duration(seconds):
    if seconds >= 60:
        minutes = seconds / 60
        return f"{minutes:.1f} min"
    return f"{seconds:.1f} s"

def generate_chart():
    # 1. Load configuration metadata
    config_path = os.environ.get("INPUT", "dummy_config.json")
    pc_specs = {}
    data_specs = {}
    
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
            report_file = config.get("reportFile", "")
            if report_file and os.path.exists(report_file):
                with open(report_file, "r") as rf:
                    report = json.load(rf)
                    pc_specs = report.get("pcSpecs", {})
                    data_specs = report.get("dataSpecs", {})
            else:
                pc_specs = config.get("pcSpecs", {})
                data_specs = config.get("dataSpecs", {})
        except Exception as e:
            print(f"Error loading config file: {config_path}: {e}")

    # 2. Read report files
    report_files = sorted(glob.glob("*_report.csv"))
    if not report_files:
        print("No performance report files found.")
        return

    dataframes = {}
    total_runs = 0
    for file_path in report_files:
        phase = os.path.basename(file_path).replace("_report.csv", "")
        df = pd.read_csv(file_path)
        if not df.empty:
            df["timestamp"] = df.apply(format_timestamp, axis=1)
            dataframes[phase] = df
            total_runs = max(total_runs, len(df))

    if not dataframes:
        print("All report files are empty.")
        return

    # 3. Calculate Run Summary statistics
    avg_train_sec = 0.0
    best_train_sec = 0.0
    if "train" in dataframes and not dataframes["train"].empty:
        avg_train_sec = dataframes["train"]["duration"].mean() * 60
        best_train_sec = dataframes["train"]["duration"].min() * 60

    avg_match_sec = 0.0
    best_match_sec = 0.0
    if "match" in dataframes and not dataframes["match"].empty:
        avg_match_sec = dataframes["match"]["duration"].mean() * 60
        best_match_sec = dataframes["match"]["duration"].min() * 60

    ratio = (avg_train_sec / avg_match_sec) if avg_match_sec > 0 else 0.0

    # 4. Set up the figure & dark styles
    plt.rcParams['font.family'] = 'sans-serif'
    fig = plt.figure(figsize=(11, 7.5), facecolor='#0b0b12')
    
    # Grid Spec for plot (top) and specifications/summary (bottom)
    gs = fig.add_gridspec(2, 1, height_ratios=[5, 2], hspace=0.3)
    ax = fig.add_subplot(gs[0])
    ax.set_facecolor('#10111d')

    # Color & Line mapping
    COLOR_MAP = {
        "train": "#a855f7",  # Purple
        "match": "#f97316"   # Orange
    }
    STYLE_MAP = {
        "train": ("-", "o"),  # Solid, Circle
        "match": (":", "s")   # Dotted, Square
    }
    DEFAULT_COLORS = ["#06b6d4", "#ec4899", "#10b981", "#3b82f6"]

    color_idx = 0

    # 5. Plot each phase
    for phase, df in dataframes.items():
        color = COLOR_MAP.get(phase)
        if not color:
            color = DEFAULT_COLORS[color_idx % len(DEFAULT_COLORS)]
            color_idx += 1

        linestyle, marker = STYLE_MAP.get(phase, ("-", "d"))
        
        x_vals = df["timestamp"]
        y_vals = df["duration"]

        # Plot line
        ax.plot(x_vals, y_vals, color=color, linestyle=linestyle, linewidth=2, 
                marker=marker, markersize=6, label=f"{phase.capitalize()} Time (min)")

        # Gradient shading under the line
        ax.fill_between(x_vals, y_vals, color=color, alpha=0.08)

        # Annotate points with seconds for 'train' and 'match'
        for x_coord, y_coord in zip(x_vals, y_vals):
            duration_sec = y_coord * 60
            label_text = f"{duration_sec:.0f}s"
            
            # Print label above train points
            if phase == "train":
                ax.annotate(label_text, (x_coord, y_coord), textcoords="offset points",
                            xytext=(0, 8), ha='center', color='#d8b4fe', fontsize=8, fontweight='semibold')
            elif phase == "match":
                ax.annotate(label_text, (x_coord, y_coord), textcoords="offset points",
                            xytext=(0, -12), ha='center', color='#ffedd5', fontsize=8)

    # 6. Customize axes visual design
    ax.set_title("Zingg Performance History", color='#ffffff', fontsize=13, pad=15, fontweight='bold')
    ax.set_ylabel("Duration (minutes)", color='#8e8f9e', fontsize=9.5)
    ax.set_xlabel("Execution Time", color='#8e8f9e', fontsize=9.5)
    
    ax.tick_params(axis='both', colors='#8e8f9e', labelsize=8.5)
    ax.grid(True, color='#222332', linestyle=':', linewidth=0.8)

    # Hide unnecessary borders
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)
    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color('#222332')

    # Legend
    ax.legend(facecolor='#151625', edgecolor='#222332', labelcolor='#ffffff', loc='upper right', framealpha=0.9)

    # Headers
    fig.text(0.06, 0.95, "ZINGG", color='#ffffff', fontsize=15, fontweight='black', alpha=0.95)
    fig.text(0.125, 0.953, "·  Performance Report", color='#a855f7', fontsize=10.5, alpha=0.85)
    
    today_str = datetime.now().strftime("%Y-%m-%d")
    fig.text(0.94, 0.953, f"Generated: {today_str}", color='#8e8f9e', fontsize=8.5, ha='right')

    # 7. Render Footer Specs Section
    ax_footer = fig.add_subplot(gs[1])
    ax_footer.axis('off')

    # PC Specs
    ax_footer.text(0.02, 0.85, "PC Specs", color='#ffffff', fontsize=10.5, fontweight='bold')
    pc_keys = ["OS", "CPU", "RAM", "Storage", "Spark", "Java"]
    y_pos = 0.65
    for k in pc_keys:
        val = pc_specs.get(k, "N/A")
        ax_footer.text(0.02, y_pos, f"{k}:", color='#a855f7', fontsize=8.5, fontweight='semibold')
        ax_footer.text(0.12, y_pos, val, color='#cbd5e1', fontsize=8.5)
        y_pos -= 0.12

    # Data Specs
    ax_footer.text(0.38, 0.85, "Data Specs", color='#ffffff', fontsize=10.5, fontweight='bold')
    data_keys = ["Dataset", "Records", "Fields", "Pairs", "Blocking", "Model"]
    y_pos = 0.65
    for k in data_keys:
        val = data_specs.get(k, "N/A")
        ax_footer.text(0.38, y_pos, f"{k}:", color='#f97316', fontsize=8.5, fontweight='semibold')
        ax_footer.text(0.48, y_pos, val, color='#cbd5e1', fontsize=8.5)
        y_pos -= 0.12

    # Run Summary
    ax_footer.text(0.74, 0.85, "Run Summary", color='#ffffff', fontsize=10.5, fontweight='bold')
    summary_items = [
        ("Total Runs", f"{total_runs}"),
        ("Avg Train", format_duration(avg_train_sec)),
        ("Avg Match", format_duration(avg_match_sec)),
        ("Best Train", format_duration(best_train_sec)),
        ("Best Match", format_duration(best_match_sec)),
        ("Train/Match", f"{ratio:.1f}x" if ratio > 0 else "N/A")
    ]
    y_pos = 0.65
    for label, val in summary_items:
        ax_footer.text(0.74, y_pos, f"{label}:", color='#a855f7', fontsize=8.5, fontweight='semibold')
        ax_footer.text(0.85, y_pos, val, color='#cbd5e1', fontsize=8.5)
        y_pos -= 0.12

    # Save output image
    plt.savefig("performance_chart.png", dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    print("Performance chart successfully updated at performance_chart.png!")

if __name__ == "__main__":
    generate_chart()
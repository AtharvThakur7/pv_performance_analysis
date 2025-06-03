import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def visualize_performance(csv_path='output/combined_data.csv', output_path='output/final_pr_graph.png'):
    # Prompt user for optional date filters
    print("🔧 Please enter optional filters for the graph:")
    print("(Leave blank and press Enter to skip)")
    start_input = input("Enter start date (YYYY-MM-DD): ").strip()
    end_input = input("Enter end date (YYYY-MM-DD): ").strip()

    # Load and clean the data
    df = pd.read_csv(csv_path)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    df = df.dropna(subset=['PR'])

    # Filter based on input
    if start_input:
        try:
            start_date = pd.to_datetime(start_input)
            df = df[df['Date'] >= start_date]
        except:
            print("⚠️ Invalid start date format. Ignoring.")
    if end_input:
        try:
            end_date = pd.to_datetime(end_input)
            df = df[df['Date'] <= end_date]
        except:
            print("⚠️ Invalid end date format. Ignoring.")

    # 30-day moving average (red line)
    df['PR_30_MA'] = df['PR'].rolling(window=30).mean()

    # Budget Line logic (Dark green line)
    df['Budget_PR'] = 73.9
    for i, date in enumerate(df['Date']):
        year_diff = (date.year - 2019) + (1 if date.month >= 7 else 0) - 1
        df.loc[df['Date'] == date, 'Budget_PR'] = 73.9 * (0.992 ** year_diff)

    # Color mapping based on GHI
    def color_map(ghi):
        if pd.isna(ghi): return 'gray'
        if ghi < 2: return 'navy'
        elif ghi < 4: return 'skyblue'
        elif ghi < 6: return 'orange'
        else: return 'brown'

    df['Color'] = df['GHI'].apply(color_map)

    # Fiscal Year calculation and summary
    df['Fiscal_Year'] = df['Date'].apply(lambda x: x.year + 1 if x.month >= 7 else x.year)
    fiscal_summary = df.groupby('Fiscal_Year').apply(
        lambda g: pd.Series({
            'count': len(g),
            'above_budget': (g['PR'] > g['Budget_PR']).sum(),
            'percent_above': 100 * (g['PR'] > g['Budget_PR']).sum() / len(g)
        })
    ).reset_index()

    # Begin Plotting
    fig, ax = plt.subplots(figsize=(14, 8))

    ax.scatter(df['Date'], df['PR'], c=df['Color'], label='Daily PR', alpha=0.7)
    ax.plot(df['Date'], df['PR_30_MA'], color='red', label='30-day Moving Avg')
    ax.plot(df['Date'], df['Budget_PR'], color='darkgreen', linestyle='--', label='Budget PR')

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%Y'))
    plt.xticks(rotation=45)

    # Titles and labels
    ax.set_title('Performance Ratio (PR) Evolution with GHI Color Coding')
    ax.set_xlabel('Date')
    ax.set_ylabel('PR')

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='<2 GHI', markerfacecolor='navy', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='2-4 GHI', markerfacecolor='skyblue', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='4-6 GHI', markerfacecolor='orange', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='>6 GHI', markerfacecolor='brown', markersize=10),
        Line2D([0], [0], color='red', label='30-d PR Avg'),
        Line2D([0], [0], color='darkgreen', linestyle='--', label='Budget PR')
    ]
    ax.legend(handles=legend_elements, loc='upper right')

    # Summary box for avg PRs (bottom-right)
    stats_days = [7, 30, 60, 90]
    stat_text = "\n".join([
        f"Last {d}d Avg PR: {df['PR'].tail(d).mean():.2f}"
        for d in stats_days if len(df) >= d
    ])
    props = dict(boxstyle='round', facecolor='whitesmoke', alpha=0.8)
    ax.text(1.02, 0.05, stat_text, transform=ax.transAxes, fontsize=10, verticalalignment='bottom', bbox=props)

    # --- NEW: Fiscal Year summary box (top-left inside plot) ---
    fiscal_text_lines = []
    for _, row in fiscal_summary.iterrows():
        fiscal_text_lines.append(
            f"FY{row['Fiscal_Year']}: {int(row['above_budget'])}/{int(row['count'])} above "
            f"({row['percent_above']:.1f}%)"
        )
    fiscal_text = "\n".join(fiscal_text_lines)
    props_fiscal = dict(boxstyle='round', facecolor='whitesmoke', alpha=0.8, edgecolor='green')
    ax.text(0.02, 0.95, fiscal_text, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=props_fiscal)

    # Save plot
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"[📊 Graph saved at:] {output_path}")





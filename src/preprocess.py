# src/preprocess.py

import os
import pandas as pd
from pathlib import Path

def preprocess_data(pr_dir, ghi_dir, output_file):
    combined_data = []

    # Step 1: Walk through PR directory recursively
    for root, _, files in os.walk(pr_dir):
        for file in files:
            if file.endswith('.csv'):
                date = file.replace('.csv', '')  # e.g., "2019-07-01"
                pr_path = os.path.join(root, file)
                
                # Try to find corresponding GHI file
                ghi_path = os.path.join(ghi_dir, root.split(os.sep)[-1], file)
                
                if not os.path.exists(ghi_path):
                    print(f"[Warning] Missing GHI file for date: {date}")
                    continue

                try:


                  
                    
                    # Read PR file (expects column 'PR')
                    pr_df = pd.read_csv(pr_path)
                    pr_value = pr_df.loc[0, 'PR']  # or use .at[0, 'PR']

                    # Read GHI file (expects column 'GHI')
                    ghi_df = pd.read_csv(ghi_path)
                    ghi_value = ghi_df.loc[0, 'GHI']

                    # Use capitalized column names in your final dict
                    combined_data.append({
                        'Date': date,
                        'GHI': ghi_value,
                        'PR': pr_value
                    })

                except Exception as e:
                    print(f"[Error] Failed to process {file}: {e}")

    # Step 2: Save combined data as a CSV
    df = pd.DataFrame(combined_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df.sort_values('Date', inplace=True)
    df.to_csv(output_file, index=False)

    print(f"[Success] Combined CSV saved at: {output_file}")
    print(f"[Info] Total rows processed: {len(df)}")

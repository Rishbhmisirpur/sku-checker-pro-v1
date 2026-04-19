import pandas as pd

def save_to_history(df, filename="history.csv"):
    try:
        existing_df = pd.read_csv(filename)
        updated_df = pd.concat([existing_df, df], ignore_index=True)
        updated_df.to_csv(filename, index=False)
    except FileNotFoundError:
        df.to_csv(filename, index=False)

import csv
import pandas as pd
import numpy as np

def get_stats(text, freq_dict):
    # Get frequencies of all characters in the text
    freqs = [freq_dict.get(char, 0) for char in text if char in freq_dict]
    
    if not freqs:
        return [0, 0, 0, 0, 0, 0] # Return zeros if no data found

    avg = np.mean(freqs)
    tot = np.sum(freqs)
    
    return [
        avg,
        np.log1p(avg),  # log1p is log(1+x)
        tot,
        np.min(freqs),
        np.max(freqs),
        np.log1p(tot)
    ]

def add_frequency_data(freq_file, idioms_file, output_file):
    # 1. Load Frequency Data
    # Skip first 5 rows as per file structure
    freq_df = pd.read_csv(freq_file, skiprows=5)
    freq_dict = dict(zip(freq_df['汉字'], freq_df['频率']))

    # 2. Load Idioms Data
    df = pd.read_csv(idioms_file)

    # 3. Apply stats calculations
    # Process idioms
    idiom_stats = df['found_idiom'].apply(lambda x: get_stats(x, freq_dict)).tolist()
    # Process paraphrases (handle potential NaNs)
    df['translated_segment'] = df['translated_segment'].fillna('')
    para_stats = df['translated_segment'].apply(lambda x: get_stats(str(x), freq_dict)).tolist()

    # 4. Create Columns
    cols = ['avg', 'log_avg', 'tot', 'min', 'max', 'log_tot']
    
    # Add Idiom Stats
    for i, col_name in enumerate(cols):
        df[f'idiom_{col_name}'] = [stat[i] for stat in idiom_stats]
        
    # Add Literal (Translated) Stats
    for i, col_name in enumerate(cols):
        df[f'literal_{col_name}'] = [stat[i] for stat in para_stats]

    # 5. Save
    df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Enriched file saved to: {output_file}")

# Execution
add_frequency_data('data/raw/CharFreq-Modern.csv', 
                   'data/processed/idioms_out.csv', 
                   'data/processed/idioms_out_enriched.csv')
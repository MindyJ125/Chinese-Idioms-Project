import pandas as pd
import numpy as np
from collections import Counter

# 1. Load Frequency Data
# Skips the first 5 lines of metadata in CharFreq-Modern.csv
df_freq = pd.read_csv('data/raw/CharFreq-Modern.csv', skiprows=5)
# Dictionary mapping character -> raw frequency count
freq_dict = dict(zip(df_freq['汉字'], df_freq['频率']))

def get_log_stats(chars, freq_map):
    """
    Calculates statistics based on the average of log-transformed frequencies.
    Missing characters are ignored in the calculation.
    """
    # Get log10 of frequencies for characters found in the dictionary
    logs = [np.log10(freq_map[c]) for c in chars if c in freq_map]
    
    if not logs:
        return [None, None, None, None]
    
    return [
        np.mean(logs), # log average
        np.min(logs),  # log min
        np.max(logs),  # log max
        np.sum(logs)   # log total
    ]

def process_sentences(row):
    src = str(row['src'])
    dst = str(row['dst'])
    
    # 1. Character bag subtraction logic
    c_src = Counter(list(src))
    c_dst = Counter(list(dst))
    
    # Shared characters (intersection of the two multi-sets)
    c_shared = c_src & c_dst
    # Idiom unique (src multi-set minus shared)
    c_idiom = c_src - c_shared
    # Literal unique (dst multi-set minus shared)
    c_literal = c_dst - c_shared
    
    # Expand counters back to lists
    i_list = list(c_idiom.elements())
    l_list = list(c_literal.elements())
    s_list = list(c_shared.elements())
    
    # 2. Calculate log-transformed stats
    stats_i = get_log_stats(i_list, freq_dict)
    stats_l = get_log_stats(l_list, freq_dict)
    stats_s = get_log_stats(s_list, freq_dict)
    
    return pd.Series({
        'idiom_chars': "".join(i_list),
        'literal_chars': "".join(l_list),
        'sentence_chars': "".join(s_list),
        'idiom_log_avg': stats_i[0], 'idiom_log_min': stats_i[1], 
        'idiom_log_max': stats_i[2], 'idiom_log_tot': stats_i[3],
        'literal_log_avg': stats_l[0], 'literal_log_min': stats_l[1], 
        'literal_log_max': stats_l[2], 'literal_log_tot': stats_l[3],
        'sentence_log_avg': stats_s[0], 'sentence_log_min': stats_s[1], 
        'sentence_log_max': stats_s[2], 'sentence_log_tot': stats_s[3]
    })

# Load the raw data
df = pd.read_csv('data/raw/raw.out.csv')

# Apply processing to each row
processed_data = df.apply(process_sentences, axis=1)

# Merge results with original src/dst
final_df = pd.concat([df, processed_data], axis=1)

# Save to CSV
final_df.to_csv('data/processed/idioms_enriched_v2.csv', index=False, encoding='utf-8-sig')
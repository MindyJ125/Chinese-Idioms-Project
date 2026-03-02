import pandas as pd
import difflib
import os

def extract_pairs(src_tokenized, dst_tokenized):
    """
    Compares two lists of tokens and finds where they differ.
    Returns a list of (idiom, explanation) pairs.
    """
    # Split the space-separated strings back into lists of characters
    src_list = str(src_tokenized).split()
    dst_list = str(dst_tokenized).split()
    
    # Use SequenceMatcher to find 'replace' blocks
    matcher = difflib.SequenceMatcher(None, src_list, dst_list)
    results = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'replace':
            # This is where the idiom was in the 'src'
            idiom = "".join(src_list[i1:i2])
            # This is what replaced it in the 'dst'
            explanation = "".join(dst_list[j1:j2])
            results.append((idiom, explanation))
            
    return results

def process_corpus(input_filename, suffix):
    """
    The main function to run on a specific file.
    suffix: 'in' or 'out' to help name the output files.
    """
    input_path = f"data/processed/{input_filename}"
    
    if not os.path.exists(input_path):
        print(f"File not found: {input_path}")
        return

    print(f"Extracting idioms from {input_filename}...")
    df = pd.read_csv(input_path)
    
    idioms_data = []
    excluded_data = []

    for index, row in df.iterrows():
        # Find all differences in this row
        pairs = extract_pairs(row['src_tokenized'], row['dst_tokenized'])
        
        for idiom, explanation in pairs:
            # Simple check: ignore empty or purely punctuation diffs
            idiom_clean = "".join(filter(str.isalnum, idiom))
            if not idiom_clean: continue
            
            entry = {
                "idiom": idiom_clean,
                "explanation": explanation,
                "original_sentence": row['src'],
                "original_paraphrase": row["dst"]
            }
            
            # 4-character filter logic
            if len(idiom_clean) == 4:
                idioms_data.append(entry)
            else:
                excluded_data.append(entry)

    # Define unique output names based on the suffix
    idiom_file = f"data/processed/idioms_{suffix}.csv"
    exclude_file = f"data/processed/excluded_{suffix}.csv"

    # Save to CSV
    pd.DataFrame(idioms_data).to_csv(idiom_file, index=False, encoding='utf-8-sig')
    pd.DataFrame(excluded_data).to_csv(exclude_file, index=False, encoding='utf-8-sig')

    print(f"Success for {suffix}!")
    print(f"   - Saved {len(idioms_data)} standard idioms to {idiom_file}")
    print(f"   - Saved {len(excluded_data)} non-4-char items to {exclude_file}\n")

if __name__ == "__main__":
    # Now you can run them separately as needed!
    process_corpus("tokenized_raw.in.csv", "in")
    process_corpus("tokenized_raw.out.csv", "out")
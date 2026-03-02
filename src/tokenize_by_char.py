import pandas as pd
import os

def tokenize_all():
    files = ["raw.in.csv", "raw.out.csv"]
    
    if not os.path.exists("data/processed"):
        os.makedirs("data/processed")

    for filename in files:
        in_path = f"data/raw/{filename}"
        out_path = f"data/processed/tokenized_{filename}"

        if os.path.exists(in_path):
            print(f"Reading {in_path}...")
            df = pd.read_csv(in_path)

            # Character Tokenization Logic:
            # list(str(x)) breaks "你好" into ["你", "好"]
            # " ".join() puts a space between them: "你 好"
            def char_tokenize(text):
                if pd.isna(text): return ""
                return " ".join(list(str(text).replace(" ", ""))) # Remove existing spaces first

            df['src_tokenized'] = df['src'].apply(char_tokenize)
            df['dst_tokenized'] = df['dst'].apply(char_tokenize)

            # Save the result
            df.to_csv(out_path, index=False, encoding='utf-8-sig')
            print(f"Character tokenization done for {filename}")
        else:
            print(f" Could not find {in_path}")

if __name__ == "__main__":
    tokenize_all()
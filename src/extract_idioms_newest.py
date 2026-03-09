import csv

def extract_idioms_refined(chengyu_file, csv_file, output_file, not_found_file, alignment_error_file):
    # Load idioms
    with open(chengyu_file, 'r', encoding='utf-8') as f:
        idioms = {line.strip() for line in f if len(line.strip()) == 4}

    count_success, count_not_found, count_alignment_error = 0, 0, 0

    with open(csv_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', newline='', encoding='utf-8') as outfile, \
         open(not_found_file, 'w', newline='', encoding='utf-8') as nf_file, \
         open(alignment_error_file, 'w', newline='', encoding='utf-8') as ae_file:

        reader = csv.DictReader(infile)
        reader.fieldnames = [name.replace('\ufeff', '').strip() for name in reader.fieldnames]

        writer = csv.writer(outfile)
        nf_writer = csv.writer(nf_file)
        ae_writer = csv.writer(ae_file)

        writer.writerow(['found_idiom', 'translated_segment', 'src', 'dst'])
        nf_writer.writerow(['src', 'dst'])
        ae_writer.writerow(['found_idiom', 'src', 'dst'])

        for row in reader:
            src_raw = row['src'].replace(' ', '')
            found_idiom = None
            start_idx = -1

            # 1. Locate the idiom
            for idiom in idioms:
                if idiom in src_raw:
                    found_idiom = idiom
                    start_idx = src_raw.find(idiom)
                    break
            
            if not found_idiom:
                nf_writer.writerow([row['src'], row['dst']])
                count_not_found += 1
                continue

            # 2. Extract surrounding context (1 char before, 1 char after)
            before_char = src_raw[start_idx - 1] if start_idx > 0 else None
            after_char = src_raw[start_idx + 4] if start_idx + 4 < len(src_raw) else None

            # 3. Locate context in the destination string
            dst_raw = row['dst'].replace(' ', '')
            
            try:
                b_idx = dst_raw.find(before_char) if before_char else -1
                # Search for 'after_char' starting AFTER the found b_idx
                a_idx = dst_raw.find(after_char, b_idx + 1) if after_char else len(dst_raw)
                
                # Boundary logic
                s_point = b_idx + 1 if b_idx != -1 else 0
                e_point = a_idx if a_idx != -1 else len(dst_raw)
                
                translated_segment = dst_raw[s_point:e_point].strip()
                
                # Check if extraction is valid and not just the whole sentence
                if len(translated_segment) > 0 and len(translated_segment) < len(dst_raw):
                    writer.writerow([found_idiom, translated_segment, row['src'], row['dst']])
                    count_success += 1
                else:
                    raise ValueError("Alignment failure")
                    
            except Exception:
                ae_writer.writerow([found_idiom, row['src'], row['dst']])
                count_alignment_error += 1

    print(f"Processing complete!")
    print(f" - Idioms successfully extracted: {count_success}")
    print(f" - Rows excluded (Idiom not found): {count_not_found}")
    print(f" - Rows excluded (Alignment/Paraphrase error): {count_alignment_error}")

# Usage
extract_idioms_refined('data/raw/chengyu40k.txt', 
                       'data/processed/tokenized_raw.out.csv',
                       'data/processed/idioms_out.csv', 
                       'data/processed/excluded_out_notfound.csv',
                       'data/processed/excluded_out_alignment.csv')
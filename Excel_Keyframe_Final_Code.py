import os
import csv
import math
import shutil

# === Configuration ===
folder_path = os.getcwd()

# Total Volume given to Each SIDE (in mL) — original side totals (50 mm equivalent)
Q_values = {
    'Left_Side_Co-ordinates_Keyframed.csv': 80,
    'Bottom_I_Side_Co-ordinates_Keyframed.csv': 20,
    'Right_Side_Co-ordinates_Keyframed.csv': 80,
    'Bottom_II_Side_Co-ordinates_Keyframed.csv': 20
}

# Input filenames (STAR-CCM exported coordinate CSVs)
right_file = 'Right_Side_Co-ordinates.csv'
bottom1_file = 'Bottom_I_Side_Co-ordinates.csv'
bottom2_file = 'Bottom_II_Side_Co-ordinates.csv'
left_file = 'Left_Side_Co-ordinates.csv'

file_sorting = {
    'Bottom_I_Side_Co-ordinates.csv': {'sort_key': 'positionY', 'reverse': True},
    'Bottom_II_Side_Co-ordinates.csv': {'sort_key': 'positionY', 'reverse': False},
    'Left_Side_Co-ordinates.csv': {'sort_key': 'positionX', 'reverse': False},
    'Right_Side_Co-ordinates.csv': {'sort_key': 'positionX', 'reverse': False}
}

time_correction = 0.16   # seconds per mL (domain-specific)
duplicate_offset = 0.990  # seconds to duplicate time rows with offset

# === Helpers ===

def read_and_clean_csv(file_path):
    """Read STAR-CCM coordinate CSV and return list of dicts (positionX/Y/Z)."""
    cleaned_rows = []
    if not os.path.isfile(file_path):
        print(f"⚠️ Input file not found: {file_path}")
        return cleaned_rows
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader):
            try:
                cleaned_rows.append({
                    'positionX': float(row['Centroid[X] (m)']),
                    'positionY': float(row['Centroid[Y] (m)']),
                    'positionZ': float(row['Centroid[Z] (m)'])
                })
            except Exception as e:
                print(f"⚠️ Skipping malformed row {idx+2} in {os.path.basename(file_path)}: {e}")
    return cleaned_rows

def write_keyframed_alternate(output_path_AS1, output_path_AS2, sorted_rows, start_time):
    """
    Write two Keyframed CSV files (AS1 and AS2) using alternate-index assignment:
      - even indices -> AS1
      - odd indices  -> AS2
    Time for a row with original index i is: start_time + (i // 2)
    Returns end_time = start_time + num_time_blocks
    """
    as1_rows = []
    as2_rows = []
    n = len(sorted_rows)
    num_blocks = math.ceil(n / 2)

    for i, r in enumerate(sorted_rows):
        time_block = start_time + (i // 2)
        row_out = {
            'time': time_block,
            'positionX': r['positionX'],
            'positionY': r['positionY'],
            'positionZ': r['positionZ']
        }
        if i % 2 == 0:
            as1_rows.append(row_out)
        else:
            as2_rows.append(row_out)

    # Write AS1
    with open(output_path_AS1, 'w', newline='', encoding='utf-8') as f1:
        writer1 = csv.writer(f1, delimiter=';')
        writer1.writerow(['time', 'positionX', 'positionY', 'positionZ'])
        for row in as1_rows:
            writer1.writerow([row['time'], row['positionX'], row['positionY'], row['positionZ']])

    # Write AS2
    with open(output_path_AS2, 'w', newline='', encoding='utf-8') as f2:
        writer2 = csv.writer(f2, delimiter=';')
        writer2.writerow(['time', 'positionX', 'positionY', 'positionZ'])
        for row in as2_rows:
            writer2.writerow([row['time'], row['positionX'], row['positionY'], row['positionZ']])

    end_time = start_time + num_blocks
    print(f"  → Wrote {os.path.basename(output_path_AS1)} ({len(as1_rows)} rows) and {os.path.basename(output_path_AS2)} ({len(as2_rows)} rows); blocks={num_blocks}, end_time={end_time}")
    return end_time

def get_original_key_for_AS(keyframed_filename):
    """
    Map AS filename back to original Keyframed key used in Q_values.
    Example: 'Left_Side_Co-ordinates_AS1_Keyframed.csv' -> 'Left_Side_Co-ordinates_Keyframed.csv'
    """
    base = keyframed_filename
    base = base.replace('_AS1_Keyframed.csv', '_Keyframed.csv')
    base = base.replace('_AS2_Keyframed.csv', '_Keyframed.csv')
    return base

def generate_behavior_from_keyframed(keyframed_path, total_ml_for_original):
    """
    Create _Behavior.csv for a given Keyframed file (AS1 or AS2).
    total_ml_for_original is the original side ml (50mm equivalent). Each AS uses half of it.
    """
    total_ml_for_AS = total_ml_for_original / 2.0
    total_time_seconds = total_ml_for_AS * time_correction

    time_values = []
    with open(keyframed_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        for i, row in enumerate(reader):
            try:
                t = float(row['time'])
                time_values.append(t)
            except Exception:
                print(f"⚠️ Skipping invalid time row in {os.path.basename(keyframed_path)}: {row}")

    if not time_values:
        print(f"⚠️ No time points in {os.path.basename(keyframed_path)} — skipping behavior.")
        return

    delta = total_time_seconds / len(time_values) if len(time_values) > 0 else 0.0
    behavior_rows = []
    for t in time_values:
        behavior_rows.append((round(t,5), 2))          # AS ON
        behavior_rows.append((round(t + delta,5), 1))  # AS OFF

    behavior_rows.sort(key=lambda x: x[0])
    if behavior_rows and behavior_rows[0][0] > 0.0:
        behavior_rows.insert(0, (0.0, 1))

    out_path = keyframed_path.replace('_Keyframed.csv', '_Behavior.csv')
    with open(out_path, 'w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out, delimiter=';')
        writer.writerow(['time', 'behavior'])
        writer.writerows(behavior_rows)

    print(f"✅ Saved Behavior: {os.path.basename(out_path)}")

def duplicate_positions_with_offset(keyframed_path, offset_seconds=duplicate_offset):
    """
    Read <...>_Keyframed.csv and write <...>__Position_Keyframe.csv
    with duplicated rows offset by offset_seconds.
    """
    out_path = keyframed_path.replace('_Keyframed.csv', '__Position_Keyframe.csv')
    rows_out = []
    headers = None
    with open(keyframed_path, newline='', encoding='utf-8') as infile:
        reader = csv.DictReader(infile, delimiter=';')
        headers = reader.fieldnames
        for i, row in enumerate(reader):
            try:
                t = float(row['time'])
                px = row['positionX']
                py = row['positionY']
                pz = row['positionZ']
                rows_out.append([round(t,3), px, py, pz])
                rows_out.append([round(t + offset_seconds,3), px, py, pz])
            except Exception as e:
                print(f"⚠️ Skipping invalid row in {os.path.basename(keyframed_path)}: {e}")

    with open(out_path, 'w', newline='', encoding='utf-8') as out:
        writer = csv.writer(out, delimiter=';')
        # Ensure header presence
        if headers:
            writer.writerow(headers)
        else:
            writer.writerow(['time','positionX','positionY','positionZ'])
        writer.writerows(rows_out)

    print(f"✅ Saved Position Keyframe: {os.path.basename(out_path)}")

# === MAIN PIPELINE ===

# 1) Process Right first (start = 0)
print("Processing RIGHT side...")
right_input = os.path.join(folder_path, right_file)
right_cleaned = read_and_clean_csv(right_input)
if right_cleaned:
    # sort if rule exists
    if right_file in file_sorting:
        s = file_sorting[right_file]
        right_cleaned.sort(key=lambda x: x[s['sort_key']], reverse=s.get('reverse', False))
    right_base = os.path.splitext(right_file)[0]
    right_as1 = os.path.join(folder_path, right_base + '_AS1_Keyframed.csv')
    right_as2 = os.path.join(folder_path, right_base + '_AS2_Keyframed.csv')
    Right_end_time = write_keyframed_alternate(right_as1, right_as2, right_cleaned, start_time=0)
    print(f"Right end time: {Right_end_time}")
else:
    Right_end_time = 0
    print("⚠️ Right input missing or empty; treating Right_end_time = 0")

# 2) Both Bottoms start together at Right_end_time + 2
bottoms_start = Right_end_time + 2
print(f"\nProcessing BOTTOMS together starting at {bottoms_start}...")

# Bottom I
bottom1_input = os.path.join(folder_path, bottom1_file)
bottom1_cleaned = read_and_clean_csv(bottom1_input)
bottom1_end = bottoms_start
if bottom1_cleaned:
    if bottom1_file in file_sorting:
        s = file_sorting[bottom1_file]
        bottom1_cleaned.sort(key=lambda x: x[s['sort_key']], reverse=s.get('reverse', False))
    base1 = os.path.splitext(bottom1_file)[0]
    b1_as1 = os.path.join(folder_path, base1 + '_AS1_Keyframed.csv')
    b1_as2 = os.path.join(folder_path, base1 + '_AS2_Keyframed.csv')
    bottom1_end = write_keyframed_alternate(b1_as1, b1_as2, bottom1_cleaned, start_time=bottoms_start)
else:
    print("⚠️ Bottom I missing or empty; skipping.")

# Bottom II
bottom2_input = os.path.join(folder_path, bottom2_file)
bottom2_cleaned = read_and_clean_csv(bottom2_input)
bottom2_end = bottoms_start
if bottom2_cleaned:
    if bottom2_file in file_sorting:
        s = file_sorting[bottom2_file]
        bottom2_cleaned.sort(key=lambda x: x[s['sort_key']], reverse=s.get('reverse', False))
    base2 = os.path.splitext(bottom2_file)[0]
    b2_as1 = os.path.join(folder_path, base2 + '_AS1_Keyframed.csv')
    b2_as2 = os.path.join(folder_path, base2 + '_AS2_Keyframed.csv')
    bottom2_end = write_keyframed_alternate(b2_as1, b2_as2, bottom2_cleaned, start_time=bottoms_start)
else:
    print("⚠️ Bottom II missing or empty; skipping.")

Bottom_end_time = max(bottom1_end, bottom2_end)
print(f"Bottoms end time: {Bottom_end_time}")

# 3) Left starts at Bottom_end_time + 2
left_start = Bottom_end_time + 2
print(f"\nProcessing LEFT starting at {left_start}...")
left_input = os.path.join(folder_path, left_file)
left_cleaned = read_and_clean_csv(left_input)
left_end = left_start
if left_cleaned:
    if left_file in file_sorting:
        s = file_sorting[left_file]
        left_cleaned.sort(key=lambda x: x[s['sort_key']], reverse=s.get('reverse', False))
    left_base = os.path.splitext(left_file)[0]
    left_as1 = os.path.join(folder_path, left_base + '_AS1_Keyframed.csv')
    left_as2 = os.path.join(folder_path, left_base + '_AS2_Keyframed.csv')
    left_end = write_keyframed_alternate(left_as1, left_as2, left_cleaned, start_time=left_start)
else:
    print("⚠️ Left missing or empty; skipping.")

print(f"Left end time: {left_end}")

# === Generate Behavior for all generated _Keyframed files (AS1 & AS2) ===
print("\nGenerating behavior files...")
for filename in os.listdir(folder_path):
    if not filename.endswith('_Keyframed.csv'):
        continue
    original_key = get_original_key_for_AS(filename)
    q_original = Q_values.get(original_key)
    if q_original is None:
        print(f"⚠️ Q not found for {original_key} (needed for behavior). Skipping behavior for {filename}.")
        continue
    generate_behavior_from_keyframed(os.path.join(folder_path, filename), q_original)

# === Duplicate positions with offset for all keyframed files ===
print("\nGenerating position keyframes with duplication offset...")
for filename in os.listdir(folder_path):
    if filename.endswith('_Keyframed.csv'):
        duplicate_positions_with_offset(os.path.join(folder_path, filename), offset_seconds=duplicate_offset)

# === Copy final files into final_csvs folder ===
final_folder = os.path.join(folder_path, 'final_csvs')
os.makedirs(final_folder, exist_ok=True)

for filename in os.listdir(folder_path):
    if filename.endswith('__Position_Keyframe.csv') or filename.endswith('_Behavior.csv'):
        src = os.path.join(folder_path, filename)
        dst = os.path.join(final_folder, filename)
        try:
            shutil.copy2(src, dst)
            print(f"Copied: {filename}")
        except Exception as e:
            print(f"⚠️ Failed copying {filename}: {e}")

print("\n✅ Done — all final CSVs copied to 'final_csvs' folder.")

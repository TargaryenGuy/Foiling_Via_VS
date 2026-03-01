import os
import csv

# === 1. USER CONFIGURATION ===
# Quantity of fluid (mL) for each original side
Q_values = {
    'Right_Side_Co-ordinates.csv': 80,
    'Bottom_I_Side_Co-ordinates.csv': 30,
    'Bottom_II_Side_Co-ordinates.csv': 30,
    'Left_Side_Co-ordinates.csv': 80
}

TIME_CORRECTION = 0.16

# === 2. FILE SETUP ===
folder_path = os.getcwd()
right_file = 'Right_Side_Co-ordinates.csv'
bottom1_file = 'Bottom_I_Side_Co-ordinates.csv'
bottom2_file = 'Bottom_II_Side_Co-ordinates.csv'
left_file = 'Left_Side_Co-ordinates.csv'

# Sorting: X for sides, Y for bottoms
file_sorting = {
    right_file:   {'key': 'x', 'rev': False},
    bottom1_file: {'key': 'y', 'rev': True},
    bottom2_file: {'key': 'y', 'rev': False},
    left_file:    {'key': 'x', 'rev': False}
}

def read_and_clean_csv(file_name):
    path = os.path.join(folder_path, file_name)
    if not os.path.exists(path): return None
    rows = []
    with open(path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append({
                'x': float(row['Centroid[X] (m)']),
                'y': float(row['Centroid[Y] (m)']),
                'z': float(row['Centroid[Z] (m)'])
            })
    return rows

def process_side(data, base_name, start_time, is_bottom):
    """
    Creates Stepped Position and Formula-based Behavior files for AS1/AS2.
    """
    # 1. Formula Calculations
    total_ml_original = Q_values.get(base_name, 0)
    total_ml_as = total_ml_original / 2.0
    total_time_seconds = total_ml_as * TIME_CORRECTION
    
    # Coordinates are split equally
    coords_per_as = len(data)
    delta = total_time_seconds / coords_per_as if coords_per_as > 0 else 0.0

    # 2. Offset and Step Configuration
    pos_hold = 0.990 if is_bottom else 1.990
    step_inc = 2 if is_bottom else 4  # Jump 2 indices for Bottom, 4 for Side
    time_jump = 1 if is_bottom else 2
    
    as1_pos, as2_pos = [], []
    as1_beh, as2_beh = [], []
    current_time = float(start_time)

    # 3. Process coordinates in pairs (AS1, AS2)
    for i in range(0, len(data), step_inc):
        t = current_time
        
        # --- AS1: Position and Behavior ---
        row1 = data[i]
        as1_pos.extend([[f"{t:.3f}", row1['x'], row1['y'], row1['z']], 
                        [f"{t + pos_hold:.3f}", row1['x'], row1['y'], row1['z']]])
        as1_beh.extend([[round(t, 5), 2],         # ON
                        [round(t + delta, 5), 1]]) # OFF
        
        # --- AS2: Position and Behavior ---
        if i + (step_inc // 2) < len(data):
            row2 = data[i + (step_inc // 2)]
            as2_pos.extend([[f"{t:.3f}", row2['x'], row2['y'], row2['z']], 
                            [f"{t + pos_hold:.3f}", row2['x'], row2['y'], row2['z']]])
            as2_beh.extend([[round(t, 5), 2],         # ON
                            [round(t + delta, 5), 1]]) # OFF
            
        current_time += time_jump

    # Final logic from your snippet: insert 0.0 if first time > 0
    for beh_list in [as1_beh, as2_beh]:
        if beh_list and beh_list[0][0] > 0.0:
            beh_list.insert(0, [0.0, 1]) # Initial OFF state

    # 4. Save 4 CSV Files
    base = os.path.splitext(base_name)[0]
    output_configs = [
        ('_AS1_Stepped.csv', as1_pos, ['time', 'positionX', 'positionY', 'positionZ']),
        ('_AS2_Stepped.csv', as2_pos, ['time', 'positionX', 'positionY', 'positionZ']),
        ('_AS1_Behavior.csv', as1_beh, ['time', 'behavior']),
        ('_AS2_Behavior.csv', as2_beh, ['time', 'behavior'])
    ]
    
    for suffix, rows, header in output_configs:
        with open(os.path.join(folder_path, base + suffix), 'w', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(header)
            writer.writerows(rows)
            
    return current_time

def run_full_workflow():
    print("🚀 Starting Integrated Workflow...")
    
    # Sequence: Right (0) -> Bottoms (2s Gap) -> Left (2s Gap)
    right_end = process_side(read_and_clean_csv(right_file), right_file, 0, False)
    
    b_start = right_end + 2
    b1_end = process_side(read_and_clean_csv(bottom1_file), bottom1_file, b_start, True)
    b2_end = process_side(read_and_clean_csv(bottom2_file), bottom2_file, b_start, True)
    
    left_start = max(b1_end, b2_end) + 2
    process_side(read_and_clean_csv(left_file), left_file, left_start, False)
    
    print("\n✅ Success! All Stepped Position and Behavior CSVs generated.")

if __name__ == "__main__":
    run_full_workflow()
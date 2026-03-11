import preonlab
import preonpy
import os
import csv

# ---------------------------------------------------------------------------
# MASTER SHEET: DYNAMIC IMPORT BASED ON CSV HEADERS
# ---------------------------------------------------------------------------

# PASTE YOUR FULL PATH HERE
CSV_FOLDER_PATH = r"/proj/rd_id/IDG/CAE/DTE/ovvt/multiphase/Transfer/Pratik/Foiling_Upadtes/Preonpy/Angles_Test/Euler_Angles/" 

# Target Parameters
TARGET_PARAMS = {
    "area type": "Rectangle",
    "particle size": 0.0005,
    "finite volume": True,
    "emit velocity": 0.25,
    "scale": (0.025, 0.013, 0.001),
    "euler angles": (0, 0, 0)
}

# Object Definitions
SOURCE_DEFINITIONS = [
    ("Bottom_I_AS1",  "Bottom_I_Side",  "AS1"),
    ("Bottom_I_AS2",  "Bottom_I_Side",  "AS2"),
    ("Bottom_II_AS1", "Bottom_II_Side", "AS1"),
    ("Bottom_II_AS2", "Bottom_II_Side", "AS2"),
    ("Left_AS1",      "Left_Side",      "AS1"),
    ("Left_AS2",      "Left_Side",      "AS2"),
    ("Right_AS1",     "Right_Side",     "AS1"),
    ("Right_AS2",     "Right_Side",     "AS2"),
]

def main():
    scene = preonlab.current_scene
    if not scene:
        print("Error: No scene is currently open.")
        return

    # 1. CHECK PATH
    if not os.path.exists(CSV_FOLDER_PATH):
        print(f"!! CRITICAL ERROR: Path not found: {CSV_FOLDER_PATH}")
        return
    
    print(f"--- Scanning Folder: {CSV_FOLDER_PATH} ---")

    # 2. EXECUTION LOOP
    for obj_name, side_prefix, as_suffix in SOURCE_DEFINITIONS:
        print(f"\nProcessing {obj_name}...")
        
        # A. Create Object
        obj = scene.find_object(obj_name)
        if obj is None:
            try:
                obj = scene.create_object("Area source", obj_name)
                print(f"  [CREATED] Success.")
            except:
                print(f"  !! CREATION FAILED. Skipping.")
                continue
        else:
            print(f"  [FOUND] Object exists.")

        # B. Apply Parameters
        for prop, val in TARGET_PARAMS.items():
            if prop == "particle size":
                try: obj[prop] = val
                except: pass
            else:
                try: obj[prop] = val
                except: pass
        print("  [UPDATED] Parameters set.")

        # C. Import Keyframes
        pos_filename = f"{side_prefix}_Co-ordinates_{as_suffix}__Position_Keyframe.csv"
        beh_filename = f"{side_prefix}_Co-ordinates_{as_suffix}_Behavior.csv"

        # Import Position
        import_csv_dynamic(obj, os.path.join(CSV_FOLDER_PATH, pos_filename), mode="position")
        
        # Import Behavior
        import_csv_dynamic(obj, os.path.join(CSV_FOLDER_PATH, beh_filename), mode="behavior")

    print("\n--- Complete ---")

def import_csv_dynamic(obj, filepath, mode):
    if not os.path.exists(filepath):
        print(f"  [MISSING] {os.path.basename(filepath)}")
        return

    try:
        with open(filepath, 'r') as f:
            # 1. READ HEADER to find property names
            # We assume Semicolon delimiter based on your previous files
            reader = csv.reader(f, delimiter=';')
            
            try:
                header = next(reader)
            except StopIteration:
                return # Empty file

            if not header: return

            # 2. MAP COLUMNS
            # We skip column 0 (Time) and map the rest based on header name
            col_mappings = []
            
            # Start from index 1 (skipping Time at index 0)
            for i in range(1, len(header)):
                col_name = header[i].strip()
                col_mappings.append((i, col_name))
            
            # Prepare data containers
            # keyframe_data = { "property_name": [(time, val, interp), ...] }
            keyframe_data = {name: [] for _, name in col_mappings}

            # 3. READ DATA ROWS
            valid_rows = 0
            for row in reader:
                if not row: continue
                
                try:
                    t = float(row[0])
                    
                    for col_idx, prop_name in col_mappings:
                        if col_idx < len(row):
                            val = float(row[col_idx])
                            
                            # Interpolation: Step for behavior, Linear for position
                            interp = "Step" if mode == "behavior" else "Linear"
                            
                            keyframe_data[prop_name].append((t, val, interp))
                    
                    valid_rows += 1
                except ValueError:
                    continue

            # 4. APPLY TO OBJECT
            if valid_rows > 0:
                for prop_name, keys in keyframe_data.items():
                    if keys:
                        try:
                            # We blindly try to set whatever the header said (e.g. "behavior", "positionX")
                            # Note: PreonLab internal names might differ slightly (e.g. "position x" vs "positionX")
                            # We apply a small fix for common CSV exports:
                            target_prop = prop_name.lower().replace("positionx", "position x").replace("positiony", "position y").replace("positionz", "position z")
                            
                            obj.set_keyframes(target_prop, keys)
                            print(f"  [SUCCESS] Set '{target_prop}' ({len(keys)} keys).")
                        except Exception as e:
                            # If exact header name fails, try falling back to standard names if meaningful
                            if mode == "behavior" and "behavior" in target_prop:
                                try:
                                    obj.set_keyframes("active", keys)
                                    print(f"  [RETRY] Mapped '{prop_name}' to 'active' -> Success.")
                                except:
                                    print(f"  !! FAILED to set property '{target_prop}': {e}")
                            else:
                                print(f"  !! FAILED to set property '{target_prop}': {e}")
            else:
                print(f"  [WARNING] No valid data rows in {os.path.basename(filepath)}")

    except Exception as e:
        print(f"  !! FILE ERROR: {e}")

if __name__ == "__main__":
    main()
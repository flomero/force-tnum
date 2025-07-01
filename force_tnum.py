# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fonttools",
# ]
# ///

# force_tnum.py
#
# This script first runs pyftsubset to prepare the font, then forces the 'tnum'
# (Tabular Figures) feature to be on by default by merging its rules into the
# 'liga' (Standard Ligatures) feature.
#
# Usage: python force_tnum.py <input_font_file>

import sys
import os
import subprocess
from fontTools.ttLib import TTFont

if len(sys.argv) != 2:
    print("Usage: python force_tnum.py <input_font_file>")
    sys.exit(1)

input_font_path = sys.argv[1]

# Generate intermediate and output filenames
base_name, ext = os.path.splitext(input_font_path)
intermediate_font_path = f"{base_name}-TEMP{ext}"
output_font_path = f"{base_name}-TNUM{ext}"

try:
    # Step 1: Run pyftsubset to prepare the font
    print(f"Step 1: Running pyftsubset on '{input_font_path}'...")
    subset_cmd = [
        "pyftsubset",
        input_font_path,
        f"--output-file={intermediate_font_path}",
        "--layout-features=kern,liga,calt,lnum,tnum",
        "--desubroutinize",
        "--unicodes=*",
    ]

    result = subprocess.run(subset_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"pyftsubset failed: {result.stderr}")

    print(f"pyftsubset completed successfully. Created '{intermediate_font_path}'")

    # Step 2: Process the font to merge tnum into liga
    print(f"\nStep 2: Processing font to enable tnum by default...")
    font = TTFont(intermediate_font_path)

    if "GSUB" not in font:
        raise Exception("Font has no GSUB table.")

    gsub = font["GSUB"]
    features = {f.FeatureTag: f for f in gsub.table.FeatureList.FeatureRecord}

    if "tnum" not in features:
        raise Exception("The 'tnum' feature was not found in this font.")
    if "liga" not in features:
        raise Exception(
            "The 'liga' feature was not found. Please re-run the previous pyftsubset step."
        )

    print("Found 'tnum' and 'liga' features. Proceeding with the merge.")

    tnum_lookups = features["tnum"].Feature.LookupListIndex
    liga_lookups = features["liga"].Feature.LookupListIndex

    # Append the tnum lookups to the liga feature's list
    # This effectively makes the tnum rules part of the default 'liga' processing
    liga_lookups.extend(tnum_lookups)
    print(f"Moved {len(tnum_lookups)} lookup(s) from 'tnum' to 'liga'.")

    # Remove the now-redundant 'tnum' feature from the font
    for i in range(len(gsub.table.FeatureList.FeatureRecord) - 1, -1, -1):
        if gsub.table.FeatureList.FeatureRecord[i].FeatureTag == "tnum":
            del gsub.table.FeatureList.FeatureRecord[i]
            print("Successfully removed the old 'tnum' feature record.")
            break

    # Step 3: Update font names to include "TNUM"
    print("\nStep 3: Updating font internal names...")
    if "name" in font:
        name_table = font["name"]
        for record in name_table.names:
            current_name = record.toUnicode()

            # Update Family Name (nameID 1) and Full Font Name (nameID 4)
            if record.nameID in [1, 4]:
                if "TNUM" not in current_name:
                    new_name = f"{current_name} TNUM"
                    record.string = new_name.encode(record.getEncoding())
                    print(
                        f"Updated nameID {record.nameID}: '{current_name}' → '{new_name}'"
                    )

            # Update PostScript Name (nameID 6) - no spaces allowed
            elif record.nameID == 6:
                if "TNUM" not in current_name:
                    new_name = f"{current_name}TNUM"
                    record.string = new_name.encode(record.getEncoding())
                    print(f"Updated PostScript name: '{current_name}' → '{new_name}'")
        print("Font internal names updated successfully.")

    # Save the modified font to the new file
    font.save(output_font_path)
    print(
        f"\nSuccessfully created '{output_font_path}' with 'tnum' enabled by default."
    )

    os.remove(intermediate_font_path)
    print(f"Cleaned up intermediate file '{intermediate_font_path}'")

except FileNotFoundError:
    print(f"ERROR: The input file '{input_font_path}' was not found.")
    print("Please make sure the file exists.")
except subprocess.CalledProcessError as e:
    print(f"ERROR: pyftsubset command failed: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
    if os.path.exists(intermediate_font_path):
        os.remove(intermediate_font_path)
        print(f"Cleaned up intermediate file '{intermediate_font_path}'")

import csv
import os

# ============================================================
# USER SETTINGS
# ============================================================

CSV_A = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Left-001.wav.csv"
CSV_B = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Right-001.wav.csv"
CSV_DIFF = r"X:\ProjectsFolder\Session\projectNAME\TrackAB_differences.csv"

# ============================================================
# LOAD CSV INTO MEMORY
# ============================================================

def load_csv(path):
    rows = []
    with open(path, "r") as f:
        reader = csv.reader(f)
        next(reader)  # skip human header
        next(reader)  # skip machine header
        for row in reader:
            rows.append(row)
    return rows

print("======================================")
print(" DIFFERENCE ENGINE v1.0")
print("======================================")
print(f"Loading A: {CSV_A}")
print(f"Loading B: {CSV_B}")

rowsA = load_csv(CSV_A)
rowsB = load_csv(CSV_B)

if len(rowsA) != len(rowsB):
    print("ERROR: CSV row counts do not match.")
    print(f"A has {len(rowsA)} rows, B has {len(rowsB)} rows.")
    exit()

print(f"Loaded {len(rowsA)} aligned rows.")

# ============================================================
# PREPARE OUTPUT CSV
# ============================================================

os.makedirs(os.path.dirname(CSV_DIFF), exist_ok=True)
out = open(CSV_DIFF, "w", newline="")
writer = csv.writer(out)

# Human header
writer.writerow([
    "project_time","local_time",
    "RMS_A","RMS_B","RMS_DIFF",
    "Peak_A","Peak_B","Peak_DIFF",
    "M_LUFS_A","M_LUFS_B","M_LUFS_DIFF",
    "ST_LUFS_A","ST_LUFS_B","ST_LUFS_DIFF",
    "Int_LUFS_A","Int_LUFS_B","Int_LUFS_DIFF"
])

# Machine header
writer.writerow([
    "t_proj","t_loc",
    "rA","rB","rD",
    "pA","pB","pD",
    "mA","mB","mD",
    "stA","stB","stD",
    "iA","iB","iD"
])

# ============================================================
# PROCESS DIFFERENCES
# ============================================================

print("Computing differences...")

line_count = 0

for rowA, rowB in zip(rowsA, rowsB):

    # unpack A
    t_proj = float(rowA[0])
    t_loc  = float(rowA[1])
    RMS_A  = float(rowA[4])
    Peak_A = float(rowA[5])
    M_A    = float(rowA[6])
    ST_A   = float(rowA[7])
    Int_A  = float(rowA[8])

    # unpack B
    RMS_B  = float(rowB[4])
    Peak_B = float(rowB[5])
    M_B    = float(rowB[6])
    ST_B   = float(rowB[7])
    Int_B  = float(rowB[8])

    # differences
    RMS_D = RMS_A - RMS_B
    Peak_D = Peak_A - Peak_B
    M_D = M_A - M_B
    ST_D = ST_A - ST_B
    Int_D = Int_A - Int_B

    writer.writerow([
        t_proj, t_loc,
        RMS_A, RMS_B, RMS_D,
        Peak_A, Peak_B, Peak_D,
        M_A, M_B, M_D,
        ST_A, ST_B, ST_D,
        Int_A, Int_B, Int_D
    ])

    line_count += 1

out.close()

print(f"Done. Wrote {line_count} rows → {CSV_DIFF}")
print("======================================")
print(" DIFFERENCE ENGINE COMPLETE")
print("======================================")

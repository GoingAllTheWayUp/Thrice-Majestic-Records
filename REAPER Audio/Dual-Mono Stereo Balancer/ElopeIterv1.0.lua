-- ============================================================
-- ENVELOPE WRITER v1.0
-- Reads TrackAB_differences.csv
-- Writes automation to the two selected tracks
-- ============================================================
X:\ProjectsFolder\Session\projectNAME\TrackAB_differences.csv
-- LYZERv1.0.py
-- WAV_A = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Left-001.wav"
-- WAV_B = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Right-001.wav"

DiffEngv1.0.py
-- CSV_A = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Left-001.wav.csv"
-- CSV_B = r"X:\ProjectsFolder\Session\projectNAME\ReaperProject_stem_TrackName_Right-001.wav.csv"
-- CSV_DIFF = r"X:\ProjectsFolder\Session\projectNAME\TrackAB_differences.csv"

-- ElopeIterv1.0.lua
-- You select two tracks in REAPER: (CLICK to SELECT ORDER)
-- Track A (right)
-- Track B (left)

-- ============================================================
-- ENVELOPE WRITER v2.0 (Trim Volume, calibrated)
-- Uses your measured Trim Volume envelope scale:
--   ENV_MAX  = +6.02 dB
--   ENV_ZERO = 0.0 dB
--   ENV_MIN  = -150 dB / -inf
--
-- Reads TrackAB_differences.csv and writes automation
-- to the Trim Volume envelopes of the TWO selected tracks.
-- ============================================================

---------------------------------------------------------------
-- USER SETTINGS
---------------------------------------------------------------
local CSV_DIFF = "X:/ProjectsFolder/Session/projectNAME/TrackAB_differences.csv"

-- Which metric drives the gain correction?
local METRIC = "RMS_DIFF"  
-- Options: "RMS_DIFF", "M_LUFS_DIFF", "ST_LUFS_DIFF", "Int_LUFS_DIFF"

-- Gain scaling (1.0 = full correction, 0.5 = half, etc.)
local SCALE = 1.0

-- Trim Volume calibration (your measured values)
local ENV_MAX  = 852.774454406994   -- +6.02 dB
local ENV_ZERO = 716.217850312608   -- 0.0 dB
local ENV_MIN  = 0.0                -- -150 dB / -inf

---------------------------------------------------------------
-- HELPERS
---------------------------------------------------------------
local function msg(s)
    reaper.ShowConsoleMsg(tostring(s) .. "\n")
end

-- Convert dB → Trim Volume envelope value using your scale
local function dB_to_env(gain_db)
    if gain_db >= 0 then
        -- Positive gain (0 → +6.02 dB)
        return ENV_ZERO + (gain_db / 6.02) * (ENV_MAX - ENV_ZERO)
    else
        -- Negative gain (0 → -150 dB)
        return ENV_ZERO + (gain_db / 150.0) * (ENV_ZERO - ENV_MIN)
    end
end

-- Load CSV
local function load_diff_csv(path)
    local rows = {}
    local f = io.open(path, "r")
    if not f then return nil end

    f:read("*l") -- skip human header
    f:read("*l") -- skip machine header

    for line in f:lines() do
        local cols = {}
        for v in string.gmatch(line, "([^,]+)") do
            table.insert(cols, v)
        end
        table.insert(rows, cols)
    end

    f:close()
    return rows
end

---------------------------------------------------------------
-- MAIN
---------------------------------------------------------------
msg("======================================")
msg(" ENVELOPE WRITER v2.0 (Trim Volume)")
msg("======================================")
msg("Loading CSV: " .. CSV_DIFF)

local rows = load_diff_csv(CSV_DIFF)
if not rows then
    msg("ERROR: Cannot load CSV.")
    return
end

local sel = reaper.CountSelectedTracks(0)
if sel ~= 2 then
    msg("ERROR: Select exactly TWO tracks.")
    return
end

local trackA = reaper.GetSelectedTrack(0, 0)
local trackB = reaper.GetSelectedTrack(0, 1)

local envA = reaper.GetTrackEnvelopeByName(trackA, "Trim Volume")
local envB = reaper.GetTrackEnvelopeByName(trackB, "Trim Volume")

if not envA or not envB then
    msg("ERROR: Trim Volume envelopes not found. Enable them first.")
    return
end

msg("Using metric: " .. METRIC)

local metric_index = {
    RMS_DIFF      = 5,
    Peak_DIFF     = 8,
    M_LUFS_DIFF   = 11,
    ST_LUFS_DIFF  = 14,
    Int_LUFS_DIFF = 17
}

local idx = metric_index[METRIC]
if not idx then
    msg("ERROR: Invalid METRIC setting.")
    return
end

reaper.Undo_BeginBlock()

local count = 0

for _, row in ipairs(rows) do
    local t = tonumber(row[1])  -- project_time
    local diff_db = tonumber(row[idx])

    if diff_db then
        local gain_db = diff_db * SCALE

        -- Convert dB → Trim Volume envelope value
        local env_val = dB_to_env(gain_db)

        reaper.InsertEnvelopePoint(envA, t, env_val, 0, 0, false, true)
        reaper.InsertEnvelopePoint(envB, t, env_val, 0, 0, false, true)

        count = count + 1
    end
end

reaper.Envelope_SortPoints(envA)
reaper.Envelope_SortPoints(envB)

reaper.Undo_EndBlock("Envelope Writer v2.0 (Trim Volume)", -1)

msg("======================================")
msg(" DONE")
msg(" Wrote " .. count .. " envelope points to each track.")
msg("======================================")

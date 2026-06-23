-- ============================================================
-- ENVELOPE WRITER v2.3 (Trim Volume, calibrated, reduction-only)
-- Uses existing TrackAB_differences.csv (no extra columns)
--   project_time, local_time,
--   RMS_A,RMS_B,RMS_DIFF,
--   ...
-- You select TWO tracks:
--   Track A (right)
--   Track B (left)
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
local ENV_MAX  = 852.774454406994   -- +6.02 dB (not used in reduction-only)
local ENV_ZERO = 716.217850312608   -- 0.0 dB
local ENV_MIN  = 0.0                -- -150 dB / -inf

---------------------------------------------------------------
-- HELPERS
---------------------------------------------------------------
local function msg(s)
    reaper.ShowConsoleMsg(tostring(s) .. "\n")
end

-- Reduction-only: positive dB = no change, negative dB = attenuation
local function dB_to_env(gain_db)
    if gain_db >= 0 then
        -- no boost in reduction-only mode
        return ENV_ZERO
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
msg(" ENVELOPE WRITER v2.3 (Trim Volume)")
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

-- Track A (right), Track B (left)
local trackA = reaper.GetSelectedTrack(0, 0)
local trackB = reaper.GetSelectedTrack(0, 1)

local envA = reaper.GetTrackEnvelopeByName(trackA, "Trim Volume")
local envB = reaper.GetTrackEnvelopeByName(trackB, "Trim Volume")

if not envA or not envB then
    msg("ERROR: Trim Volume envelopes not found. Enable them first.")
    return
end

msg("Using metric: " .. METRIC)

-- Column indices in your CSV (1-based Lua):
-- 1: project_time
-- 2: local_time
-- 3: RMS_A
-- 4: RMS_B
-- 5: RMS_DIFF
-- 6: Peak_A
-- 7: Peak_B
-- 8: Peak_DIFF
-- 9: M_LUFS_A
-- 10: M_LUFS_B
-- 11: M_LUFS_DIFF
-- 12: ST_LUFS_A
-- 13: ST_LUFS_B
-- 14: ST_LUFS_DIFF
-- 15: Int_LUFS_A
-- 16: Int_LUFS_B
-- 17: Int_LUFS_DIFF
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

    if t and diff_db then
        -- Stereo balancer, reduction-only:
        -- diff_db > 0  → A louder → reduce A
        -- diff_db < 0  → B louder → reduce B
        local gainA_db, gainB_db

        if diff_db > 0 then
            gainA_db = -diff_db
            gainB_db = 0.0
        elseif diff_db < 0 then
            gainA_db = 0.0
            gainB_db = diff_db  -- negative
        else
            gainA_db = 0.0
            gainB_db = 0.0
        end

        gainA_db = gainA_db * SCALE
        gainB_db = gainB_db * SCALE

        local envA_val = dB_to_env(gainA_db)
        local envB_val = dB_to_env(gainB_db)

        reaper.InsertEnvelopePoint(envA, t, envA_val, 0, 0, false, true)
        reaper.InsertEnvelopePoint(envB, t, envB_val, 0, 0, false, true)

        count = count + 1
    end
end

reaper.Envelope_SortPoints(envA)
reaper.Envelope_SortPoints(envB)

reaper.Undo_EndBlock("Envelope Writer v2.3 (Trim Volume)", -1)

msg("======================================")
msg(" DONE")
msg(" Wrote " .. count .. " envelope points to each track.")
msg("======================================")

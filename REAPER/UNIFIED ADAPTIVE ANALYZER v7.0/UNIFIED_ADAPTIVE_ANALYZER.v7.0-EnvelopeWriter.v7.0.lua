-- ============================================================
-- VOCAL LEVELER — ENVELOPE WRITER v7.0 (Trim Volume Compatible)
-- Reads unified CSV analysis and draws smooth REAPER automation
-- ============================================================

---------------------------------------------------------------
-- USER SETTINGS
---------------------------------------------------------------
local CSV_PATH      = "X:/AudioProject/Vocal/Stem/-v7.0-ANALYSIS.csv"

-- Global scaling factor (1.0 = full correction, 0.5 = half weight)
local SCALE         = 1.0

-- REAPER Trim Volume calibration values
local ENV_MAX       = 852.77445440699   -- +6.02 dB slider max
local ENV_ZERO      = 716.21785031261   -- 0.0 dB unity gain
local ENV_MIN       = 0.0               -- -inf / -150 dB min

-- Point spacing in seconds (matches STEP_MS = 0.010s)
local POINT_SPACING = 0.010

---------------------------------------------------------------
-- HELPERS
---------------------------------------------------------------
local function msg(s)
    reaper.ShowConsoleMsg(tostring(s) .. "\n")
end

-- Convert dB gain value to REAPER Trim Volume slider position
local function dB_to_env(gain_db)
    if gain_db >= 0 then
        return ENV_ZERO + (gain_db / 6.02) * (ENV_MAX - ENV_ZERO)
    else
        return ENV_ZERO + (gain_db / 150.0) * (ENV_ZERO - ENV_MIN)
    end
end

-- Load and parse CSV (skipping human & machine headers)
local function load_csv(path)
    local rows = {}
    local f = io.open(path, "r")
    if not f then return nil end

    f:read("*l") -- Skip human header
    f:read("*l") -- Skip machine header

    for line in f:lines() do
        local cols = {}
        for v in string.gmatch(line, "([^,]+)") do
            cols[#cols + 1] = v
        end
        rows[#rows + 1] = cols
    end

    f:close()
    return rows
end

---------------------------------------------------------------
-- MAIN EXECUTION
---------------------------------------------------------------
reaper.ShowConsoleMsg("")
msg("======================================")
msg(" VOCAL LEVELER — ENVELOPE WRITER v7.0")
msg("======================================")
msg("Loading CSV: " .. CSV_PATH)

local rows = load_csv(CSV_PATH)
if not rows then
    msg("ERROR: Cannot load or read CSV file.")
    return
end

local sel = reaper.CountSelectedTracks(0)
if sel ~= 1 then
    msg("ERROR: Please select exactly ONE track in REAPER.")
    return
end

local track = reaper.GetSelectedTrack(0, 0)
local env   = reaper.GetTrackEnvelopeByName(track, "Trim Volume")

if not env then
    msg("ERROR: 'Trim Volume' envelope not found on selected track. Please enable/show it first.")
    return
end

msg("Writing Trim Volume automation points...")

local TIME_COL = 1
local GAIN_COL = 10

reaper.Undo_BeginBlock()

local count  = 0
local last_t = nil

for _, row in ipairs(rows) do
    local t    = tonumber(row[TIME_COL])
    local g_db = tonumber(row[GAIN_COL])

    if t and g_db then
        if not last_t or (t - last_t) >= (POINT_SPACING - 1e-6) then
            local gain_db = g_db * SCALE
            local env_val = dB_to_env(gain_db)

            reaper.InsertEnvelopePoint(env, t, env_val, 0, 0, false, true)
            last_t = t
            count = count + 1
        end
    end
end

reaper.Envelope_SortPoints(env)
reaper.Undo_EndBlock("Vocal Leveler — Envelope Writer v7.0", -1)

msg("======================================")
msg(" DONE")
msg(" Successfully wrote " .. count .. " envelope points.")
msg("======================================")
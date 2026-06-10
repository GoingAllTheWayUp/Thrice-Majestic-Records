-- ============================================================
-- READ THREE MANUALLY-PLACED ENVELOPE POINTS
-- For the track's "Trim Volume" envelope
--
-- You must place EXACTLY THREE POINTS on the envelope:
--   1. MAX  (+6.02 dB)
--   2. ZERO (0.0 dB)
--   3. MIN  (-inf ; -150 dB)
-- In that order, anywhere on the timeline.
-- ============================================================

local function msg(s)
    reaper.ShowConsoleMsg(tostring(s) .. "\n")
end

-- ============================================================
-- MAIN
-- ============================================================

reaper.ShowConsoleMsg("")

local track = reaper.GetSelectedTrack(0, 0)
if not track then
    reaper.ShowMessageBox("Select the track with the Trim Volume envelope.", "Error", 0)
    return
end

-- Get Trim Volume envelope
local env = reaper.GetTrackEnvelopeByName(track, "Trim Volume")
if not env then
    reaper.ShowMessageBox("Trim Volume envelope not found. Enable it first.", "Error", 0)
    return
end

local point_count = reaper.CountEnvelopePoints(env)
if point_count < 3 then
    reaper.ShowMessageBox("You must place EXACTLY THREE points: MAX, ZERO, MIN.", "Error", 0)
    return
end

-- Read the FIRST THREE POINTS in the order you placed them
local function read_point(i)
    local ok, time, value, shape, tension, selected = reaper.GetEnvelopePoint(env, i)
    return value
end

local MAX_val  = read_point(0)
local ZERO_val = read_point(1)
local MIN_val  = read_point(2)

msg("======================================")
msg("Trim Volume Envelope Scale (Readback)")
msg("======================================")
msg(string.format("MAX  (+150 dB):  %.12f", MAX_val))
msg(string.format("ZERO (0.0 dB):   %.12f", ZERO_val))
msg(string.format("MIN  (-150 dB):  %.12f", MIN_val))
msg("======================================")

reaper.ShowMessageBox("Readback complete. Check console.", "Done", 0)

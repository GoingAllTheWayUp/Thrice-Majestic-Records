-- ============================================================
-- TIME SELECTION LOOP DIAGNOSTIC (SAFE TEST SCRIPT)
-- ============================================================
-- This script:
--   • Reads REAPER's time selection
--   • Loops through it in 50 ms steps
--   • Prints each step to the console
--   • Confirms boundaries, stepping, and iteration count
--   • Does NOT modify envelopes or audio
-- ============================================================

local function msg(s)
    reaper.ShowConsoleMsg(tostring(s) .. "\n")
end

reaper.ShowConsoleMsg("") -- clear console

-- Get time selection
local start_t, end_t = reaper.GetSet_LoopTimeRange(false, false, 0, 0, false)

if start_t == end_t then
    reaper.ShowMessageBox("No time selection detected.", "Error", 0)
    return
end

-- User-adjustable step size (ms)
local STEP_MS = 50  -- change this to test different stepping
local step_s = STEP_MS / 1000.0

msg("======================================")
msg(" TIME SELECTION LOOP DIAGNOSTIC START ")
msg("======================================")
msg("Start time: " .. start_t)
msg("End time:   " .. end_t)
msg("Length:     " .. (end_t - start_t))
msg("Step size:  " .. STEP_MS .. " ms")
msg("--------------------------------------")

local t = start_t
local count = 0

while t <= end_t do
    count = count + 1
    msg(string.format("Step %d: t = %.6f", count, t))
    t = t + step_s
end

msg("--------------------------------------")
msg("Total steps: " .. count)
msg("======================================")
msg(" DIAGNOSTIC COMPLETE ")
msg("======================================")

-- Dump_ReaEQ_Gain_dB.lua
-- Select the track with ReaEQ in slot 0, then run.

local track = reaper.GetSelectedTrack(0, 0)
if not track then
  reaper.ShowConsoleMsg("No track selected\n")
  return
end

local fx = 0
local _, name = reaper.TrackFX_GetFXName(track, fx, "")
reaper.ShowConsoleMsg("FX: " .. name .. "\n\n")

-- YOUR gain params:
local gain_params = {1, 4, 7, 10, 13}

for _, p in ipairs(gain_params) do
    local _, pname = reaper.TrackFX_GetParamName(track, fx, p, "")
    local val = reaper.TrackFX_GetParam(track, fx, p)

    local _, formatted = reaper.TrackFX_GetFormattedParamValue(track, fx, p, "")

    reaper.ShowConsoleMsg(
        string.format(
            "Param %d (%s):\n  Normalized: %.4f\n  Formatted: %s\n\n",
            p, pname, val, formatted
        )
    )
end

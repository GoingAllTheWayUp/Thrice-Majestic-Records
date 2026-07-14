-- Dump_ReaEQ_Params.lua
-- Select the track with ReaEQ in slot 0, then run this.

local track = reaper.GetSelectedTrack(0, 0)
if not track then
  reaper.ShowConsoleMsg("No track selected\n")
  return
end

local fx = 0
local _, name = reaper.TrackFX_GetFXName(track, fx, "")
reaper.ShowConsoleMsg("FX: " .. name .. "\n\n")

local param_count = reaper.TrackFX_GetNumParams(track, fx)

for p = 0, param_count - 1 do
    local _, pname = reaper.TrackFX_GetParamName(track, fx, p, "")
    local val = reaper.TrackFX_GetParam(track, fx, p)
    local minval, maxval = reaper.TrackFX_GetParamEx(track, fx, p)

    reaper.ShowConsoleMsg(
        string.format(
            "Param %d: %s\n  Value: %.4f\n  Min: %.4f  Max: %.4f\n\n",
            p, pname, val, minval, maxval
        )
    )
end

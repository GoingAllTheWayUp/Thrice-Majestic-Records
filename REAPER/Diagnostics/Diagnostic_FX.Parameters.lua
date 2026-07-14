-- List FX and parameters on the selected track
-- Step 1: Select your guitar FOLDER track, then run this.
-- What this does:
-- Looks at the selected track (so select the folder first).
-- Lists:
-- Each FX index (FX 0, FX 1, etc.)
-- Each parameter index and name (Param 0: Left Volume, etc.)
-- Prints everything to the ReaScript console.

local track = reaper.GetSelectedTrack(0, 0)
if not track then
  reaper.ShowMessageBox("No track selected. Select the guitar FOLDER track and run again.", "Error", 0)
  return
end

local _, track_name = reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "", false)
track_name = track_name ~= "" and track_name or "(unnamed track)"

local fx_count = reaper.TrackFX_GetCount(track)
if fx_count == 0 then
  reaper.ShowMessageBox("Selected track has no FX.\n\nAdd 'JS: Stereo Channel Volume/Pan/Polarity' to this track first.", "Error", 0)
  return
end

local msg = "Track: " .. track_name .. "\nFX count: " .. fx_count .. "\n\n"

for fx = 0, fx_count - 1 do
  local retval, fx_name = reaper.TrackFX_GetFXName(track, fx, "")
  msg = msg .. string.format("FX %d: %s\n", fx, fx_name)

  local param_count = reaper.TrackFX_GetNumParams(track, fx)
  for p = 0, param_count - 1 do
    local retval2, param_name = reaper.TrackFX_GetParamName(track, fx, p, "")
    msg = msg .. string.format("    Param %d: %s\n", p, param_name)
  end

  msg = msg .. "\n"
end

reaper.ShowConsoleMsg(msg)
reaper.ShowMessageBox("FX/parameter list printed to ReaScript console.\n\nView -> ReaScript console output.", "Done", 0)

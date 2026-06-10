-- List parameters for JS: Volume Adjustment on the FIRST selected track

local track = reaper.GetSelectedTrack(0, 0)
if not track then
  reaper.ShowMessageBox("Select the RIGHT guitar track and run again.", "Error", 0)
  return
end

local fx_count = reaper.TrackFX_GetCount(track)
local msg = ""

for fx = 0, fx_count - 1 do
  local _, fx_name = reaper.TrackFX_GetFXName(track, fx, "")
  if fx_name:find("Volume Adjustment") then
    msg = msg .. "FX index: " .. fx .. " - " .. fx_name .. "\n"

    local param_count = reaper.TrackFX_GetNumParams(track, fx)
    for p = 0, param_count - 1 do
      local _, pname = reaper.TrackFX_GetParamName(track, fx, p, "")
      local _, pval  = reaper.TrackFX_GetFormattedParamValue(track, fx, p, "")
      msg = msg .. string.format("  Param %d: %s (current: %s)\n", p, pname, pval)
    end
  end
end

reaper.ShowConsoleMsg(msg)
reaper.ShowMessageBox("Check ReaScript console for FX/param list.", "Done", 0)

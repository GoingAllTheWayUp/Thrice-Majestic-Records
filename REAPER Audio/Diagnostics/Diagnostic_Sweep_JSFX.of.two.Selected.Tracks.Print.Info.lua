-- Sweep-test JS: Volume Adjustment on two selected tracks

local sel_count = reaper.CountSelectedTracks(0)
if sel_count < 2 then
  reaper.ShowMessageBox("Select your TWO guitar tracks and run again.", "Error", 0)
  return
end

reaper.ShowConsoleMsg("")

for i = 0, 1 do
  local track = reaper.GetSelectedTrack(0, i)
  local _, name = reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "", false)
  name = name ~= "" and name or "(unnamed track)"

  reaper.ShowConsoleMsg("=== TRACK " .. (i+1) .. ": " .. name .. " ===\n")

  -- Find JS: Volume Adjustment
  local fx_count = reaper.TrackFX_GetCount(track)
  local fx_index = -1

  for fx = 0, fx_count - 1 do
    local _, fx_name = reaper.TrackFX_GetFXName(track, fx, "")
    if fx_name:find("Volume Adjustment") then
      fx_index = fx
      break
    end
  end

  if fx_index == -1 then
    reaper.ShowConsoleMsg("   ❌ JS: Volume Adjustment NOT FOUND\n\n")
  else
    reaper.ShowConsoleMsg("   ✅ JSFX found at FX index " .. fx_index .. "\n")
    reaper.ShowConsoleMsg("   Normalized → Displayed dB\n")

    for step = 0, 10 do
      local norm = step / 10
      reaper.TrackFX_SetParam(track, fx_index, 0, norm)
      local _, dB = reaper.TrackFX_GetFormattedParamValue(track, fx_index, 0, "")
      reaper.ShowConsoleMsg(string.format("   %.2f → %s\n", norm, dB))
    end

    reaper.ShowConsoleMsg("\n")
  end
end

reaper.ShowMessageBox("Sweep complete. Check ReaScript console.", "Done", 0)

--   MY RESULTS
--   The slider is not in dB
--   The slider is not logarithmic
--   The slider is not a gain control
--   The slider is just a raw linear scalar from 0.0 to 1.0
--   In other words:
--   ✔ This JSFX is a linear amplitude multiplier, not a dB fader.

--   
--   === TRACK 1: RIGHT ===
--      ✅ JSFX found at FX index 7
--      Normalized → Displayed dB
--      0.00 → 0.0
--      0.10 → 0.1
--      0.20 → 0.2
--     0.30 → 0.3
--     0.40 → 0.4
--     0.50 → 0.5
--     0.60 → 0.6
--      0.70 → 0.7
--      0.80 → 0.8
--      0.90 → 0.9
--      1.00 → 1.0

--   === TRACK 2: LEFT ===
--      ✅ JSFX found at FX index 6
--     Normalized → Displayed dB
--      0.00 → 0.0
--     0.10 → 0.1
--     0.20 → 0.2
--     0.30 → 0.3
--      0.40 → 0.4
--      0.50 → 0.5
--      0.60 → 0.6
--      0.70 → 0.7
--      0.80 → 0.8
--      0.90 → 0.9
--      1.00 → 1.0

--   
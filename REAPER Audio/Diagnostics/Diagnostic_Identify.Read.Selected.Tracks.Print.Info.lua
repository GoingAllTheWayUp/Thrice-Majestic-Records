-- Identify selected tracks and locate "JS: Volume Adjustment" on each

-- Lua reads the selected tracks in order:
-- Selected track 1 → Left guitar
-- Selected track 2 → Right guitar
-- This is the simplest and most reliable.

-- Reads all selected tracks
-- Prints:
-- Track index
-- Track name
-- Every FX name on that track
-- The FX index of JS: Volume Adjustment if present

-- Confirms whether the JSFX is found-- 


-- RESULT
-- TRACK 1: RIGHT
--    FX 0: VST: ReaEQ (Cockos)
--    FX 1: VST: ReaTune (Cockos)
--    FX 2: VST3: NeuralAmpModeler (Steven Atkinson)
--    FX 3: VST: ReaEQ (Cockos)
--    FX 4: VST: GComp (GVST)
--    FX 5: VST: ReaXcomp (Cockos)
--    FX 6: VST: TDR Nova (Tokyo Dawn Labs)
--   FX 7: JS: Volume Adjustment
--    ✅ JS: Volume Adjustment FOUND at FX index 7

-- TRACK 2: LEFT
--    FX 0: VST: ReaEQ (Cockos)
--    FX 1: VST: ReaTune (Cockos)
--    FX 2: VST3: NeuralAmpModeler (Steven Atkinson)
--    FX 3: VST: ReaEQ (Cockos)
--    FX 4: VST: GComp (GVST)
--    FX 5: VST: ReaXcomp (Cockos)
--    FX 6: JS: Volume Adjustment
--    ✅ JS: Volume Adjustment FOUND at FX index 6
   

local sel_count = reaper.CountSelectedTracks(0)
if sel_count < 2 then
  reaper.ShowMessageBox("Select your TWO guitar tracks and run again.", "Error", 0)
  return
end

reaper.ShowConsoleMsg("") -- clear console

for i = 0, sel_count - 1 do
  local track = reaper.GetSelectedTrack(0, i)
  local _, name = reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "", false)
  name = name ~= "" and name or "(unnamed track)"

  reaper.ShowConsoleMsg("TRACK " .. (i+1) .. ": " .. name .. "\n")

  local fx_count = reaper.TrackFX_GetCount(track)
  local found_fx = -1

  for fx = 0, fx_count - 1 do
    local _, fx_name = reaper.TrackFX_GetFXName(track, fx, "")
    reaper.ShowConsoleMsg(string.format("   FX %d: %s\n", fx, fx_name))

    -- Look for JS: Volume Adjustment (exact match or renamed)
    if fx_name:find("Volume Adjustment") then
      found_fx = fx
    end
  end

  if found_fx == -1 then
    reaper.ShowConsoleMsg("   ❌ JS: Volume Adjustment NOT FOUND on this track!\n\n")
  else
    reaper.ShowConsoleMsg("   ✅ JS: Volume Adjustment FOUND at FX index " .. found_fx .. "\n\n")
  end
end

reaper.ShowMessageBox("Scan complete. Check ReaScript console.", "Done", 0)

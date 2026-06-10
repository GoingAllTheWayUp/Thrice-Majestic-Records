-- My Result for "Balancing ACT" 
-- FX 3: JS: Stereo Channel Volume/Pan/Polarity Control
--     Param 0: Left Volume (dB)
--     Param 1: Left Pan
--     Param 2: Left Phase
--     Param 3: Right Volume (dB)
--     Param 4: Right Pan
--     Param 5: Right Phase
--     Param 6: Bypass
--     Param 7: Wet
--     Param 8: Delta

-- My Resoult expressed a "Non-lineer dB scale"
--next script "Sweeps" left channel volume of this JSSX

-- TEST 1: Directly set Left/Right Volume parameters on FX 3

local track = reaper.GetSelectedTrack(0, 0)
if not track then
  reaper.ShowMessageBox("Select the guitar FOLDER track first.", "Error", 0)
  return
end

local fx = 3  -- JS: Stereo Channel Volume/Pan/Polarity Control

-- Set Left Volume to -3 dB
reaper.TrackFX_SetParam(track, fx, 0, 0.45)  -- normalized value approx for -3 dB

-- Set Right Volume to +3 dB
reaper.TrackFX_SetParam(track, fx, 3, 0.55)  -- normalized value approx for +3 dB

reaper.TrackList_AdjustWindows(false)
reaper.UpdateArrange()

reaper.ShowMessageBox("Test complete.\nLeft = -3 dB, Right = +3 dB.", "OK", 0)

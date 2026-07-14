-- Sweep-test the JSFX parameter mapping for Left Volume (Param 0)

local track = reaper.GetSelectedTrack(0, 0)
if not track then
  reaper.ShowMessageBox("Select the folder track first.", "Error", 0)
  return
end

local fx = 3  -- JSFX index
local param = 0 -- Left Volume

reaper.ShowConsoleMsg("Normalized -> Displayed dB\n")

for i = 0, 10 do
  local norm = i / 10
  reaper.TrackFX_SetParam(track, fx, param, norm)
  local _, dB = reaper.TrackFX_GetFormattedParamValue(track, fx, param, "")
  reaper.ShowConsoleMsg(string.format("%.2f -> %s\n", norm, dB))
end

reaper.ShowMessageBox("Sweep complete. Check ReaScript console.", "Done", 0)

--RESULT

--    Normalized -> Displayed dB
--    0.00 -> 0.0
--    0.10 -> 0.0
--    0.20 -> 0.0
--    0.30 -> 0.0
--    0.40 -> 0.0
--    0.50 -> 1.0
--    0.60 -> 1.0
--    0.70 -> 1.0
0--    .80 -> 1.0
--    0.90 -> 1.0
--    1.00 -> 1.0

-- ⭐ The JSFX you’re using does not expose real dB values at all.
-- It only exposes two states:

-- Code
-- 0.00–0.49 → “0.0”
-- 0.50–1.00 → “1.0”
-- That means:

-- The “Left Volume (dB)” slider is not actually a dB slider

-- It’s a binary gain switch

-- It only has two values

-- The displayed “0.0” and “1.0” are not dB, they’re just labels

-- This is why:

-- Setting 0.45 → “0.0”

-- Setting 0.55 → “1.0”

-- You never see –3 dB, +3 dB, etc.

-- The sweep shows no intermediate values

-- This JSFX is not a continuous gain control.
-- It’s basically a left/right on/off or polarity/gain toggle, not a real volume fader.
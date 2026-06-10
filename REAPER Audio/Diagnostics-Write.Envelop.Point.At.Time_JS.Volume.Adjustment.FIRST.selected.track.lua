-- UNIVERSAL SWEEP TEST
-- Works on ALL REAPER versions (no DeleteEnvelopePoint, no GetSetEnvelopeInfo_Value)

local function msg(s)
  reaper.ShowConsoleMsg(tostring(s) .. "\n")
end

local function find_js_volume_adjustment(track)
  local fx_count = reaper.TrackFX_GetCount(track)
  for fx = 0, fx_count - 1 do
    local _, name = reaper.TrackFX_GetFXName(track, fx, "")
    if name:find("Volume Adjustment") then
      return fx, name
    end
  end
  return nil, nil
end

local function write_sweep(track, fx_index, track_name)
  local param = 0  -- Adjustment (dB)

  -- Create/get envelope
  local env = reaper.GetFXEnvelope(track, fx_index, param, true)
  if not env then
    msg("  ❌ Could not get/create envelope for " .. track_name)
    return
  end

  -- Write 11 points: 0s..10s, values 0.0..1.0
  for i = 0, 10 do
    local t = i
    local v = i / 10
    reaper.InsertEnvelopePoint(env, t, v, 0, 0, false, true)
  end

  reaper.Envelope_SortPoints(env)
  msg("  ✅ Sweep written on " .. track_name)
end

-- MAIN
reaper.ShowConsoleMsg("")
local sel = reaper.CountSelectedTracks(0)
if sel == 0 then
  reaper.ShowMessageBox("Select at least one track.", "Error", 0)
  return
end

for i = 0, sel - 1 do
  local track = reaper.GetSelectedTrack(0, i)
  local _, name = reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "", false)
  name = name ~= "" and name or ("Track " .. (i+1))

  msg("TRACK " .. (i+1) .. ": " .. name)

  local fx_index, fx_name = find_js_volume_adjustment(track)
  if not fx_index then
    msg("  ❌ JS: Volume Adjustment not found.")
  else
    msg("  Found FX: " .. fx_name .. " at index " .. fx_index)
    write_sweep(track, fx_index, name)
  end
end

reaper.ShowMessageBox("Sweep complete.\nIf envelope is hidden, show it manually once.", "Done", 0)

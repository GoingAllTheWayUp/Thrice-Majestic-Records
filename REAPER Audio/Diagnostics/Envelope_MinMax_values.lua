reaper.ShowConsoleMsg("")
local function msg(s) reaper.ShowConsoleMsg(tostring(s) .. "\n") end

local track = reaper.GetSelectedTrack(0, 0)
if not track then msg("No track selected.") return end

local env = reaper.GetTrackEnvelopeByName(track, "Trim Volume")
if not env then msg("Trim Volume envelope not found.") return end

msg("=== TRIM VOLUME ENVELOPE RANGE TEST ===")

-- Count points
local point_count = reaper.CountEnvelopePoints(env)
msg("Point count: " .. point_count)

if point_count == 0 then
    msg("No points found. Please place min and max points manually.")
    return
end

-- Scan all points to find min/max
local min_val = 999
local max_val = -999

for i = 0, point_count - 1 do
    local ok, time, value, shape, tension, selected = reaper.GetEnvelopePoint(env, i)
    if ok then
        if value < min_val then min_val = value end
        if value > max_val then max_val = value end
    end
end

msg("Detected MIN value = " .. min_val)
msg("Detected MAX value = " .. max_val)

msg("=== END RANGE TEST ===")

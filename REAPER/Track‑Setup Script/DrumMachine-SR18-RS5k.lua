-- SR18 → RS5K Kit Builder (Notes 36–48)

--https://www.alesisdrums.com/multipads-and-drum-machines/sr18/
--https://reaper.fm
--ReaSamplOmatic5000

-- Creates a new track named <strong>SR18 RS5K Kit</strong>
-- Prompts the user for a folder containing WAV samples
-- Enumerates all <code>.wav</code> files in the folder
-- Loads the first 12 samples into RS5K instances
-- Maps MIDI notes to each pad
-- Names each RS5K instance using pad number, MIDI note, and filename

-- Enable Reaper Audio to your Audio Interfaces MIDI input.
-- Turn MIDI out "On" and record Channel Number on Alesis SR18.
-- Arm the track the script created, set input "MIDI", Set Audio Interface, Set Channel.

reaper.Undo_BeginBlock()

-- Create track
reaper.InsertTrackAtIndex(0, true)
local track = reaper.GetTrack(0, 0)
reaper.GetSetMediaTrackInfo_String(track, "P_NAME", "SR18 RS5K Kit", true)

-- Ask user for folder
local ok, folder = reaper.GetUserInputs(
    "Select folder containing samples",
    1,
    "Folder path:",
    "X:\\Path\\Audio\\Drum\\Kit\\Number12"
)

if not ok or folder == "" then return end

-- Get all WAV files in folder
local files = {}
local i = 0
while true do
    local file = reaper.EnumerateFiles(folder, i)
    if not file then break end
    if file:lower():match("%.wav$") then
        files[#files+1] = folder .. "\\" .. file
    end
    i = i + 1
end

-- MIDI notes 36–48 (12 pads)
-- Diffrent kits may utilize diffrent MIDI notes
local start_note = 36
local end_note = 48

for pad = start_note, end_note do
    local idx = pad - start_note + 1
    local sample = files[idx]
    if not sample then break end

    -- Add RS5K
    local fx = reaper.TrackFX_AddByName(track, "ReaSamplomatic5000", false, -1)

    -- Convert MIDI note → normalized param
    local norm = pad / 127

    -- Set note start/end
    reaper.TrackFX_SetParam(track, fx, 3, norm)
    reaper.TrackFX_SetParam(track, fx, 4, norm)

    -- Load sample
    reaper.TrackFX_SetNamedConfigParm(track, fx, "FILE0", sample)

    -- Rename RS5K instance
    local name = "Pad" .. (idx) .. ":MIDI" .. pad .. "_" .. sample:match("([^\\]+)$")
    reaper.TrackFX_SetNamedConfigParm(track, fx, "fx_name", name)
end

reaper.Undo_EndBlock("SR18 RS5K Kit Builder", -1)

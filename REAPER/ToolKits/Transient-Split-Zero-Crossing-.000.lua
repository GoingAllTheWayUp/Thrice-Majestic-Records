-- Split selected items at transients
-- No zero-crossing snap, no auto-fades changed permanently

reaper.Undo_BeginBlock()

local fade_toggle_cmd = 41194 -- Options: Toggle auto-fade in/out for split items

-- Save current auto-fade state
local fade_state = reaper.GetToggleCommandState(fade_toggle_cmd)

-- Ensure auto-fade is OFF while we split
if fade_state == 1 then
    reaper.Main_OnCommand(fade_toggle_cmd, 0)
end

local item_count = reaper.CountSelectedMediaItems(0)
if item_count > 0 then
    -- This already splits each selected item at its own transients
    reaper.Main_OnCommand(40757, 0) -- Item: Split items at transients
end

-- Restore previous auto-fade state
if fade_state == 1 then
    reaper.Main_OnCommand(fade_toggle_cmd, 0)
end

reaper.Undo_EndBlock("Split items at transients (no auto-fade)", -1)

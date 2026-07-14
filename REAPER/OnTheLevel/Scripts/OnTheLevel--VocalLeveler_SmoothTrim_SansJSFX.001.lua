-- VocalLeveler_SmoothTrim_OptionA.lua
-- Post-process Trim Volume envelope to add musical glides
-- Run AFTER your Step-6 script

---------------------------------------------------------
-- User-tunable parameters (in milliseconds)
---------------------------------------------------------
local ATTACK_MS     = 15   -- fade-in before each item
local RELEASE_MS    = 40   -- fade-out after each item
local MAX_GLIDE_MS  = 80   -- max glide time between items

-- Envelope curve shape:
-- 0 = linear, 3 = slow start / fast end (more "musical")
local SHAPE = 3

---------------------------------------------------------
-- Setup
---------------------------------------------------------
local track = reaper.GetSelectedTrack(0, 0)
if not track then return end

-- Your build: "Trim Volume"
local env = reaper.GetTrackEnvelopeByName(track, "Trim Volume")
if not env then return end

local item_count = reaper.CountTrackMediaItems(track)
if item_count == 0 then return end

local attack  = math.max(ATTACK_MS, 0)    / 1000.0
local release = math.max(RELEASE_MS, 0)   / 1000.0
local glide   = math.max(MAX_GLIDE_MS, 0) / 1000.0

---------------------------------------------------------
-- Helpers
---------------------------------------------------------
local function eval_env(t)
    local ok, value, _, _ = reaper.Envelope_Evaluate(env, t, 0, 0)
    if not ok then return nil end
    return value
end

local function insert_point(t, v, shape)
    reaper.InsertEnvelopePoint(env, t, v, shape or 0, 0, false, true)
end

---------------------------------------------------------
-- Pass 1: Per-item attack/release smoothing
---------------------------------------------------------
local items = {}

for i = 0, item_count - 1 do
    local item = reaper.GetTrackMediaItem(track, i)
    local pos  = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
    local len  = reaper.GetMediaItemInfo_Value(item, "D_LENGTH")
    local pos2 = pos + len
    items[i] = { item = item, pos = pos, pos2 = pos2 }
end

reaper.Undo_BeginBlock()

for i = 0, item_count - 1 do
    local pos  = items[i].pos
    local pos2 = items[i].pos2

    -- Attack: glide from pre-item value into item value
    if attack > 0 then
        local t0 = math.max(pos - attack, 0)
        local v_prev  = eval_env(t0)
        local v_start = eval_env(pos)
        if v_prev and v_start then
            insert_point(t0, v_prev,  SHAPE)
            insert_point(pos, v_start, SHAPE)
        end
    end

    -- Release: glide from item value into post-item value
    if release > 0 then
        local t1 = pos2 + release
        local v_end  = eval_env(pos2)
        local v_next = eval_env(t1)
        if v_end and v_next then
            insert_point(pos2, v_end,  SHAPE)
            insert_point(t1,   v_next, SHAPE)
        end
    end
end

---------------------------------------------------------
-- Pass 2: Musical glide between adjacent items
---------------------------------------------------------
if glide > 0 then
    for i = 0, item_count - 2 do
        local a = items[i]
        local b = items[i + 1]

        local endA   = a.pos2
        local startB = b.pos

        -- Only if there is a gap
        if startB > endA then
            local gap = startB - endA
            local g   = math.min(glide, gap)

            local t_start = endA
            local t_end   = endA + g
            if t_end > startB then t_end = startB end

            local v_start = eval_env(t_start)
            local v_end   = eval_env(t_end)

            if v_start and v_end then
                insert_point(t_start, v_start, SHAPE)
                insert_point(t_end,   v_end,   SHAPE)
            end
        end
    end
end

reaper.Envelope_SortPoints(env)
reaper.Undo_EndBlock("VocalLeveler Smooth Trim (Musical Glide)", -1)

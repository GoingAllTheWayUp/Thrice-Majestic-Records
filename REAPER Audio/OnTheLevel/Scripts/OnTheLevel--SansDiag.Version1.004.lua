---------------------------------------------------------
-- STEP 4: Read JSFX Variables
---------------------------------------------------------

reaper.gmem_attach("VocalLeveler")

local target_rms_JSFX = reaper.gmem_read(0)
local max_boost       = reaper.gmem_read(1)
local max_cut         = reaper.gmem_read(2)

---------------------------------------------------------
-- STEP 1–5: Scan items, measure RMS, compute trim dB
-- (Silent version: no printing, only calculations)
---------------------------------------------------------

local track = reaper.GetSelectedTrack(0, 0)
if not track then return end

local item_count = reaper.CountTrackMediaItems(track)
if item_count == 0 then return end

local target_rms = target_rms_JSFX

-- Precompute per‑item trim dB values
local trim_db_list = {}

for i = 0, item_count - 1 do
    local item = reaper.GetTrackMediaItem(track, i)
    local take = reaper.GetActiveTake(item)
    if take then
        local rms = reaper.NF_GetMediaItemAverageRMS(item)
        if rms and rms > -150 then
            local diff = target_rms - rms
            if diff >  max_boost then diff =  max_boost end
            if diff < -max_cut   then diff = -max_cut   end
            trim_db_list[i] = diff
        else
            trim_db_list[i] = nil
        end
    end
end

---------------------------------------------------------
-- STEP 6: WRITE TRIM ENVELOPE POINTS (FINAL FIXED)
---------------------------------------------------------

-- IMPORTANT: Your REAPER build exposes Trim Volume as "Trim Volume"
local env = reaper.GetTrackEnvelopeByName(track, "Trim Volume")
if not env then return end

-- Your measured envelope constants
local TRIM_MIN   = 0.0
local TRIM_MAX   = 852.77445440699
local TRIM_UNITY = 716.21785031261   -- 0 dB point
local TRIM_SCALE = TRIM_UNITY        -- amplitude 1.0 = 716.21785

for i = 0, item_count - 1 do
    local trim_db = trim_db_list[i]
    if trim_db then
        local item = reaper.GetTrackMediaItem(track, i)

        ---------------------------------------------------------
        -- Convert dB → amplitude → envelope value
        ---------------------------------------------------------
        local amp   = 10^(trim_db / 20)
        local value = amp * TRIM_SCALE

        if value < TRIM_MIN then value = TRIM_MIN end
        if value > TRIM_MAX then value = TRIM_MAX end

        ---------------------------------------------------------
        -- Item boundaries
        ---------------------------------------------------------
        local pos  = reaper.GetMediaItemInfo_Value(item, "D_POSITION")
        local len  = reaper.GetMediaItemInfo_Value(item, "D_LENGTH")
        local pos2 = pos + len

        ---------------------------------------------------------
        -- Write envelope points
        ---------------------------------------------------------
        reaper.InsertEnvelopePoint(env, pos,  value, 0, 0, false, true)
        reaper.InsertEnvelopePoint(env, pos2, value, 0, 0, false, true)
    end
end

reaper.Envelope_SortPoints(env)

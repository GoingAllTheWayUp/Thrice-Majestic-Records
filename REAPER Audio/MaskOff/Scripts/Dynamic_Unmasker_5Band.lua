-- Dynamic_Unmasker_5Band.lua
-- 5-band shaping, variable format, selected-track only

local GMEM_SPACE = "mask_unmask"

-- Per-band shaping variables (C-style arrays)
local sensitivity = {2000, 2000, 2000, 2000, 2000}
local strength    = {2.25, 2.25, 2.25, 2.25, 2.25}
local exponent    = {1.0,  1.0,  1.0,  1.0,  1.0}
local knee        = {0.0,  0.0,  0.0,  0.0,  0.0}
local maxcut      = {0.5,  0.5,  0.5,  0.5,  0.5}
local attack_ms   = {1,   1,   1,   1,   1}
local release_ms  = {0,  0,  0,  0,  0}

-- ReaEQ gain parameters for your preset
local band_gain_params = {1, 4, 7, 10, 13}

-- Attack/release envelopes
local env = {0, 0, 0, 0, 0}

reaper.gmem_attach(GMEM_SPACE)

-- Convert ms → smoothing coefficient
local function coeff(ms)
    local sr = reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 0, false)
    if sr == 0 then sr = 44100 end -- fallback if project uses audio device rate
    return 1 - math.exp(-1 / (ms * 0.001 * sr))
end

-- Full shaping pipeline for each band
local function shape(mask, i)
    -- Sensitivity + strength
    local amt = (mask * sensitivity[i]) * strength[i]

    -- Clamp
    if amt < 0 then amt = 0 end
    if amt > 1 then amt = 1 end

    -- Exponent
    amt = amt ^ exponent[i]

    -- Knee
    amt = amt * (1 - knee[i]) + (amt ^ exponent[i]) * knee[i]

    -- Max cut
    if amt > maxcut[i] then amt = maxcut[i] end

    -- Attack / release smoothing
    local a = coeff(attack_ms[i])
    local r = coeff(release_ms[i])
    local prev = env[i]

    local new
    if amt > prev then
        new = prev + a * (amt - prev)
    else
        new = prev + r * (amt - prev)
    end

    -- Clamp envelope
    if new < 0 then new = 0 end
    if new > 1 then new = 1 end

    env[i] = new
    return new
end

-- Convert shaped 0–1 → ReaEQ normalized gain
local function map_to_norm(v)
    -- 0 → 0.25 (0 dB)
    -- 1 → 0.00 (max cut)
    return 0.25 - (0.25 * v)
end

local function main()
    -- Selected track only
    local track = reaper.GetSelectedTrack(0, 0)
    if not track then return reaper.defer(main) end

    -- ReaEQ must be FX #0
    local fx = 0
    local _, fx_name = reaper.TrackFX_GetFXName(track, fx, "")
    if not fx_name:lower():find("reaeq") then
        return reaper.defer(main)
    end

    -- Read raw masks from JSFX
    local raw = {
        reaper.gmem_read(0),
        reaper.gmem_read(1),
        reaper.gmem_read(2),
        reaper.gmem_read(3),
        reaper.gmem_read(4)
    }

    -- Process each band
    for i = 1, 5 do
        local shaped = shape(raw[i], i)
        local norm = map_to_norm(shaped)
        reaper.TrackFX_SetParam(track, fx, band_gain_params[i], norm)
    end

    reaper.defer(main)
end

main()

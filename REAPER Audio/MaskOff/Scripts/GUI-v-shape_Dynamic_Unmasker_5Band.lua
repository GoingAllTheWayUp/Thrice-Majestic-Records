-- Dynamic_Unmasker_5Band.lua
-- 5-band shaping, driven by GUI JSFX (mask_gui) + analyzer (mask_unmask)

local GMEM_ANALYZER = "mask_unmask"
local GMEM_GUI      = "mask_gui"

-- Per-band shaping variables (will be filled from GUI)
local sensitivity = {0, 0, 0, 0, 0}
local strength    = {0, 0, 0, 0, 0}
local exponent    = {1, 1, 1, 1, 1}
local knee        = {0, 0, 0, 0, 0}
local maxcut      = {1, 1, 1, 1, 1}
local attack_ms   = {0, 0, 0, 0, 0}
local release_ms  = {0, 0, 0, 0, 0}

-- ReaEQ gain parameters for your preset
local band_gain_params = {1, 4, 7, 10, 13}

-- Attack/release envelopes
local env = {0, 0, 0, 0, 0}

-- ms → smoothing coefficient
local function coeff(ms)
    if ms <= 0 then return 1 end -- instant change if 0
    local sr = reaper.GetSetProjectInfo(0, "PROJECT_SRATE", 0, false)
    if sr == 0 then sr = 44100 end
    return 1 - math.exp(-1 / (ms * 0.001 * sr))
end

-- Read GUI values from mask_gui into arrays
local function update_from_gui()
    reaper.gmem_attach(GMEM_GUI)
    for i = 1, 5 do
        local base = (i - 1) * 7
        local sens   = reaper.gmem_read(base + 0)
        local str    = reaper.gmem_read(base + 1)
        local exp    = reaper.gmem_read(base + 2)
        local kn     = reaper.gmem_read(base + 3)
        local mc     = reaper.gmem_read(base + 4)
        local att    = reaper.gmem_read(base + 5)
        local rel    = reaper.gmem_read(base + 6)

        sensitivity[i] = sens or 0
        strength[i]    = str  or 0
        exponent[i]    = (exp ~= 0 and exp) or 1
        knee[i]        = kn   or 0
        maxcut[i]      = (mc ~= 0 and mc) or 1
        attack_ms[i]   = att  or 0
        release_ms[i]  = rel  or 0
    end
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

    if new < 0 then new = 0 end
    if new > 1 then new = 1 end

    env[i] = new
    return new
end

-- 0–1 → ReaEQ normalized gain (0 dB at 0.25)
local function map_to_norm(v)
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

    -- Update shaping params from GUI
    update_from_gui()

    -- Read raw masks from analyzer
    reaper.gmem_attach(GMEM_ANALYZER)
    local raw = {
        reaper.gmem_read(0),
        reaper.gmem_read(1),
        reaper.gmem_read(2),
        reaper.gmem_read(3),
        reaper.gmem_read(4)
    }

    -- Process each band
    for i = 1, 5 do
        local shaped = shape(raw[i] or 0, i)
        local norm = map_to_norm(shaped)
        reaper.TrackFX_SetParam(track, fx, band_gain_params[i], norm)
    end

    reaper.defer(main)
end

main()

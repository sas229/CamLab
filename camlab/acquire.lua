-- Declarations.
AIN = 0

-- Functions.
local checkInterval = LJ.CheckInterval
local read = MB.R
local write = MB.W
local function readAIN()
    for i = 0, 7 do
        AIN = read(i*2, 3) -- read AIN
        write(46000+(2*i), 3, AIN)
    end
    return
end

-- Initialisation.
LJ.setLuaThrottle(78)

local interval = read(46180, 0)/1000
LJ.IntervalConfig(0, interval)

-- Main loop.
while true do
    if checkInterval(0) then
        readAIN()
    end
end
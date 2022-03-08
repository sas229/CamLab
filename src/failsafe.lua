-- Declarations.
failsafe = 0

-- Functions.
local checkInterval = LJ.CheckInterval
local read = MB.R
local write = MB.W

-- Check the failsafe register every 1000ms.
LJ.IntervalConfig(0, 1000)

-- Main loop.
while true do
    if checkInterval(0) then
        -- Check USER_RAM for communications boolean.
        failsafe = read(46180, 0)
        if failsafe == 1 then
            -- Communication confirmed. Reset register.
            write(46180, 0, 0)
        else
            -- Communication lost. Stop output movement.
            write(44008, 1, 0)
            write(44010, 1, 0)
        end
    end
end
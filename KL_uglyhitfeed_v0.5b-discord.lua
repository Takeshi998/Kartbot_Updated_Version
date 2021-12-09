local hfp1a = {"","","",""} -- p1 names
local hfp2a = {"","","",""} -- p2 names
local hfp1c = {0,0,0,0} -- p1 colors
local hfp2c = {0,0,0,0} -- p2 colors
local hfia = {"","","",""} -- inflictor names
local hfsta = {0,0,0,0} -- start tic

local hitfeeddiscord = CV_RegisterVar({ -- if on, throws stuff on log so it can be read by other programs; non-dedicated servers should disable
	name = "hitfeeddiscord",
	defaultvalue = "on",
    flags = CV_NETVAR, -- only affects server so regular players shouldnt worry about it
	possiblevalue = CV_OnOff
})

local function hasVictim(index)
    return hfp2a[index] ~= "" and hfp2a[index] ~= nil
end

addHook("MapChange", do -- reset values
    hfp1a = {"","","",""}
    hfp2a = {"","","",""}
    hfp1c = {0,0,0,0}
    hfp2c = {0,0,0,0}
    hfia = {"","","",""}
    hfsta = {0,0,0,0}
end)

local function getDiscordEmoji(sprite)
    if(sprite == "K_ISGROW") return "<:KISGROW:824019994685210694> " end
    if(sprite == "K_ISSINK") return "<:KISSINK:824018506567778389>" end
    if(sprite == "K_ISBANA") return "<:KISBANA:824019994466975764>" end
    if(sprite == "K_ISORBN") return "<:KISORBN:824019994500530197>" end
    if(sprite == "K_ISJAWZ") return "<:KISJAWZ:824019994395410466>" end
    if(sprite == "K_ISBHOG") return "<:KISBHOG:824019994584154122>" end
    if(sprite == "K_ISSPB") return "<:KISSPB:824018506907254814>" end
    if(sprite == "K_ISMINE") return "<:KISMINE:824019994442465351>" end
    if(sprite == "K_ISEGGM") return "<:KISEGGM:824019994857701507>" end
    if(sprite == "K_ISINV1") return "<:KISINV6:824019994634747964>" end
    if(sprite == "K_ISTHNS") return "<:KISTHNS:824018506403938305>" end
    if(sprite == "K_ISRSHE") return "<:KISRSHE:824024478119755826>" end
    if(sprite == "K_ISSHOE") return "<:KISSHOE:824018506571710524>" end
    if(sprite == "K_ISPOGO") return "<:KISPOGO:824024477816848426>" end
    return sprite
end

local function setHitFeedStuff(player, inflictor, source, hitType)
    if(inflictor ~= nil and source ~= nil and source.player ~= nil)
        hfp1a[4],hfp2a[4],hfp1c[4],hfp2c[4],hfia[4],hfsta[4] = hfp1a[3],hfp2a[3],hfp1c[3],hfp2c[3],hfia[3],hfsta[3]
        hfp1a[3],hfp2a[3],hfp1c[3],hfp2c[3],hfia[3],hfsta[3] = hfp1a[2],hfp2a[2],hfp1c[2],hfp2c[2],hfia[2],hfsta[2]
        hfp1a[2],hfp2a[2],hfp1c[2],hfp2c[2],hfia[2],hfsta[2] = hfp1a[1],hfp2a[1],hfp1c[1],hfp2c[1],hfia[1],hfsta[1]
        hfp1a[1] = source.player.name
        hfp2a[1] = player.name
        hfp1c[1] = source.player.skincolor
        hfp2c[1] = player.skincolor
        -- get inflictor name - this bit is partailly based on the original hitfeed
        if(hitType == 2) then hfia[1] = "K_ISGROW"
        elseif(hitType == 4) then hfia[1] = "K_ISSINK"
        else
            local items = {
	        [MT_BANANA] = "K_ISBANA",
	        [MT_BANANA_SHIELD] = "K_ISBANA",
	        [MT_ORBINAUT] = "K_ISORBN",
	        [MT_ORBINAUT_SHIELD] = "K_ISORBN",
	        [MT_JAWZ] = "K_ISJAWZ",
	        [MT_JAWZ_DUD] = "K_ISJAWZ",
	        [MT_JAWZ_SHIELD] = "K_ISJAWZ",
	        [MT_BALLHOG] = "K_ISBHOG",
	        [MT_SPB] = "K_ISSPB",
	        [MT_SPBEXPLOSION] = "K_ISSPB",
	        [MT_MINEEXPLOSION] = "K_ISMINE",
	        [MT_SSMINE] = "K_ISMINE",
	        [MT_SSMINE_SHIELD] = "K_ISMINE",
            [MT_KARMAHITBOX] = "K_ISSPB",
	        }
	        if inflictor.type == MT_SPBEXPLOSION and not inflictor.extravalue1
		        hfia[1] = "K_ISEGGM"
	        elseif items[inflictor.type]
		        hfia[1] = items[inflictor.type]
            elseif (inflictor.player)
	            if (source.player.kartstuff[k_invincibilitytimer])
		            hfia[1] = "K_ISINV1"
	            elseif (inflictor.player.kartstuff[k_curshield] == 1)
		            hfia[1] = "K_ISTHNS"
	            elseif (source.player.kartstuff[k_sneakertimer] or source.player.kartstuff[k_pogospring])
		            if source.player.kartstuff[k_sneakertimer]
			            if source.player.kartstuff[k_rocketsneakertimer]
				            hfia[1] = "K_ISRSHE"
			            else
				            hfia[1] = "K_ISSHOE"
			            end
		            else
			            hfia[1] = "K_ISPOGO"
		            end
	            end
            end
        end
        hfsta[1] = leveltime
        -- if isdedicatedserver
        if hitfeeddiscord.value == 1 then
            local emoji = getDiscordEmoji(hfia[1])
            CONS_Printf(server, "[HITFEED] " + source.player.name +  " " + emoji + " " + player.name)
        end
            -- file = io.openlocal("hitfeed.log", "a")
            -- file:write(tostring(player) ..  "\t" .. tostring(inflictor) .. "\t" .. tostring(source) .. "\t" .. tostring(hitType))
            -- io.close(file)
        -- end 
    end
end

addHook("PlayerSpin", function(player, inflictor, source)
    if hitfeeddiscord.value == 1
        setHitFeedStuff(player, inflictor, source, 1)
    end
end)
addHook("PlayerSquish", function(player, inflictor, source) -- esmagou
    if hitfeeddiscord.value == 1
        setHitFeedStuff(player, inflictor, source, 2)
    end
end)
addHook("PlayerExplode", function(player, inflictor, source)
    if hitfeeddiscord.value == 1
        setHitFeedStuff(player, inflictor, source, 3)
    end
end)
addHook("MobjDamage", do
    if hitfeeddiscord.value == 1
        setHitFeedStuff(player, inflictor, source, 4)
    end
end) -- literalmente uma pia

local mod	= DBM:NewMod("Firemaw", "DBM-BWL", 1)
local L		= mod:GetLocalizedStrings()

mod:SetRevision("20261021000000")
mod:SetCreatureID(11983)
mod:SetEncounterID(613)
mod:SetModelID(6377)
mod:RegisterCombat("combat")

mod:RegisterEventsInCombat(
	"SPELL_CAST_START 23339 22539",
	"SPELL_AURA_APPLIED_DOSE 23341"
)

--(ability.id = 23339 or ability.id = 22539) and type = "begincast" or ability.id = 23341 and type = "cast"
local warnWingBuffet		= mod:NewCastAnnounce(23339, 2)
local warnShadowFlame		= mod:NewCastAnnounce(22539, 2)
local warnFlameBuffet		= mod:NewStackAnnounce(23341, 3)

-- AzerothCore: Shadow Flame at 18s, then 15-25s; Wing Buffet every 30s.
local timerWingBuffet		= mod:NewNextTimer(30, 23339, nil, nil, nil, 2)
local timerShadowFlameCD	= mod:NewCDTimer(15, 22539, nil, false, nil, 5)

function mod:OnCombatStart(delay)
	timerShadowFlameCD:Start(18-delay)
	timerWingBuffet:Start(-delay)
end

function mod:SPELL_CAST_START(args)
	local spellId = args.spellId
	if spellId == 23339 then
		warnWingBuffet:Show()
		timerWingBuffet:Start()
	elseif spellId == 22539 then
		warnShadowFlame:Show()
		timerShadowFlameCD:Start()
	end
end

function mod:SPELL_AURA_APPLIED_DOSE(args)
	local spellId = args.spellId
	if spellId == 23341 and args:IsPlayer() then
		local amount = args.amount or 1
		if (amount >= 4) and (amount % 2 == 0) then--Starting at 4, every even amount warn stack
			warnFlameBuffet:Show(amount)
		end
	end
end

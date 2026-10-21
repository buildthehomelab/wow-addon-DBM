local mod	= DBM:NewMod("Broodlord", "DBM-BWL", 1)
local L		= mod:GetLocalizedStrings()

mod:SetRevision("20261021000000")
mod:SetCreatureID(12017)
mod:SetEncounterID(612)
mod:SetModelID(14308)
mod:RegisterCombat("combat_yell", L.Pull)--L.Pull is backup for classic, since classic probably won't have ENCOUNTER_START to rely on and player regen never works for this boss

mod:RegisterEventsInCombat(
	"SPELL_CAST_SUCCESS 23331 25778",
	"SPELL_AURA_APPLIED 24573",
	"SPELL_AURA_REMOVED 24573"
)

-- AzerothCore: Blast Wave at 12s, then 20-35s; Knock Away at 30s, then 15-30s.
-- Cooldown bars show the earliest scheduled repeat; casting can delay execution.
--(ability.id = 25778 or ability.id = 23331 or ability.id = 24573) and type = "cast"
local warnBlastWave		= mod:NewSpellAnnounce(23331, 2)
local warnKnockAway		= mod:NewSpellAnnounce(25778, 3)
local warnMortal		= mod:NewTargetNoFilterAnnounce(24573, 2, nil, "Tank|Healer", 3)

local timerBlastWaveCD	= mod:NewCDTimer(20, 23331, nil, nil, nil, 2, nil, nil, true)
local timerKnockAwayCD	= mod:NewCDTimer(15, 25778, nil, nil, nil, 3, nil, nil, true)
local timerMortal		= mod:NewTargetTimer(5, 24573, nil, "Tank|Healer", 3, 5, nil, DBM_COMMON_L.TANK_ICON)

function mod:OnCombatStart(delay)
	timerBlastWaveCD:Start(12-delay)
	timerKnockAwayCD:Start(30-delay)
end

function mod:SPELL_CAST_SUCCESS(args)
	local spellId = args.spellId
	if spellId == 23331 and args:IsSrcTypeHostile() then
		warnBlastWave:Show()
		timerBlastWaveCD:Start()
	elseif spellId == 25778 then
		warnKnockAway:Show()
		timerKnockAwayCD:Start()
	end
end

function mod:SPELL_AURA_APPLIED(args)
	local spellId = args.spellId
	if spellId == 24573 and args:IsDestTypePlayer() then
		local destName = args.destName
		warnMortal:Show(destName)
		timerMortal:Start(destName)
	end
end

function mod:SPELL_AURA_REMOVED(args)
	local spellId = args.spellId
	if spellId == 24573 and args:IsDestTypePlayer() then
		timerMortal:Stop(args.destName)
	end
end

local mod	= DBM:NewMod("Majordomo", "DBM-MC", 1)
local L		= mod:GetLocalizedStrings()

mod:SetRevision("20250929220131")
mod:SetCreatureID(12018, 11663, 11664)
mod:SetEncounterID(671)

mod:SetModelID(12029)

mod:RegisterCombat("combat")
-- AzerothCore: Majordomo submits (turns friendly) instead of dying once his eight Flamewakers are dead,
-- so the kill is counted from the add deaths rather than boss deaths.
mod:DisableBossDeathKill()

mod:RegisterEventsInCombat(
	"SPELL_CAST_SUCCESS 20619 21075 20534 20618",
	"UNIT_DIED"
)

--[[
(ability.id = 20619 or ability.id = 21075 or ability.id = 20534) and type = "cast"
--]]
local warnTeleport			= mod:NewTargetNoFilterAnnounce(20534)
local warnDamageShield		= mod:NewSpellAnnounce(21075, 2)

local specWarnMagicReflect	= mod:NewSpecialWarningReflect(20619, "CasterDps", nil, 2, 1, 2)
local specWarnDamageShield	= mod:NewSpecialWarningReflect(21075, false, nil, 2, 1, 2)

local timerMagicReflect		= mod:NewBuffActiveTimer(10, 20619, nil, nil, nil, 5, nil, DBM_COMMON_L.DAMAGE_ICON)
local timerDamageShield		= mod:NewBuffActiveTimer(10, 21075, nil, nil, nil, 5, nil, DBM_COMMON_L.DAMAGE_ICON)
local timerTeleportCD		= mod:NewCDTimer(25, 20534, nil, nil, nil, 5, nil, DBM_COMMON_L.TANK_ICON)--25-30
local timerShieldCD			= mod:NewTimer(30.3, "timerShieldCD", nil, nil, nil, 6, nil, DBM_COMMON_L.DAMAGE_ICON)

local ADD_COUNT = 8 -- 4 Flamewaker Healers (11663) + 4 Flamewaker Elites (11664)
local deadAdds = {}

function mod:OnCombatStart(delay)
	table.wipe(deadAdds)
	timerTeleportCD:Start(19.4-delay)
	timerShieldCD:Start(27.8-delay)--27-30
end

function mod:SPELL_CAST_SUCCESS(args)
	if args.spellId == 20619 then
		specWarnMagicReflect:Show(BOSS)--Always a threat to casters
		specWarnMagicReflect:Play("stopattack")
		timerMagicReflect:Start()
		timerShieldCD:Start()
	elseif args.spellId == 21075 then
		if self.Options.SpecWarn21075reflect and not self:IsTrivial() then--Not a threat to high level melee
			specWarnDamageShield:Show(BOSS)
			specWarnDamageShield:Play("stopattack")
		else
			warnDamageShield:Show()
		end
		timerDamageShield:Start()
		timerShieldCD:Start()
	elseif args.spellId == 20534 or args.spellId == 20618 then -- 20618: AzerothCore's random-target teleport
		warnTeleport:Show(args.destName)
		timerTeleportCD:Start()
	end
end

function mod:UNIT_DIED(args)
	local cid = self:GetCIDFromGUID(args.destGUID)
	if (cid == 11663 or cid == 11664) and not deadAdds[args.destGUID] then
		deadAdds[args.destGUID] = true
		local count = 0
		for _ in pairs(deadAdds) do
			count = count + 1
		end
		if count >= ADD_COUNT then
			DBM:EndCombat(self)
		end
	end
end

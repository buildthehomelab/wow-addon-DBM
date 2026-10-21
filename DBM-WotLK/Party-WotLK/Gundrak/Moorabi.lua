local mod	= DBM:NewMod("Moorabi", "DBM-Party-WotLK", 5)
local L		= mod:GetLocalizedStrings()

mod.statTypes = "normal,heroic,mythic"

mod:SetRevision("20250929220131")
mod:SetCreatureID(29305)
mod:SetEncounterID(387)

mod:RegisterCombat("combat")

mod:RegisterEventsInCombat(
	"SPELL_CAST_START 55098"
)

-- local warnCopies			= mod:NewSpellAnnounce(55101, 4)

local specWarnTransform		= mod:NewSpecialWarningInterruptCount(55098, nil, nil, nil, 1, 2)

local timerTransform		= mod:NewCDTimer(10, 55098, nil, nil, nil, 4, nil, DBM_COMMON_L.INTERRUPT_ICON)--experimental

mod.vb.kickCount = 0

function mod:OnCombatStart()
	self.vb.kickCount = 0
end

function mod:SPELL_CAST_START(args)
	if args.spellId == 55098 then
		self.vb.kickCount = self.vb.kickCount + 1
		specWarnTransform:Show(args.sourceName, self.vb.kickCount)
		specWarnTransform:Play("kickcast")
		timerTransform:Start()
	end
end

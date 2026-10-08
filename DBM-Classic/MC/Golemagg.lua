local mod	= DBM:NewMod("Golemagg", "DBM-MC", 1)
local L		= mod:GetLocalizedStrings()

mod:SetRevision("20250929220131")
mod:SetCreatureID(11988)--, 11672
mod:SetEncounterID(670)

mod:SetModelID(11986)
mod:RegisterCombat("combat")

mod:RegisterEventsInCombat(
	"SPELL_CAST_SUCCESS 19798"
)

-- AzerothCore's Golemagg casts Earthquake 19798 below 10% health (classic ID 20553 is never used)
local warnQuake		= mod:NewSpellAnnounce(19798)

function mod:SPELL_CAST_SUCCESS(args)
	if args.spellId == 19798 then
		warnQuake:Show()
	end
end

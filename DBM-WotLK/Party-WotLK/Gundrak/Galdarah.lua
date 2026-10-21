local mod	= DBM:NewMod("Galdarah", "DBM-Party-WotLK", 5)
local L		= mod:GetLocalizedStrings()

mod.statTypes = "normal,heroic,mythic"

mod:SetRevision("20250929220131")
mod:SetCreatureID(29306)
mod:SetEncounterID(390)

mod:RegisterCombat("combat")

mod:RegisterEventsInCombat(
	"SPELL_CAST_SUCCESS 55250 59824 55292 59829 54956 59827 55297 55299"
)

local warnPhase1		= mod:NewAnnounce("TimerPhase1", 4, "Interface\\Icons\\Spell_Shadow_ShadesOfDarkness")
local warnPhase2		= mod:NewAnnounce("TimerPhase2", 4, "Interface\\Icons\\Spell_Shadow_ShadesOfDarkness")

local specWarnSlash		= mod:NewSpecialWarningMove(59824)

local timerStomp		= mod:NewCDTimer(10, 59829)
local timerSlash		= mod:NewCDTimer(17, 59824)
local timerCharge		= mod:NewCDTimer(16, 59827)
local timerPhase1		= mod:NewTimer(32, "TimerPhase1", 72262)
local timerPhase2		= mod:NewTimer(32, "TimerPhase2", 72262)

function mod:OnCombatStart(delay)
	self:SetStage(1)
	timerSlash:Start(11-delay)
	timerPhase2:Start(32-delay)
end

function mod:SPELL_CAST_SUCCESS(args)
	if args:IsSpellID(55250, 59824) then
		timerSlash:Start()
		specWarnSlash:Show()
	elseif args:IsSpellID(54956, 59827) then
		timerCharge:Start()
	elseif args.spellId == 55297 then
		self:SetForm(2)
	elseif args.spellId == 55299 then
		self:SetForm(1)
	elseif args:IsSpellID(55292, 59829) then
		timerStomp:Start()
	end
end

function mod:SetForm(stage)
	if self.vb.phase == stage then return end
	self:SetStage(stage)
	timerPhase1:Stop()
	timerPhase2:Stop()
	timerSlash:Stop()
	timerStomp:Stop()
	timerCharge:Stop()
	if stage == 2 then
		warnPhase2:Show()
		timerPhase1:Start()
		timerStomp:Start(7)
		timerCharge:Start(8)
	else
		warnPhase1:Show()
		timerPhase2:Start()
		timerSlash:Start(11)
	end
end

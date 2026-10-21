local mod = DBM:NewMod("Thekal", "DBM-ZG", 1)
local L = mod:GetLocalizedStrings()

mod:SetRevision("20250929220131")
mod:SetCreatureID(14509, 11348, 11347)
mod:SetEncounterID(789)

mod:SetBossHPInfoToHighest()
mod:DisableBossDeathKill() -- Instructs mod to ignore boss deaths, since Thekal dies twice
mod:RegisterCombat("combat")
mod:RegisterKill("yell", L.YellKill)

mod:RegisterEventsInCombat(
	"SPELL_CAST_START 24208",
	"SPELL_AURA_APPLIED 21060 12540 24169",
	"SPELL_AURA_REMOVED 21060 12540",
	"SPELL_CAST_SUCCESS 24183",
	"CHAT_MSG_MONSTER_EMOTE",
	"CHAT_MSG_MONSTER_YELL"
)

local warnSimulKill		= mod:NewAnnounce("WarnSimulKill", 1, 24173)
local warnBlind			= mod:NewTargetAnnounce(21060, 2)
local warnGouge			= mod:NewTargetAnnounce(12540, 2)
local warnPhase2		= mod:NewPhaseAnnounce(2)
local warnAdds			= mod:NewSpellAnnounce(24183, 3)

local specWarnHeal		= mod:NewSpecialWarningInterrupt(24208, "HasInterrupt", nil, nil, 1, 2)

local timerSimulKill	= mod:NewTimer(10, "TimerSimulKill", 24173)
local timerBlind		= mod:NewTargetTimer(10, 21060, nil, nil, nil, 3)
local timerGouge		= mod:NewTargetTimer(4, 12540, nil, nil, nil, 3)


mod.vb.priestDeathDeadline = 0

function mod:OnCombatStart()
	self.vb.priestDeathDeadline = 0
	self:SetStage(1)
end

function mod:SPELL_CAST_START(args)
	if args.spellId == 24208 and args:IsSrcTypeHostile() then
		if self:CheckInterruptFilter(args.sourceGUID, false, true) then
			specWarnHeal:Show(args.sourceName)
			specWarnHeal:Play("kickcast")
		end
	end
end

function mod:SPELL_AURA_APPLIED(args)
	if args.spellId == 24169 and args:GetDestCreatureID() == 14509 then
		self:SendSync("TigerForm")
	elseif args.spellId == 21060 and args:IsDestTypePlayer() then
		warnBlind:Show(args.destName)
		timerBlind:Start(args.destName)
	elseif args.spellId == 12540 and args:IsDestTypePlayer() then
		warnGouge:Show(args.destName)
		timerGouge:Start(args.destName)
	end
end

function mod:SPELL_AURA_REMOVED(args)
	if args.spellId == 21060 and args:IsDestTypePlayer() then
		timerBlind:Stop(args.destName)
	elseif args.spellId == 12540 and args:IsDestTypePlayer() then
		timerGouge:Stop(args.destName)
	end
end

function mod:SPELL_CAST_SUCCESS(args)
	if args.spellId == 24183 then
		warnAdds:Show()
	end
end

function mod:CHAT_MSG_MONSTER_EMOTE(msg)
	if msg == L.PriestDied then -- Starts timer before ressurection of adds.
		self:SendSync("PriestDied")
	end
end

function mod:CHAT_MSG_MONSTER_YELL(msg)
	if msg == L.YellPhase2 and self.vb.phase < 2 then -- Bossfight (tank and spank)
		-- Tiger Form aura marks the actual transition, several seconds after this yell.
	end
end

function mod:OnSync(msg)
	if not self:IsInCombat() then return end
	if msg == "PriestDied" then
		local now = GetTime()
		if now >= self.vb.priestDeathDeadline then
			self.vb.priestDeathDeadline = now + 10
			warnSimulKill:Show()
			timerSimulKill:Start()
		end
	elseif msg == "TigerForm" and self.vb.phase < 2 then
		self.vb.priestDeathDeadline = 0
		self:SetStage(2)
		warnPhase2:Show()
		timerSimulKill:Stop()
	end
end

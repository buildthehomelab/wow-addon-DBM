"""Execute real Lua 5.1 handlers through their registered combat-log events."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from test_mc_bwl import STUB
ROOT = Path(__file__).resolve().parents[1]
HARNESS = STUB.replace('o={args=args, calls={}}', 'o={kind=key,args=args,calls={}}') + r'''
DBM.Options={GroupOptionsBySpell=true}
DBM_CORE_L=setmetatable({}, {__index=function() return "%s" end})
TANK="Tank"
function GetRealmName() return realm or "ExampleRealm" end
function UnitGUID() return "player-guid" end
function UnitName() return "Player" end
function UnitIsDeadOrGhost() return false end
function GetTime() return simulatedTime or 0 end
function GetSpellInfo(id) return "spell"..id end
function table.wipe(t) for k in pairs(t) do t[k]=nil end end
DBM.GetSpellInfo=function(_,id) return GetSpellInfo(id) end
DBM.GetGroupMembers=function() return function() end end
function configure()
 mod.vb.phase=1
 mod.SetStage=function(self,phase) self.vb.phase=phase end
 mod.IsInCombat=function() return true end
 mod.IsDifficulty=function(_,...) for _,v in ipairs({...}) do if v==difficulty then return true end end return false end
 mod.IsHeroic=function() return difficulty=="heroic5" end
 mod.AntiSpam=function() return true end
 mod.CheckInterruptFilter=function() return true end
end
function dispatch(event,id,creature)
 local registered=false
 for _,entry in ipairs(events) do
  if entry:match("^(%S+)")==event and (entry==event or (" "..entry.." "):find(" "..id.." ",1,true)) then registered=true end
 end
 if not registered then return false end
 local args={spellId=id,destName="Player",sourceName="Boss",sourceGUID="boss-guid",destGUID="player-guid",amount=5,spellName="spell"..id,
  IsPlayer=function() return true end,IsPlayerSource=function() return true end,
  IsDestTypePlayer=function() return true end,IsDestTypeHostile=function() return true end,IsSrcTypeHostile=function() return true end,
  GetSrcCreatureID=function() return creature end,GetDestCreatureID=function() return creature end,
  IsSpellID=function(_,...) for _,v in ipairs({...}) do if v==id then return true end end return false end}
 mod[event](mod,args);return true
end
'''
class EncounterSync(unittest.TestCase):
 def load(self,path,difficulty='normal10',realm='ExampleRealm'):
  l=LuaRuntime();l.execute(HARNESS);g=l.globals();g.difficulty=difficulty;g.realm=realm
  l.execute((ROOT/path).read_text(encoding='utf-8-sig'));g.configure();return g
 def obj(self,g,kind,spell):
  for _,o in g.objects.items():
   if o.kind==kind and o.args[2]==spell:return o
  self.fail(f'{kind} for {spell} not found')
 def calls(self,o,method):return [c for _,c in o.calls.items() if c.method==method]
 def start(self,o):
  cs=self.calls(o,'Start');self.assertTrue(cs);a=cs[-1].args;v=a[1] if len(a) else o.args[1]
  return o.args[1]+v if isinstance(v,(int,float)) and v<=0 else v
 def test_registered_ability_handlers(self):
  cases=[
   ('DBM-Classic/AQ20/Kurinnaxx.lua','SPELL_AURA_APPLIED',25646,15348,'NewTargetTimer',25646,'Start'),
   ('DBM-Classic/ZG/Jeklik.lua','SPELL_AURA_REMOVED',23952,14517,'NewTargetTimer',23952,'Stop'),
   ('DBM-Classic/ZG/EdgeOfMadness.lua','SPELL_AURA_APPLIED',24664,15083,'NewBuffActiveTimer',24664,'Start'),
   ('DBM-Classic/Party-Classic/Gnomeregan/MekgineerThermaplugg.lua','SPELL_CAST_SUCCESS',10101,7800,'NewCDTimer',10101,'Start'),
   ('DBM-Classic/Party-Classic/ScarletMonastery/Herod.lua','SPELL_AURA_APPLIED',8989,3975,'NewCDTimer',8989,'Start'),
   ('DBM-BC/BlackTemple/TeronGorefiend.lua','SPELL_CAST_SUCCESS',40251,22871,'NewCDTimer',40251,'Start'),
   ("DBM-BC/Party-BC/MagistersTerrace/Kael'thas.lua",'SPELL_CAST_START',44224,24664,'NewBuffActiveTimer',44224,'Start'),
   ('DBM-BC/Party-BC/TK_Botanica/WarpSplinter.lua','SPELL_SUMMON',34730,17977,'NewCDTimer',34727,'Start'),
   ('DBM-WotLK/VoA/Koralon.lua','SPELL_CAST_SUCCESS',66725,35013,'NewCDTimer',66725,'Start'),
   ('DBM-WotLK/Party-WotLK/DrakTharon/Trollgore.lua','SPELL_CAST_SUCCESS',49380,26630,'NewNextTimer',59803,'Start'),
   ('DBM-WotLK/Ulduar/Ignis.lua','SPELL_CAST_SUCCESS',62546,33118,'NewCDTimer',63473,'Start'),
   ('DBM-WotLK/Ulduar/Ignis.lua','SPELL_CAST_SUCCESS',63474,33118,'NewCDTimer',63473,'Start'),
   ('DBM-WotLK/Naxx/ConstructQuarter/Grobbulus.lua','SPELL_CAST_SUCCESS',28157,15931,'NewCDTimer',54364,'Start'),
   ('DBM-WotLK/Party-WotLK/Gundrak/Galdarah.lua','SPELL_CAST_SUCCESS',55250,29306,'NewCDTimer',59824,'Start')]
  for path,event,spell,cid,kind,timer,method in cases:
   with self.subTest(path=path,event=event,spell=spell):
    g=self.load(path);self.assertTrue(g.dispatch(event,spell,cid));self.assertTrue(self.calls(self.obj(g,kind,timer),method))
 def test_opening_then_repeat(self):
  cases=[
   ('DBM-Classic/AQ20/Kurinnaxx.lua',25656,5,'SPELL_CREATE',25648,5),
   ('DBM-Classic/Party-Classic/Maraudon/PrincessTheradras.lua',21909,15,'SPELL_CAST_SUCCESS',21909,30),
   ('DBM-BC/Party-BC/Auct_ShadowLabyrinth/Inciter.lua',33676,24,'SPELL_CAST_SUCCESS',33676,50),
   ('DBM-BC/Party-BC/Auct_Tombs/Tavarok.lua',32361,12,'SPELL_AURA_APPLIED',32361,15),
   ('DBM-WotLK/VoA/Toravon.lua',72034,25,'SPELL_CAST_START',72034,40),
   ('DBM-WotLK/VoA/Emalon.lua',65279,40,'SPELL_CAST_START',65279,40),
   ('DBM-WotLK/VoA/Koralon.lua',66725,30,'SPELL_CAST_SUCCESS',66725,45),
   ('DBM-WotLK/Party-WotLK/HallsOfLightning/Loken.lua',52960,15,'SPELL_CAST_START',52960,15),
   ('DBM-WotLK/Naxx/ConstructQuarter/Grobbulus.lua',54364,10,'SPELL_CAST_SUCCESS',28157,20)]
  for path,spell,opening,event,trigger,repeat in cases:
   with self.subTest(path=path,spell=spell):
    g=self.load(path);g.mod.OnCombatStart(g.mod,2);o=self.obj(g,'NewCDTimer',spell)
    self.assertEqual(self.start(o),opening-2);self.assertTrue(g.dispatch(event,trigger,0));self.assertEqual(self.start(o),repeat)
 def test_herod_enrage_does_not_restart_whirlwind(self):
  g=self.load('DBM-Classic/Party-Classic/ScarletMonastery/Herod.lua');g.dispatch('SPELL_AURA_APPLIED',8269,3975)
  self.assertFalse(self.calls(self.obj(g,'NewCDTimer',8989),'Start'))
 def test_jeklik_transition_starts_heal(self):
  g=self.load('DBM-Classic/ZG/Jeklik.lua');g.dispatch('SPELL_AURA_REMOVED',23966,14517)
  self.assertEqual(self.start(self.obj(g,'NewCDTimer',23954)),25)
 def test_huhuran_keeps_sting_and_poison_at_berserk(self):
  g=self.load('DBM-Classic/AQ40/Huhuran.lua');g.dispatch('SPELL_AURA_APPLIED',26068,15509)
  for spell in (26180,26053):self.assertFalse(self.calls(self.obj(g,'NewCDTimer',spell),'Stop'))
  self.assertTrue(self.calls(self.obj(g,'NewCDTimer',26051),'Stop'))
 def test_gluth_decimate_difficulty_and_repeat(self):
  for difficulty,expected in [('normal10',110),('normal25',90)]:
   with self.subTest(difficulty=difficulty):
    g=self.load('DBM-WotLK/Naxx/ConstructQuarter/Gluth.lua',difficulty);g.mod.OnCombatStart(g.mod,2);o=self.obj(g,'NewCDTimer',28374)
    self.assertEqual(self.start(o),expected-2);g.mod.SPELL_DAMAGE(g.mod,None,None,None,None,None,None,28375);self.assertEqual(self.start(o),expected)
 def test_loatheb_doom_accelerates_at_sixth_cast(self):
  g=self.load('DBM-Classic/VanillaNaxx/PlagueQuarter/Loatheb.lua');o=self.obj(g,'NewNextTimer',29204)
  for count in range(1,10):
   g.dispatch('SPELL_CAST_SUCCESS',29204,16011);self.assertEqual(self.start(o),30 if count<6 else 15)
 def test_thekal_preserves_first_resurrection_deadline(self):
  g=self.load('DBM-Classic/ZG/Thekal.lua');o=self.obj(g,'NewTimer','TimerSimulKill')
  g.mod.OnSync(g.mod,'PriestDied');self.assertEqual(self.start(o),10)
  g.simulatedTime=5;o.remaining=5;g.mod.OnSync(g.mod,'PriestDied');self.assertEqual(len(self.calls(o,'Start')),1)
  g.simulatedTime=10;o.remaining=0;g.mod.OnSync(g.mod,'PriestDied');self.assertEqual(len(self.calls(o,'Start')),2)
  g.mod.OnSync(g.mod,'TigerForm');self.assertEqual(g.mod.vb.phase,2);self.assertTrue(self.calls(o,'Stop'))
 def test_thekal_hidden_bar_does_not_reset_logical_window(self):
  g=self.load('DBM-Classic/ZG/Thekal.lua');g.mod.OnCombatStart(g.mod)
  o=self.obj(g,'NewTimer','TimerSimulKill');g.mod.Options.TimerSimulKill=False
  g.mod.OnSync(g.mod,'PriestDied');self.assertEqual(g.mod.vb.priestDeathDeadline,10)
  # A disabled timer never creates a bar; it reports zero remaining even at t=9.
  o.remaining=0;g.simulatedTime=9;g.mod.OnSync(g.mod,'PriestDied')
  self.assertEqual(len(self.calls(o,'Start')),1);self.assertEqual(g.mod.vb.priestDeathDeadline,10)
  g.simulatedTime=10;g.mod.OnSync(g.mod,'PriestDied')
  self.assertEqual(len(self.calls(o,'Start')),2);self.assertEqual(g.mod.vb.priestDeathDeadline,20)
  g.mod.OnSync(g.mod,'TigerForm');self.assertEqual(g.mod.vb.priestDeathDeadline,0)
 def test_galdarah_both_forms_and_charge_recovery(self):
  g=self.load('DBM-WotLK/Party-WotLK/Gundrak/Galdarah.lua');g.mod.OnCombatStart(g.mod,2)
  for _ in range(2):
   self.assertTrue(g.dispatch('SPELL_CAST_SUCCESS',55297,29306));self.assertEqual(g.mod.vb.phase,2)
   charge=self.obj(g,'NewCDTimer',59827);self.assertEqual(self.start(charge),8)
   g.dispatch('SPELL_CAST_SUCCESS',54956,29306);self.assertEqual(self.start(charge),16)
   self.assertTrue(g.dispatch('SPELL_CAST_SUCCESS',55299,29306));self.assertEqual(g.mod.vb.phase,1)
   self.assertEqual(self.start(self.obj(g,'NewCDTimer',59824)),11)
 def test_eck_opening_uses_server_berserk(self):
  g=self.load('DBM-WotLK/Party-WotLK/Gundrak/Eck.lua');g.mod.OnCombatStart(g.mod,2)
  self.assertEqual(self.start(self.obj(g,'NewBerserkTimer',None)),88)
 def test_ip40_creature_ids_are_scoped_to_ip40(self):
  # Execute the production mapping and decoder, not a Python reimplementation.
  s=(ROOT/'DBM-Core/DBM-Core.lua').read_text()
  code=s[s.index('local ip40NaxxCreatureIds = {'):s.index('function DBM:IsNonPlayableGUID')]
  l=LuaRuntime();l.execute('DBM={IsIP40Raid=function() return ip40 end}');l.execute(code);g=l.globals()
  cases={351000:15928,351004:15932,351019:15990,351020:16011,351037:30549,351084:16803}
  for raw,canonical in cases.items():
   guid=f'0xF1300{raw:05X}000001'
   g.ip40=True;self.assertEqual(g.DBM.GetCIDFromGUID(g.DBM,guid),canonical)
   g.ip40=False;self.assertEqual(g.DBM.GetCIDFromGUID(g.DBM,guid),raw)
  g.ip40=True
  for raw in (301000,15932,35013):
   self.assertEqual(g.DBM.GetCIDFromGUID(g.DBM,f'0xF1300{raw:05X}000001'),raw)
  self.assertEqual(g.DBM.GetCIDFromGUID(g.DBM,None),0)
  self.assertEqual(g.DBM.GetCIDFromGUID(g.DBM,42),0)
 def test_custom_loatheb_spore_emits_registered_warning(self):
  g=self.load('DBM-Classic/VanillaNaxx/PlagueQuarter/Loatheb.lua')
  self.assertTrue(g.dispatch('SPELL_CAST_SUCCESS',90006,351020));self.assertEqual(g.mod.vb.sporeCounter,1)
  self.assertEqual(self.start(self.obj(g,'NewNextTimer',29234)),13)
 def test_onyxia_ip40_timers_preserve_original_realm(self):
  for realm,flame,whelps,guards in [('ExampleRealm',10,90,False),('Onyxia_old',12.1,105,True)]:
   with self.subTest(realm=realm):
    g=self.load('DBM-Classic/VanillaOnyxia/Onyxia.lua',realm=realm);g.mod.OnCombatStart(g.mod,2)
    self.assertAlmostEqual(self.start(self.obj(g,'NewCDTimer',18435)),flame-2)
    self.assertEqual(self.obj(g,'NewNextTimer',17646).args[1],whelps)
    g.mod.OnSync(g.mod,'Phase2')
    self.assertEqual(bool(self.calls(self.obj(g,'NewNextTimer',68959),'Start')),guards)
    self.assertEqual(bool(self.calls(self.obj(g,'NewCDTimer',18584),'Start')),guards)
 def test_all_expansion_lua_syntax(self):
  l=LuaRuntime(encoding=None)
  for pack in ('Core','Classic','BC','WotLK'):
   for p in (ROOT/('DBM-'+pack)).rglob('*.lua'):
    with self.subTest(file=str(p.relative_to(ROOT))):
     # WoW's file loader accepts BOMs, unlike Lua's loadstring.
     ok,err=l.execute(b'local f,e=loadstring(...); return f ~= nil,e',p.read_bytes().removeprefix(b'\xef\xbb\xbf'))
     self.assertTrue(ok,repr(err))
if __name__=='__main__':unittest.main()

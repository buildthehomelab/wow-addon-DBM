"""Execute raid event handlers with a DBM test double. Requires lupa (Lua 5.1)."""
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
ROOT = Path(__file__).resolve().parents[1]
STUB = r'''
objects = {}; events = {}
function UnitClass() return "Mage", "MAGE" end
local noop = function() end
DBM_COMMON_L = setmetatable({}, {__index=function() return "" end})
local methods = {
 GetLocalizedStrings=function() return {Event="opening", EventTimer=eventTimer} end,
 SendSync=function(self, event, remaining) sync={event,remaining} end,
 RegisterEventsInCombat=function(self, ...) events={...} end,
 GetModByName=function() return {vb={}, Options={}} end,
}
DBM = setmetatable({}, {__index=methods})
function DBM:NewMod()
 mod = setmetatable({vb={}, Options={}}, {__index=function(self, key)
  if methods[key] then return methods[key] end
  if key:match('^New') then return function(_, ...)
   local args={...}; local o={args=args, calls={}}
   setmetatable(o, {__index=function(_, method) return function(_, ...)
    local call={...}; table.insert(o.calls, {method=method, args=call})
   end end})
   table.insert(objects, o); return o
  end end
  return noop
 end}); return mod
end
function spell(id)
 return {spellId=id, IsSrcTypeHostile=function() return true end}
end
function find(kind, id)
 for _, o in ipairs(objects) do
  if o.args[2]==id then
   if kind=='timer' and type(o.args[1])=='number' then return o end
  end
 end
end
'''
class RaidTimers(unittest.TestCase):
 def load(self, path):
  lua=LuaRuntime(); lua.execute(STUB); lua.execute((ROOT/'DBM-Classic'/path).read_text()); return lua
 def last_start(self, obj):
  calls=[c for _,c in obj.calls.items() if c.method=='Start']
  self.assertTrue(calls)
  value = calls[-1].args[1] if len(calls[-1].args) else obj.args[1]
  return obj.args[1]+value if isinstance(value,(int,float)) and value <= 0 else value
 def test_broodlord(self):
  l=self.load('BWL/Broodlord.lua'); g=l.globals(); g.mod.OnCombatStart(g.mod,2)
  wave=g.find('timer',23331); knock=g.find('timer',25778)
  self.assertEqual(self.last_start(wave),10); self.assertEqual(self.last_start(knock),28)
  self.assertIn('SPELL_CAST_SUCCESS 23331 25778',list(g.events.values()))
  g.mod.SPELL_CAST_SUCCESS(g.mod,g.spell(25778)); self.assertEqual(self.last_start(knock),15)
  g.mod.SPELL_CAST_SUCCESS(g.mod,g.spell(23331)); self.assertEqual(self.last_start(wave),20)
 def test_drakes(self):
  for boss in ['Firemaw','Ebonroc','Flamegor']:
   with self.subTest(boss=boss):
    l=self.load('BWL/'+boss+'.lua');g=l.globals();g.mod.OnCombatStart(g.mod,2)
    flame=g.find('timer',22539);wing=g.find('timer',23339)
    self.assertEqual(self.last_start(flame),16);self.assertEqual(self.last_start(wing),28)
    g.mod.SPELL_CAST_START(g.mod,g.spell(22539));self.assertEqual(self.last_start(flame),15)
    g.mod.SPELL_CAST_START(g.mod,g.spell(23339));self.assertEqual(self.last_start(wing),30)
 def test_vael(self):
  l=self.load('BWL/Vaelastrasz.lua');g=l.globals();g.mod.OnCombatStart(g.mod,2)
  timer=g.find('timer',18173);self.assertEqual(self.last_start(timer),13)
  g.mod.SPELL_CAST_SUCCESS(g.mod,g.spell(18173));self.assertEqual(self.last_start(timer),15)
  g.mod.OnSync(g.mod,'PullRP')
  self.assertEqual(self.last_start(g.objects[len(g.objects)]),41)
  l.execute('eventTimer=29')
  # The localization table is resolved at module load time.
  l.execute((ROOT/'DBM-Classic/BWL/Vaelastrasz.lua').read_text())
  g.mod.CHAT_MSG_MONSTER_YELL(g.mod,'opening')
  self.assertEqual(g.sync[1],'PullRP'); self.assertEqual(g.sync[2],29)
  g.mod.OnSync(g.mod,g.sync[1],str(g.sync[2]))
  self.assertEqual(self.last_start(g.objects[len(g.objects)]),29)
  g.mod.OnSync(g.mod,'PullRP','999')
  self.assertEqual(self.last_start(g.objects[len(g.objects)]),41)
 def test_magmadar(self):
  l=self.load('MC/Magmadar.lua');g=l.globals();g.mod.OnCombatStart(g.mod,2)
  timer=g.find('timer',19408);self.assertEqual(self.last_start(timer),7.5)
  g.mod.SPELL_CAST_SUCCESS(g.mod,g.spell(19408));self.assertEqual(self.last_start(timer),31)
 def test_nefarian(self):
  l=self.load('BWL/Nefarian.lua');g=l.globals()
  g.mod.SPELL_CAST_START(g.mod,g.spell(22686));self.assertEqual(self.last_start(g.find('timer',22686)),25)
 def test_lua51_syntax(self):
  l=LuaRuntime()
  for path in list((ROOT/'DBM-Classic/MC').rglob('*.lua')) + list((ROOT/'DBM-Classic/BWL').rglob('*.lua')):
   with self.subTest(file=str(path)):
    l.execute('assert(loadstring(...))',path.read_text())
if __name__=='__main__': unittest.main()

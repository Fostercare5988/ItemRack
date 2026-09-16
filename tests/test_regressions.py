"""Headless regression checks; requires lupa with its Lua 5.1 runtime.

Run: python -B tests/test_regressions.py [directory-containing-lupa]
Legacy Lua 5.0 table iteration is adapted only in the test harness.
WoW frame/event delivery and ClassicAPI bindings still require in-game tests.
"""

from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv.pop(1))
from lupa.lua51 import LuaRuntime

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "ItemRack.lua").read_text(encoding="utf-8")


def section(start, end):
    return SOURCE[SOURCE.index(start):SOURCE.index(end, SOURCE.index(start))]


def legacy_loops(code):
    return re.sub(
        r"(for\s+[\w, ]+\s+in\s+)([\w.\[\]]+)(\s+do\b)",
        r"\1pairs(\2)\3", code,
    )


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("""
        function table.wipe(t) for k in pairs(t) do t[k] = nil end end
        function frame()
            return {
                shown=false, events={},
                Show=function(s) s.shown=true end,
                Hide=function(s) s.shown=false end,
                IsShown=function(s) return s.shown end,
                IsVisible=function(s) return s.shown end,
                RegisterEvent=function(s,e) s.events[e]=true end,
                UnregisterEvent=function(s,e) s.events[e]=nil end,
                UnregisterAllEvents=function(s) table.wipe(s.events) end
            }
        end
        ItemRack = {Buffs={}}
        ItemRack_Settings = {EnableEvents='ON', Notify='ON'}
        ItemRack_Users = {test={Events={}}}
        Rack_User = {test={Sets={A={}, B={}}}}
        ItemRack_Events = {}
        ItemRack_RegisterFrame, ItemRackFrame, ItemRack_SetsFrame = frame(), frame(), frame()
        errors={}
        DEFAULT_CHAT_FRAME={AddMessage=function(s,msg) table.insert(errors,msg) end}
        now=0
        function GetTime() return now end
    """)
    return lua


def automation():
    lua = runtime()
    lua.execute("local user='test'\n" + legacy_loops(section(
        "--[[ Event Registration ]]--",
        '-- saves the items currently worn that EventSetName defines',
    )))
    lua.execute("""
        function addEvent(name, script, delay, trigger)
            ItemRack_Events[name]={script=script,delay=delay or 0,trigger=trigger or 'TEST'}
            ItemRack_Users.test.Events[name]={enabled=1,setname='A'}
            ItemRack_EnableEvent(name)
        end
        function tick(t) now=t; arg1=.3; ItemRack_RegisterFrame_OnUpdate() end
    """)
    return lua


def swap_runtime():
    lua = runtime()
    lua.execute("local user='test'\n" + legacy_loops(SOURCE[SOURCE.index("Rack = {"):]))
    lua.execute("""
        RackFrame=frame()
        inventory={}; bags={[0]={}}; capacity=8; pending={}; moves={}; clears=0
        itemTypes={two='INVTYPE_2HWEAPON',one='INVTYPE_WEAPON',shield='INVTYPE_SHIELD'}
        function Rack.GetItemInfo(bag,slot)
            local id = slot and bags[bag][slot] or (not slot and (inventory[bag] or 0))
            return nil,id,id,itemTypes[id] or 'INVTYPE_FINGER'
        end
        function Rack.GetNameByID(id) return id end
        function Rack.GetItemID(name) return name end
        -- Mock lookup at its boundary: the client's legacy numeric-loop exits
        -- are outside this swap test and behave differently under Lua 5.1.
        function Rack.FindItem(id,name,passive)
            for _,wanted in ipairs({id or name,name or id}) do
                for slot=1,capacity do
                    if bags[0][slot]==wanted and (passive or not Rack.LockList[0][slot]) then
                        return nil,0,slot
                    end
                end
                for slot=0,19 do
                    if (inventory[slot] or 0)==wanted and (passive or not Rack.LockList[-2][slot]) then
                        return slot
                    end
                end
            end
        end
        function Rack.ValidBag(bag) return bag==0 end
        function GetContainerNumSlots(bag) return bag==0 and capacity or 0 end
        function GetContainerItemLink(bag,slot) return bags[bag] and bags[bag][slot] end
        function GetInventoryItemLink(unit,slot) return inventory[slot] end
        function Rack.AnyLocked() return locked end
        function Rack.IsPlayerReallyDead() return dead end
        function UnitAffectingCombat() return combat end
        function SpellIsTargeting() return targeting end
        function CursorHasItem() return held~=nil end
        function ClearCursor() held=nil; clears=clears+1 end
        function ShowHelm() end
        function ShowCloak() end
        function pickup(location,slot)
            if not held then
                held={location=location,slot=slot}
                if reentrant then Rack.OnItemLockChanged() end
                return
            end
            if failDestination then return end
            local source=held; held=nil
            table.insert(moves,{source=source,location=location,slot=slot})
            local function apply()
                if failMoves then return end
                local item=source.location[source.slot]
                source.location[source.slot]=location[slot]
                location[slot]=item
            end
            if asynchronous then table.insert(pending,apply) else apply() end
            if reentrant then Rack.OnItemLockChanged() end
        end
        function PickupInventoryItem(slot) pickup(inventory,slot) end
        function PickupContainerItem(bag,slot) pickup(bags[bag],slot) end
        function flush(event)
            local work=pending; pending={}
            for _,apply in ipairs(work) do apply() end
            if event then Rack.OnItemLockChanged() end
        end
        function tickSwap(t)
            now=t; arg1=1.1; Rack.OnUpdate()
        end
        function clean()
            assert(not Rack.SwapRequest and not Rack.SetSwapping and not Rack.SwapIssuing)
            assert(#Rack.SwapQueueOrder==0 and not Rack.TimerEnabled('WaitToIterate'))
            assert(not RackFrame.events.ITEM_LOCK_CHANGED)
            for _,slots in pairs(Rack.LockList) do assert(next(slots)==nil) end
        end
        for i=0,19 do
            local f=frame(); f.SetTexture=function() end
            _G['ItemRackInv'..i..'Queue']=f
            ItemRack.Indexes=ItemRack.Indexes or {}
            ItemRack.Indexes[i]={paperdoll_slot='Paper'..i}
            _G['Paper'..i..'Queue']=f
        end
        Rack.Initialize()
        Rack_User.test.CurrentSet='Previous'
    """)
    return lua


class RegressionTests(unittest.TestCase):
    def test_lua_and_xml_syntax(self):
        lua = runtime()
        compile_lua = lua.eval("function(s,n) assert(loadstring(s,n)) end")
        for path in ROOT.glob("*.lua"):
            compile_lua(path.read_text(encoding="utf-8"), path.name)
        for path in ROOT.glob("*.xml"):
            root = ET.parse(path).getroot()
            for scripts in root.iter("{http://www.blizzard.com/wow/ui/}Scripts"):
                for handler in scripts:
                    compile_lua(handler.text or "", path.name + handler.tag)
            if path.name == "Bindings.xml":
                for binding in root:
                    compile_lua(binding.text or "", path.name)
        lua.execute((ROOT / "Events.lua").read_text(encoding="utf-8"))
        lua.execute("for _,v in pairs(ItemRack_DefaultEvents) do assert(loadstring(v.script)) end")

    def test_aura_fill_contract_and_stale_keys(self):
        lua = runtime()
        lua.execute("""
            auras={[3]={name='Drink',icon='drink-icon'}, [8]={name='Spirit Tap',icon='spirit-icon'}}
            slots={3,8}
            C_UnitAuras={
                GetAuraSlots=function(unit,filter,max,token,out)
                    assert(unit=='player' and filter=='HELPFUL' and type(out)=='table')
                    table.wipe(out)
                    for i,v in ipairs(slots) do out[i]=v end
                    return nil,#slots
                end,
                GetAuraDataBySlot=function(unit,slot) return auras[slot] end
            }
            function ItemRack_RegisterFrame_OnEvent(e)
                assert(e=='ITEMRACK_BUFFS_CHANGED' and arg1==ItemRack.Buffs)
            end
        """)
        lua.execute(section("local buffSlots = {}", "-- returns 1 if all pieces of setname"))
        lua.execute("""
            arg1='original'; ItemRack_BuffsChanged()
            assert(ItemRack.Buffs.Drink==1 and ItemRack.Buffs['spirit-icon']==1)
            assert(arg1=='original')
            slots={8}; ItemRack_BuffsChanged()
            assert(ItemRack.Buffs.Drink==nil and ItemRack.Buffs['drink-icon']==nil)
            slots={}; ItemRack_BuffsChanged(); assert(next(ItemRack.Buffs)==nil)
        """)

    def test_mount_state(self):
        lua = runtime()
        lua.execute(section("function ItemRack_PlayerMounted", "-- returns the name of the form"))
        lua.execute("""
            function IsMounted() return true end
            assert(ItemRack_PlayerMounted())
            function IsMounted() return false end
            assert(ItemRack_PlayerMounted()==false)
        """)

    def test_debounce_and_payload_release(self):
        lua = automation()
        lua.execute("""
            addEvent('delayed', 'runs=(runs or 0)+1; payload=arg1', 1)
            arg1='first'; ItemRack_RegisterFrame_OnEvent('TEST')
            now=.5; arg1='last'; ItemRack_RegisterFrame_OnEvent('TEST')
            tick(1.1); assert(runs==nil)
            tick(1.6); assert(runs==1 and payload=='last')
            assert(next(ItemRack.EventQueue)==nil and next(ItemRack.EventQueueArg1)==nil)
            assert(next(ItemRack.EventQueueSetName)==nil and not ItemRack_RegisterFrame.shown)
        """)

    def test_disable_suspend_and_reassociate(self):
        for action in (
            "ItemRack_DisableEvent('delayed')",
            "ItemRack_Settings.EnableEvents='OFF'; ItemRack_DisableAllEvents()",
            "ItemRack_SetsFrame:Show(); ItemRack_DisableAllEvents(); ItemRack_EnableAllEvents()",
            "ItemRack.CancelEvent('delayed'); ItemRack_Users.test.Events.delayed.setname='B'",
            "ItemRack_Users.test.Events.delayed.setname='B'",
            "ItemRack_Users.test.Events.delayed.enabled=nil",
            "ItemRack_DisableEvent('delayed'); ItemRack_Events.delayed=nil",
        ):
            with self.subTest(action=action):
                lua = automation()
                lua.execute("addEvent('delayed','runs=(runs or 0)+1',1); ItemRack_RegisterFrame_OnEvent('TEST')")
                lua.execute(action)
                lua.execute("tick(2); assert(runs==nil and next(ItemRack.EventQueue)==nil)")

    def test_nested_scripts_and_error_cleanup(self):
        lua = automation()
        lua.execute("""
            addEvent('inner', "assert(ItemRack.EventSetName=='B'); error('inner failure')", 0, 'INNER')
            ItemRack_Users.test.Events.inner.setname='B'
            addEvent('outer', [[
                assert(ItemRack.EventSetName=='A' and arg1=='payload')
                ItemRack_RegisterFrame_OnEvent('INNER')
                assert(ItemRack.EventSetName=='A' and ItemRack.EventEventName=='outer')
                this='changed'; event='changed'; arg1='changed'; arg2='changed'
                error('outer failure')
            ]])
            this='frame'; event='TEST'; arg1='payload'; arg2='second'
            ItemRack_RegisterFrame_OnEvent('TEST')
            assert(this=='frame' and event=='TEST' and arg1=='payload' and arg2=='second')
            assert(ItemRack.EventSetName==nil and ItemRack.EventEventName==nil)
            assert(#errors==2 and string.find(errors[1],'inner') and string.find(errors[2],'outer'))
            ItemRack.RunEventScript('not valid lua!', 'syntax', nil, nil, nil)
            assert(#errors==3 and arg1=='payload')
        """)

    def test_script_can_requeue_itself(self):
        lua = automation()
        lua.execute("""
            addEvent('again', "runs=(runs or 0)+1; ItemRack_RegisterFrame_OnEvent('TEST')", 1)
            ItemRack_RegisterFrame_OnEvent('TEST'); tick(2)
            assert(runs==1 and ItemRack.EventQueue.again==3 and ItemRack_RegisterFrame.shown)
            tick(4); assert(runs==2 and ItemRack.EventQueue.again==5)
        """)

    def test_event_list_shrinks_without_stale_sort_entries(self):
        lua = runtime()
        lua.execute("""
            function UnitClass() return 'Warrior' end
            function ItemRack_Validate_EventList_Buttons() end
            function ItemRack_Events_ScrollFrame_Update() end
            ItemRack.SelectedEvent=0
            ItemRack_Settings.ShowAllEvents='ON'
            ItemRack_Events={A={trigger='TEST'},B={trigger='TEST'},C={trigger='TEST'},D={trigger='TEST'}}
        """)
        lua.execute("local user='test'; local eventList={}; local eventListSize=1; local scratchTable={{},{}}; local scratchTableSize={}\n" + legacy_loops(section(
            "function ItemRack_Build_eventList()", "-- update for the list of events scrollframe",
        )) + "\nfunction checkList(n) assert(#scratchTable[2]==n and eventListSize==n+1) end")
        lua.execute("""
            ItemRack_Build_eventList(); checkList(4)
            ItemRack_Events={A={trigger='TEST'}}; ItemRack_Build_eventList(); checkList(1)
            ItemRack_Events={}; ItemRack_Build_eventList(); checkList(0)
        """)

    def test_swap_abort_drains_queue_and_stops_retry(self):
        lua = swap_runtime()
        lua.execute("""
            TrinketMenu={UpdateWornTrinkets=function()
                assert(#Rack.SwapQueueOrder==0 and not Rack.SwapRequest)
                notified=true
            end}
            for _,n in ipairs({0,1,2,5}) do
                local entries={}; notified=false
                for i=1,n do
                    local idx=Rack.GetFreeQueueEntry(); Rack.AddQueueEntry(idx)
                    table.insert(entries,idx)
                    Rack.SwapQueue[idx].direction='INVTOBAG'
                    Rack.SwapQueue[idx].started=true; Rack.SwapQueue[idx].deadline=10
                    Rack.SwapQueue[idx][0].id=0
                end
                Rack.StartTimer('WaitToIterate'); Rack.SetSwapping='A'
                Rack.ShutdownQueue(); clean(); assert(notified)
                for _,idx in ipairs(entries) do
                    local entry=Rack.SwapQueue[idx]
                    assert(not entry.direction and not entry.started and not entry.deadline)
                    assert(entry[0].id==nil)
                end
            end
            capacity=0; inventory[1]='hat'; inventory[2]='neck'
            Rack_User.test.Sets.A={[1]={id=0},[2]={id=0}}
            Rack.EquipSet('A'); clean()
            assert(#moves==0 and Rack_User.test.CurrentSet=='Previous')
        """)

    def test_two_hand_requirements_stay_runtime_only(self):
        for offhand in ("nil", "{id='shield',name='shield',old='older'}"):
            with self.subTest(offhand=offhand):
                lua = swap_runtime()
                lua.execute("Rack_User.test.Sets.A={[16]={id='two'},[17]=" + offhand + "}")
                lua.execute("""
                    local original=Rack_User.test.Sets.A[17]
                    inventory[16]='one'; inventory[17]='shield'; bags[0][1]='two'
                    asynchronous=true; reentrant=true
                    Rack.EquipSet('A')
                    assert(Rack_User.test.Sets.A[17]==original)
                    if original then assert(original.id=='shield' and original.old=='older') end
                    assert(Rack.SwapRequest.items[17].id==0 and #moves==1)
                    Rack.OnItemLockChanged() -- unrelated unlock, prerequisite still not observed
                    assert(#moves==1 and Rack_User.test.CurrentSet=='Previous')
                    flush(true) -- offhand removal complete, main-hand equip issued
                    assert(#moves==2 and Rack_User.test.CurrentSet=='Previous')
                    flush(true); clean()
                    assert(inventory[16]=='two' and not inventory[17])
                    assert(Rack_User.test.CurrentSet=='A' and Rack.SwapUndo.A[17]=='shield')
                    Rack.UnequipSet('A')
                    assert(Rack_User.test.CurrentSet=='A')
                    flush(true); assert(Rack_User.test.CurrentSet=='A')
                    flush(true); clean()
                    assert(inventory[16]=='one' and inventory[17]=='shield')
                    assert(Rack_User.test.CurrentSet=='Previous')
                """)

    def test_weapon_prerequisite_full_bags_and_failed_moves(self):
        for requested,worn in (("[16]={id='two'}", "inventory[17]='shield'; bags[0][1]='two'"),
                               ("[17]={id='shield'}", "inventory[16]='two'; bags[0][1]='shield'")):
            for failure in ("capacity=1", "failMoves=true", "failDestination=true"):
                with self.subTest(requested=requested,failure=failure):
                    lua = swap_runtime()
                    lua.execute("Rack_User.test.Sets.A={" + requested + "}; " + worn + "; " + failure)
                    lua.execute("""
                        Rack.EquipSet('A'); tickSwap(11); clean()
                        assert(#moves<=1 and Rack_User.test.CurrentSet=='Previous')
                        assert(not Rack_User.test.Sets.A[16] or Rack_User.test.Sets.A[16].id=='two')
                        assert(not Rack_User.test.Sets.A[17] or Rack_User.test.Sets.A[17].id=='shield')
                    """)

    def test_offhand_only_request_removes_two_hander(self):
        lua = swap_runtime()
        lua.execute("""
            inventory[16]='two'; bags[0][1]='shield'
            Rack_User.test.Sets.A={[17]={id='shield'}}
            Rack.EquipSet('A'); clean()
            assert(not inventory[16] and inventory[17]=='shield' and #moves==2)
            assert(Rack_User.test.Sets.A[16]==nil and Rack.SwapUndo.A[16]=='two')
            assert(Rack_User.test.CurrentSet=='A')
        """)

    def test_menu_prerequisite_reports_failure(self):
        lua = swap_runtime()
        lua.execute(section("local function unequip_2h_weapon()", "function ItemRack_Menu_OnClick")
                    + "\ntryUnequip=unequip_2h_weapon")
        lua.execute("""
            strfind=string.find
            UIErrorsFrame={AddMessage=function() end}
            function GetInventoryItemLink(unit,slot) return inventory[slot] and 'item:100' end
            function GetItemInfo() return nil,nil,nil,nil,nil,nil,nil,'INVTYPE_2HWEAPON' end
            inventory[16]='two'; capacity=0
            assert(tryUnequip()==false and #moves==0)
            capacity=8; failMoves=true
            assert(tryUnequip()==false and inventory[16]=='two')
            failMoves=false
            assert(tryUnequip()==true and not inventory[16])
        """)

    def test_swap_reconciliation_missing_events_and_timeouts(self):
        for failure in (False, True):
            with self.subTest(failure=failure):
                lua = swap_runtime()
                lua.execute("""
                    Rack_User.test.Sets.A={[13]={id='trinket'}}; bags[0][1]='trinket'
                    asynchronous=true; Rack.EquipSet('A')
                    assert(#moves==1 and Rack_User.test.CurrentSet=='Previous')
                    for i=1,3 do Rack.OnItemLockChanged() end
                    assert(#moves==1 and Rack.SwapRequest)
                """)
                if failure:
                    lua.execute("tickSwap(11); clean(); assert(Rack_User.test.CurrentSet=='Previous')")
                else:
                    lua.execute("flush(false); tickSwap(1); clean(); assert(Rack_User.test.CurrentSet=='A')")

    def test_unavailable_and_partial_requests_never_claim_completion(self):
        lua = swap_runtime()
        lua.execute("""
            Rack_User.test.Sets.A={[13]={id='trinket'},[14]={id='missing'}}
            bags[0][1]='trinket'; Rack.EquipSet('A')
            assert(inventory[13]=='trinket' and Rack_User.test.CurrentSet=='Previous')
            tickSwap(11); clean(); assert(Rack_User.test.CurrentSet=='Previous')
            locked=true; Rack_User.test.Sets.A={[13]={id='next'}}; bags[0][2]='next'
            Rack.EquipSet('A'); bags[0][2]=nil; locked=false; tickSwap(12); clean()
            assert(inventory[13]=='trinket' and #moves==1)
        """)

    def test_queue_serializes_requests_and_checks_unchanged_slots(self):
        lua = swap_runtime()
        lua.execute("""
            asynchronous=true
            inventory[1]='hat'; bags[0][1]='first'; bags[0][2]='second'
            Rack_User.test.Sets.A={[1]={id='hat'},[13]={id='first'}}
            Rack_User.test.Sets.B={[14]={id='second'}}
            Rack.EquipSet('A'); combat=true; Rack.EquipSet('B'); combat=false
            assert(#moves==1)
            flush(true); assert(Rack_User.test.CurrentSet=='A' and #moves==2)
            flush(true); clean(); assert(Rack_User.test.CurrentSet=='B')
            bags[0][3]='third'; Rack_User.test.Sets.A[13].id='third'
            Rack.EquipSet('A'); inventory[1]='different'; flush(true)
            assert(Rack_User.test.CurrentSet=='B')
            tickSwap(11); clean(); assert(Rack_User.test.CurrentSet=='B')
        """)

    def test_combat_completion_waits_for_actual_equipment(self):
        lua = swap_runtime()
        lua.execute("""
            combat=true; bags[0][1]='hat'; bags[0][2]='one'
            Rack_User.test.Sets.A={[1]={id='hat'},[16]={id='one'}}
            Rack.EquipSet('A'); clean()
            assert(inventory[16]=='one' and not inventory[1])
            assert(Rack_User.test.CurrentSet=='Previous' and Rack.PendingCombatRequest)
            Rack.EquipSet('A'); assert(Rack.CombatQueue[1]=='hat')
            combat=false; asynchronous=true; Rack.OnEvent('PLAYER_REGEN_ENABLED')
            assert(Rack_User.test.CurrentSet=='Previous')
            flush(true); clean(); assert(Rack_User.test.CurrentSet=='A')
            assert(not Rack.PendingCombatRequest)
        """)

    def test_ammo_only_and_noop_requests_complete(self):
        lua = swap_runtime()
        lua.execute("""
            Rack_User.test.Sets.A={[0]={id='ammo'}}; bags[0][1]='ammo'
            asynchronous=true; Rack.EquipSet('A')
            assert(Rack_User.test.CurrentSet=='Previous')
            flush(false); tickSwap(1); clean(); assert(Rack_User.test.CurrentSet=='A')
            Rack_User.test.Sets.B={[0]={id='ammo'}}
            Rack.EquipSet('B'); clean(); assert(Rack_User.test.CurrentSet=='B' and #moves==1)
        """)

    def test_dead_request_resumes_on_revival(self):
        lua = swap_runtime()
        lua.execute("""
            dead=true; bags[0][1]='hat'; Rack_User.test.Sets.A={[1]={id='hat'}}
            Rack.EquipSet('A'); clean()
            assert(#moves==0 and Rack_User.test.CurrentSet=='Previous' and Rack.PendingCombatRequest)
            dead=false; Rack.OnEvent('PLAYER_ALIVE'); clean()
            assert(inventory[1]=='hat' and Rack_User.test.CurrentSet=='A')
        """)

    def test_swap_waits_are_bounded_without_touching_user_cursor(self):
        for blocker in ("held={}", "targeting=true", "locked=true"):
            with self.subTest(blocker=blocker):
                lua = swap_runtime()
                lua.execute("Rack_User.test.Sets.A={[13]={id='trinket'}}; bags[0][1]='trinket'; " + blocker)
                lua.execute("""
                    Rack.EquipSet('A'); assert(#moves==0)
                    tickSwap(11); clean(); assert(#moves==0 and clears==0)
                    assert(Rack_User.test.CurrentSet=='Previous')
                """)

    def test_inventory_pair_is_not_swapped_twice(self):
        lua = swap_runtime()
        lua.execute("""
            inventory[11]='left'; inventory[12]='right'; asynchronous=true; reentrant=true
            Rack_User.test.Sets.A={[11]={id='right'},[12]={id='left'}}
            Rack.EquipSet('A'); assert(#moves==1)
            flush(true); clean(); assert(Rack_User.test.CurrentSet=='A')
            assert(inventory[11]=='right' and inventory[12]=='left')
        """)

    def test_duplicate_lifecycle_events_do_not_erase_deferred_work(self):
        lua = swap_runtime()
        lua.execute("""
            combat=true; asynchronous=true; bags[0][1]='hat'; bags[0][2]='one'
            Rack_User.test.Sets.A={[1]={id='hat'},[16]={id='one'}}
            Rack.EquipSet('A'); local owner=Rack.SwapRequest
            combat=false; Rack.OnEvent('PLAYER_REGEN_ENABLED'); Rack.OnEvent('PLAYER_ALIVE')
            assert(Rack.SwapRequest==owner and Rack.CombatQueue[1]=='hat')
            flush(true); assert(inventory[16]=='one' and not inventory[1])
            assert(Rack_User.test.CurrentSet=='Previous')
            Rack.OnEvent('PLAYER_UNGHOST'); flush(true); clean()
            assert(inventory[1]=='hat' and Rack_User.test.CurrentSet=='A')
            assert(not Rack.PendingCombatRequest and next(Rack.CombatQueueOwner)==nil)
        """)

    def test_abort_discards_only_owned_deferred_work_and_preserves_undo(self):
        lua = swap_runtime()
        lua.execute("""
            combat=true; capacity=3; inventory[17]='shield'
            bags[0][1]='two'; bags[0][2]='hat'; bags[0][3]='neck'
            Rack_User.test.Sets.A={[1]={id='hat',old='previousHat'},[16]={id='two'},oldsetname='Older'}
            Rack.SwapUndo.A={[17]='previousShield'}
            Rack.AddToCombatQueue(2,'neck') -- independent manual request
            Rack.EquipSet('A'); clean()
            assert(Rack.CombatQueue[1]==nil and Rack.CombatQueue[2]=='neck')
            assert(next(Rack.CombatQueueOwner)==nil and not Rack.PendingCombatRequest)
            assert(Rack.SwapUndo.A[17]=='previousShield')
            assert(Rack_User.test.Sets.A[1].old=='previousHat' and Rack_User.test.Sets.A.oldsetname=='Older')
            combat=false; Rack.OnEvent('PLAYER_REGEN_ENABLED'); clean()
            assert(not inventory[1] and inventory[2]=='neck' and Rack_User.test.CurrentSet=='Previous')
        """)

    def test_failed_undo_can_be_retried_without_persisting_scratch_sets(self):
        lua = swap_runtime()
        lua.execute("""
            inventory[13]='old'; bags[0][1]='new'; Rack_User.test.Sets.A={[13]={id='new'}}
            Rack.EquipSet('A'); failMoves=true; Rack.UnequipSet('A'); tickSwap(11); clean()
            assert(Rack_User.test.Sets.A[13].old=='old' and Rack_User.test.Sets.A.oldsetname=='Previous')
            assert(Rack_User.test.CurrentSet=='A')
            failMoves=false; Rack.UnequipSet('A'); clean()
            assert(inventory[13]=='old' and Rack_User.test.CurrentSet=='Previous')
            assert(Rack_User.test.Sets.A[13].old==nil and Rack.SwapUndo.A==nil)
            assert(Rack_User.test.Sets['Rack-Unequip-A']==nil)
        """)

    def test_undo_queued_during_active_swap_owns_its_snapshot(self):
        lua = swap_runtime()
        lua.execute("""
            asynchronous=true; inventory[16]='one'; inventory[17]='shield'; bags[0][1]='two'
            Rack_User.test.Sets.A={[16]={id='two'}}
            Rack.EquipSet('A'); Rack.UnequipSet('A')
            assert(Rack.SwapRequest.setname=='A' and Rack_User.test.Sets.A[16].old==nil)
            flush(true); flush(true)
            assert(Rack_User.test.CurrentSet=='A')
            flush(true); flush(true); clean()
            assert(inventory[16]=='one' and inventory[17]=='shield')
            assert(Rack_User.test.CurrentSet=='Previous' and Rack.SwapUndo.A==nil)
        """)

    def test_death_prerequisites_and_undo_stay_out_of_saved_requirements(self):
        lua = swap_runtime()
        lua.execute("""
            dead=true; inventory[16]='one'; inventory[17]='shield'; bags[0][1]='two'
            Rack_User.test.Sets.A={[16]={id='two'}}
            Rack.EquipSet('A'); assert(not Rack_User.test.Sets.A[17])
            dead=false; Rack.OnEvent('PLAYER_ALIVE'); clean()
            assert(Rack_User.test.CurrentSet=='A' and Rack.SwapUndo.A[17]=='shield')
            for i=0,19 do assert(Rack_User.test.Sets['Rack-CombatQueue'][i].id==nil) end
            Rack.UnequipSet('A'); clean()
            assert(inventory[16]=='one' and inventory[17]=='shield')
            assert(not Rack_User.test.Sets.A[17] and not Rack_User.test.Sets['Rack-Unequip-A'])
        """)

    def test_superseding_deferred_request_keeps_shared_slots_and_new_owner(self):
        lua = swap_runtime()
        lua.execute("""
            combat=true; bags[0][1]='hat'; bags[0][2]='chest'
            Rack_User.test.Sets.A={[1]={id='hat'}}
            Rack_User.test.Sets.B={[1]={id='hat'},[5]={id='chest'}}
            Rack.EquipSet('A'); local first=Rack.PendingCombatRequest
            Rack.EquipSet('B'); local second=Rack.PendingCombatRequest
            assert(first.cancelled and second~=first)
            assert(Rack.CombatQueue[1]=='hat' and Rack.CombatQueueOwner[1]==second)
            assert(not Rack.CompleteSwapRequest(first) and Rack_User.test.CurrentSet=='Previous')
            combat=false; Rack.OnEvent('PLAYER_REGEN_ENABLED'); clean()
            assert(inventory[1]=='hat' and inventory[5]=='chest' and Rack_User.test.CurrentSet=='B')
        """)

    def test_timeout_then_new_request_ignores_late_old_completion(self):
        lua = swap_runtime()
        lua.execute("""
            asynchronous=true; inventory[13]='old'; bags[0][1]='first'; bags[0][2]='second'
            Rack_User.test.Sets.A={[13]={id='first'}}; Rack_User.test.Sets.B={[13]={id='second'}}
            Rack.EquipSet('A'); local late=pending; pending={}; tickSwap(11); clean()
            Rack.EquipSet('B'); local owner=Rack.SwapRequest
            for _,apply in ipairs(late) do apply() end
            Rack.OnItemLockChanged(); Rack.OnItemLockChanged()
            assert(Rack.SwapRequest==owner and Rack_User.test.CurrentSet=='Previous')
            flush(true); clean(); assert(Rack_User.test.CurrentSet=='B')
            Rack.OnItemLockChanged(); tickSwap(22); clean()
            assert(Rack_User.test.CurrentSet=='B' and Rack_User.test.Sets.A[13].old==nil)
        """)

    def test_manual_deferred_cancellation_releases_pending_or_active_owner(self):
        for active in (False, "issued", "blocked"):
            with self.subTest(active=active):
                lua = swap_runtime()
                lua.execute("""
                    combat=true; bags[0][1]='hat'; bags[0][2]='one'
                    Rack_User.test.Sets.A={[1]={id='hat'}}
                """)
                if active:
                    lua.execute("asynchronous=true; Rack_User.test.Sets.A[16]={id='one'}")
                if active == "blocked":
                    lua.execute("targeting=true")
                lua.execute("""
                    Rack.EquipSet('A'); Rack.AddToCombatQueue(1,'hat')
                    targeting=false; tickSwap(1); flush(true); clean()
                    assert(not Rack.PendingCombatRequest and next(Rack.CombatQueue)==nil)
                    assert(next(Rack.CombatQueueOwner)==nil and Rack_User.test.CurrentSet=='Previous')
                    combat=false; Rack.OnEvent('PLAYER_ALIVE'); clean()
                    assert(Rack_User.test.CurrentSet=='Previous' and not inventory[1])
                """)
                if active == "blocked":
                    lua.execute("assert(#moves==0)")

    def test_flyout_cache_inputs(self):
        lua = runtime()
        lua.execute("""
            ItemRack_MenuFrame=frame()
            ItemRack_Settings.Soulbound='OFF'; ItemRack_Settings.AllowHidden='OFF'
            ItemRack_Settings.ShowEmpty='OFF'; ItemRack_Settings.RightClick='OFF'
            function IsAltKeyDown() return alt end
            scans=0
            function GetContainerNumSlots() scans=scans+1; return 0 end
            function GetInventoryItemLink() return nil end
            function sort_menu() end
        """)
        lua.execute(section("local cacheInvalid = true", '\tlocal mainorient = ItemRack_Users[user].MainOrient\n\n\tif relativeTo=="SET"') + "\nend")
        lua.execute("""
            ItemRack_BuildMenu(13,'BAR'); assert(scans==5)
            ItemRack_BuildMenu(13,'BAR'); assert(scans==5)
            alt=true; ItemRack_BuildMenu(13,'BAR'); assert(scans==10)
            ItemRack_BuildMenu(13,'CHARACTERSHEET'); assert(scans==15)
            for _,option in ipairs({'Soulbound','AllowHidden','ShowEmpty','RightClick'}) do
                local before=scans; ItemRack_Settings[option]='ON'
                ItemRack_BuildMenu(13,'CHARACTERSHEET'); assert(scans==before+5)
            end
            local before=scans; ItemRack.BankIsOpen=1
            ItemRack_BuildMenu(13,'CHARACTERSHEET'); assert(scans==before+12)
        """)

    def test_bank_transfer_uses_row_location_and_revalidates(self):
        lua = runtime()
        lua.execute("""
            ItemRack.BankIsOpen=1; ItemRack.InvOpen=13
            ItemRack.BankedItems={same=true}
            ItemRack.BaggedItems={{id='same',name='copy',bag=0,slot=2}}
            this={GetID=function() return 1 end, SetChecked=function() end}
            function SpellIsTargeting() return false end
            function CursorHasItem() return false end
            function ItemRack_BuildMenu() rebuilt=true end
            Rack={ClearLockList=function() end, GetItemInfo=function() return nil,currentID end}
            function Rack.FindSpace(bank) destination=bank and 'bank' or 'bags'; return 1,1 end
            moves=0
            function PickupContainerItem() moves=moves+1 end
            currentID='same'
        """)
        lua.execute("local cacheInvalid=false; local user='test'\n" + section(
            "function ItemRack_Menu_OnClick", "function ItemRack_MenuFrame_OnShow",
        ))
        lua.execute("""
            ItemRack_Menu_OnClick('LeftButton'); assert(destination=='bank' and moves==2)
            ItemRack.BaggedItems[1].bag=-1
            ItemRack_Menu_OnClick('LeftButton'); assert(destination=='bags' and moves==4)
            currentID='different'; ItemRack_Menu_OnClick('LeftButton')
            assert(rebuilt and moves==4)
        """)


if __name__ == "__main__":
    unittest.main(verbosity=2)

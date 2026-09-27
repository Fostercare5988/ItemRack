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

        timerHandles={}
        C_Timer={}
        function C_Timer.NewTimer(delay,callback)
            local h={deadline=now+math.max(delay,0),callback=callback,cancelled=false}
            function h:Cancel() self.cancelled=true end
            function h:IsCancelled() return self.cancelled end
            table.insert(timerHandles,h)
            return h
        end
        function runTimers(t)
            now=t
            local due={}
            for _,h in ipairs(timerHandles) do
                if not h.cancelled and h.deadline<=now then table.insert(due,h) end
            end
            for _,h in ipairs(due) do
                if not h.cancelled then h.callback(); h.cancelled=true end
            end
        end
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
        function tick(t) runTimers(t) end
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
        function GetCursorInfo() return cursorType or (held and 'item') end
        function ClearCursor() held=nil; clears=clears+1 end
        function ShowHelm() end
        function ShowCloak() end
        pickups=0
        function pickup(location,slot)
            pickups=pickups+1
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

        C_Container={
            GetContainerItemID=function(bag,slot) return bags[bag] and bags[bag][slot] end,
            HasContainerItem=function(bag,slot) return bags[bag] and bags[bag][slot]~=nil end
        }
        C_Item={EquipItemByName=function(location,slot)
            assert(slot>=1 and slot<=19)
            -- The real API clears held cursor state before resolving the source.
            if held then ClearCursor() end
            assert(not cursorType)
            local source=location.equipmentSlotIndex and inventory or bags[location.bagID]
            local sourceSlot=location.equipmentSlotIndex or location.slotIndex
            table.insert(moves,{source={location=source,slot=sourceSlot},location=inventory,slot=slot,direct=true})
            local function apply()
                if failMoves or failDestination then return end
                source[sourceSlot],inventory[slot]=inventory[slot],source[sourceSlot]
            end
            if asynchronous then table.insert(pending,apply) else apply() end
            if reentrant then Rack.OnItemLockChanged() end
        end}
        function flush(event)
            local work=pending; pending={}
            for _,apply in ipairs(work) do apply() end
            if event then Rack.OnItemLockChanged() end
        end
        function tickSwap(t)
            runTimers(t)
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
            assert(runs==1 and ItemRack.EventQueue.again==3 and not ItemRack_RegisterFrame.shown)
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
            function GetCursorInfo() return nil end
            function ItemRack_BuildMenu() rebuilt=true end
            Rack={ClearLockList=function() end, GetItemInfo=function() return nil,currentID end}
            function Rack.FindSpace(bank) destination=bank and 'bank' or 'bags'; return 1,1 end
            moves=0
            C_Container={SwapItems=function(sourceBag,sourceSlot,bag,slot)
                assert(sourceBag==ItemRack.BaggedItems[1].bag and sourceSlot==2)
                assert(bag==1 and slot==1)
                moves=moves+1; return true
            end}
            currentID='same'
        """)
        lua.execute("local cacheInvalid=false; local user='test'\n" + section(
            "function ItemRack_Menu_OnClick", "function ItemRack_MenuFrame_OnShow",
        ))
        lua.execute("""
            ItemRack_Menu_OnClick('LeftButton'); assert(destination=='bank' and moves==1)
            ItemRack.BaggedItems[1].bag=-1
            ItemRack_Menu_OnClick('LeftButton'); assert(destination=='bags' and moves==2)
            currentID='different'; ItemRack_Menu_OnClick('LeftButton')
            assert(rebuilt and moves==2)
        """)


    def test_structured_enchants_equipped_bag_and_missing(self):
        lua = runtime()
        lua.execute("""
            function overlay()
                local o=frame(); o.iconFrame=frame(); o.duration=frame()
                o.icon={SetTexture=function(s,v) s.texture=v end}
                o.duration.SetText=function(s,v) s.text=v end
                o.duration.SetTextColor=function(s,r,g,b) s.color={r,g,b} end
                return o
            end
            equipped={enchantOverlay=overlay()}; bagged={enchantOverlay=overlay()}
            enchants={main={true,3600000,40,101},bag={true,119000,4,202}}
            C_Item={
                GetItemTempEnchantInfo=function(loc)
                    local data=loc.equipmentSlotIndex==16 and enchants.main or
                        (loc.bagID==0 and loc.slotIndex==2 and enchants.bag)
                    if data then return unpack(data) end
                    return false,0,0,0
                end,
                GetEnchantInfo=function(id)
                    return id==101 and {name='Localized enchant',spellID=77} or {name='Stone'}
                end
            }
            C_Spell={GetSpellTexture=function(id) assert(id==77); return 'spell-icon' end}
        """)
        lua.execute(section("local function format_enchant_duration","local current_events_version") + """
            refreshEquipped=update_equipped_enchant; refreshBag=update_menu_weapon_enchant
        """)
        lua.execute("""
            refreshEquipped(16,equipped)
            assert(equipped.enchantOverlay.shown and equipped.enchantOverlay.icon.texture=='spell-icon')
            assert(equipped.enchantOverlay.duration.text=='1h')
            refreshBag(bagged,{bag=0,slot=2})
            assert(bagged.enchantOverlay.shown and bagged.enchantOverlay.duration.text=='4c')
            assert(string.find(bagged.enchantOverlay.icon.texture,'QuestionMark'))
            enchants.bag={true,59000,0,202}; refreshBag(bagged,{bag=0,slot=2})
            assert(bagged.enchantOverlay.duration.text=='59s' and bagged.enchantOverlay.duration.color[2]==.2)
            enchants.main=nil; refreshEquipped(16,equipped)
            assert(not equipped.enchantOverlay.shown)
            refreshBag(bagged,nil); assert(not bagged.enchantOverlay.shown)
            refreshEquipped(13,equipped); refreshEquipped(16,nil)
        """)

    def test_wear_requirements_use_player_eligibility(self):
        lua = runtime()
        lua.execute("""
            Rack={GetItemInfo=function() return nil,nil,nil,itemType end}
            C_Container={GetContainerItemID=function() return itemID end}
            C_PlayerInfo={CanUseItem=function(id) assert(id==900); return allowed end}
            itemID=900; allowed=true; itemType='INVTYPE_WEAPON'
        """)
        lua.execute(section("-- CanUseItem checks","-- the old central info gatherer") + """
            canWear=player_can_wear
        """)
        lua.execute("""
            assert(canWear(0,1,16)); assert(not canWear(0,1,17))
            ItemRack.CanWearOneHandOffHand=1; assert(canWear(0,1,17))
            allowed=false; assert(not canWear(0,1,16))
            allowed=true; itemType='INVTYPE_SHIELD'; assert(canWear(0,1,17))
            itemID=nil; assert(not canWear(0,1,17))
        """)

    def test_bound_filter_preserves_quest_and_conjured_exceptions(self):
        lua = runtime()
        lua.execute("""
            ItemRack_Settings.Soulbound='ON'
            Rack={GetItemInfo=function() return 'icon','900:0:0','Name','INVTYPE_HEAD',3 end}
            function GetContainerItemInfo() return 'icon',1 end
            bit={band=function(value,mask) assert(mask==2); return math.floor(value/2)%2*2 end}
            C_Item={
                GetItemData=function(loc) assert(loc.bagID==0 and loc.slotIndex==2); return data end,
                IsBound=function() return bound end
            }
        """)
        lua.execute("local user='test'\n"+section("-- the old central info gatherer","local function cursor_empty") + """
            function isFiltered() local _,_,_,_,bound=get_item_info(0,2); return bound end
        """)
        lua.execute("""
            data={bindType=2,flags=0}; bound=false; assert(not isFiltered())
            bound=true; assert(isFiltered())
            bound=false; data={bindType=4,flags=0}; assert(isFiltered())
            data={bindType=0,flags=2}; assert(isFiltered())
            data={bindType=1,flags=0}; assert(not isFiltered())
            data=nil; assert(not isFiltered())
        """)

    def test_compact_tooltip_reads_durability_and_cooldown(self):
        lua = runtime()
        lua.execute("""
            lines={}; name='Sword'; link='|cff0070ddSword'
            GameTooltip={
                GetItem=function() return name,link,900 end,
                ClearLines=function() lines={} end,
                AddLine=function(s,text) assert(text); table.insert(lines,text) end
            }
            local function durability() return current,maximum end
            C_Container={GetContainerItemDurability=function(bag,slot) assert(bag==-1 and slot==2); return durability() end}
            function GetInventoryItemDurability(slot) assert(slot==16); return durability() end
            function GetContainerItemCooldown() return start,duration end
            function GetInventoryItemCooldown() return start,duration end
            function SecondsToTime(seconds) return tostring(seconds)..'s' end
            DURABILITY_TEMPLATE='Durability %d / %d'; COOLDOWN_REMAINING='Cooldown remaining'
            function set_tooltip_anchor() end
            current=0; maximum=100; start=1; duration=20; now=11
        """)
        lua.execute(section("-- Rebuild a compact tooltip","--[[ Cooldowns ]]--") + """
            compact=shrink_tooltip
        """)
        lua.execute("""
            ItemRack.TooltipType='INVENTORY'; ItemRack.TooltipSlot=16
            compact(); assert(#lines==3 and lines[2]=='Durability 0 / 100')
            assert(lines[3]=='Cooldown remaining: 10s')
            ItemRack.TooltipType='BAG'; ItemRack.TooltipBag=-1; ItemRack.TooltipSlot=2
            current=nil; maximum=nil; start=0; duration=0
            compact(); assert(#lines==1)
            name=nil; compact(); assert(#lines==1)
        """)

    def test_action_use_reads_structured_identity_and_skips_sets(self):
        lua = runtime()
        lua.execute("""
            actionType='item'; actionID=900; tooltipID=901; reads=0; slots={}
            function GetActionInfo() return actionType,actionID end
            function IsEquippedAction() return true end
            function cursor_empty() return not busy end
            function GetInventoryItemID(unit,slot) assert(unit=='player'); return slots[slot] end
            function GetActionCooldown() return cooldown or 0 end
            function ItemRack_ReactUseInventoryItem(slot) used=slot end
            ItemRack_ItemTooltip={
                ClearLines=function() end,SetAction=function() reads=reads+1 end,
                GetItem=function() return nil,nil,tooltipID end
            }
        """)
        lua.execute(section("-- Observe item use","-- Inv slots are added"))
        lua.execute("""
            slots[13]=900; slots[14]=901
            ItemRack.OnUseAction(1); assert(used==13 and reads==0)
            used=nil; actionID=nil; ItemRack.OnUseAction(1); assert(used==14 and reads==1)
            used=nil; actionType='macro'; actionID=4
            ItemRack.OnUseAction(1); assert(used==14 and reads==2)
            used=nil; actionType='equipmentset'; actionID='PvP'
            ItemRack.OnUseAction(1); assert(not used and reads==2)
            actionType='spell'; ItemRack.OnUseAction(1); assert(not used and reads==2)
            actionType='item'; actionID=nil; tooltipID=nil
            ItemRack.OnUseAction(1); assert(not used and reads==3)
            actionID=900; busy=true; ItemRack.OnUseAction(1); assert(not used and reads==3)
        """)

    def test_native_timer_restart_cancel_render_and_errors(self):
        lua = swap_runtime()
        lua.execute("""
            runs=0
            Rack.CreateTimer('test',function() runs=runs+1 end,.5,1)
            Rack.StartTimer('test',2)
            local stale=Rack.TimerPool.test.handle
            assert(not RackFrame.shown and Rack.TimerEnabled('test'))
            runTimers(1); assert(runs==0)
            Rack.StartTimer('test',.25); stale.callback(); assert(runs==0)
            runTimers(1.3); assert(runs==1)
            runTimers(1.9); assert(runs==2)
            Rack.StopTimer('test'); runTimers(3); assert(runs==2)
            Rack.CreateTimer('once',function()
                runs=runs+1
                if runs==3 then Rack.StartTimer('once',1) end
            end,1)
            Rack.StartTimer('once',0); runTimers(3); assert(runs==3 and Rack.TimerEnabled('once'))
            runTimers(4); assert(runs==4 and not Rack.TimerEnabled('once'))
            Rack.CreateTimer('render',function() runs=runs+1 end,0,1)
            Rack.StartTimer('render'); assert(RackFrame.shown)
            Rack.OnUpdate(); assert(runs==5)
            Rack.StopTimer('render'); assert(not RackFrame.shown)
            Rack.CreateTimer('broken',function() error('bad callback') end,.5,1)
            Rack.StartTimer('broken'); runTimers(5)
            assert(not Rack.TimerEnabled('broken') and #errors==1)
            assert(string.find(errors[1],'broken') and string.find(errors[1],'bad callback'))
            Rack.CreateTimer('zero-once',function() runs=runs+1 end,0)
            Rack.StartTimer('zero-once'); assert(not RackFrame.shown)
            runTimers(5); assert(runs==6 and not Rack.TimerEnabled('zero-once'))
            runTimers(6); assert(runs==6)
        """)

    def test_cancelled_delayed_callback_cannot_consume_new_payload(self):
        lua = automation()
        lua.execute("""
            addEvent('delayed','runs=(runs or 0)+1; payload=arg1',1)
            arg1='old'; ItemRack_RegisterFrame_OnEvent('TEST')
            local stale=ItemRack.EventTimers.delayed
            now=.5; arg1='new'; ItemRack_RegisterFrame_OnEvent('TEST')
            stale.callback()
            assert(not runs and ItemRack.EventQueueArg1.delayed=='new')
            tick(1.6); assert(runs==1 and payload=='new')
            assert(next(ItemRack.EventTimers)==nil)
        """)

    def test_direct_equips_do_not_use_pickup_pairs(self):
        lua = swap_runtime()
        lua.execute("""
            bags[0][2]='ring:new-enchant'; bags[0][1]='ring:old-enchant'
            Rack_User.test.Sets.A={[11]={id='ring:new-enchant'}}
            Rack.EquipSet('A'); clean()
            assert(inventory[11]=='ring:new-enchant' and bags[0][1]=='ring:old-enchant')
            assert(#moves==1 and moves[1].direct and pickups==0)
            inventory[12]='other-ring'
            Rack_User.test.Sets.B={[11]={id='other-ring'},[12]={id='ring:new-enchant'}}
            Rack.EquipSet('B'); clean()
            assert(inventory[12]=='ring:new-enchant' and pickups==0 and #moves==2)
        """)

    def test_set_swap_waits_for_any_user_cursor(self):
        for cursor in ('item','spell','money','equipmentset'):
            with self.subTest(cursor=cursor):
                lua = swap_runtime()
                lua.execute(f"cursorType='{cursor}'")
                lua.execute("""
                    bags[0][1]='ring'; Rack_User.test.Sets.A={[11]={id='ring'}}
                    Rack.EquipSet('A'); tickSwap(11); clean()
                    assert(#moves==0 and clears==0 and cursorType)
                """)

    def test_cursor_created_during_native_equip_is_preserved(self):
        lua = swap_runtime()
        lua.execute("""
            local equip=C_Item.EquipItemByName
            C_Item.EquipItemByName=function(loc,slot)
                equip(loc,slot); held={location=bags[0],slot=8}
            end
            bags[0][1]='ring'; bags[0][2]='neck'
            Rack_User.test.Sets.A={[11]={id='ring'},[2]={id='neck'}}
            Rack.EquipSet('A'); clean()
            assert(#moves==1 and held and clears==0 and Rack_User.test.CurrentSet=='Previous')
        """)

    def test_free_slot_uses_occupancy_not_item_metadata(self):
        lua = swap_runtime()
        lua.execute("""
            bags[0][1]='uncached-item'; bags[0][2]='cached-item'
            C_Container.GetContainerItemID=function() return nil end
            assert(Rack.FindSpaceInBag(0)==3)
            Rack.LockList[0][3]=1; assert(Rack.FindSpaceInBag(0)==4)
        """)

    def test_default_event_migration_preserves_customizations(self):
        lua = runtime()
        lua.execute((ROOT/'Events.lua').read_text(encoding='utf-8'))
        lua.execute(r"""
            local prefix='local mount = (IsMounted and IsMounted()) or (UnitIsMounted and UnitIsMounted("player")) or ItemRack_PlayerMounted()'
            local old=prefix..'\nif not IR_MOUNT and mount then\n  EquipSet()\nelseif IR_MOUNT and not mount then\n  LoadSet()\nend\nIR_MOUNT=mount\n--[[Equips set to be worn while mounted.]]'
            ItemRack_Events.Mount={trigger='PLAYER_AURAS_CHANGED',delay=0,script=old}
            ItemRack_Events['Mount(Not ZG/AQ)']={trigger='CUSTOM',delay=0,script='my code'}
            ItemRack_UpgradeDefaultEvents()
            assert(ItemRack_Events.Mount.script==ItemRack_DefaultEvents.Mount.script)
            assert(ItemRack_Events['Mount(Not ZG/AQ)'].script=='my code')
            ItemRack_Events.Mount.script=old..'\nmy_custom_code()'
            ItemRack_UpgradeDefaultEvents()
            assert(ItemRack_Events.Mount.script==old..'\nmy_custom_code()')
            ItemRack_Events.Mount.script=old; ItemRack_Events.Mount.delay=2
            ItemRack_UpgradeDefaultEvents(); assert(ItemRack_Events.Mount.script==old)
            ItemRack_UpgradeDefaultEvents()
            function IsMounted() return mounted end
            function EquipSet() equips=(equips or 0)+1 end
            function LoadSet() restores=(restores or 0)+1 end
            mounted=false; assert(loadstring(ItemRack_DefaultEvents.Mount.script))()
            assert(not equips)
            mounted=true; assert(loadstring(ItemRack_DefaultEvents.Mount.script))()
            assert(equips==1)
            mounted=false; assert(loadstring(ItemRack_DefaultEvents.Mount.script))()
            assert(restores==1)
            arg1='EXHAUSTION'; assert(loadstring(ItemRack_DefaultEvents.Swimming.script))()
            assert(equips==1)
            arg1='BREATH'; assert(loadstring(ItemRack_DefaultEvents.Swimming.script))()
            assert(equips==2)
        """)

    def test_successful_item_cache_fill_refreshes_inventory(self):
        lua = runtime()
        lua.execute("""
            updates=0; scans=0
            Rack={
                PopulateBank=function() scans=scans+1 end,
                StartTimer=function(name) assert(name=='InvUpdate'); updates=updates+1 end
            }
        """)
        lua.execute("local cacheInvalid=false; local user='test'\n"+section(
            "function ItemRack_OnEvent","function ItemRack_SlashHandler",
        ))
        lua.execute("""
            arg2=nil; ItemRack_OnEvent('GET_ITEM_INFO_RECEIVED'); assert(updates==0)
            arg2=1; ItemRack_OnEvent('GET_ITEM_INFO_RECEIVED')
            assert(updates==1 and scans==1)
        """)

    def test_toc_sources_and_event_frame_have_no_obsolete_polling(self):
        toc=(ROOT/'ItemRack.toc').read_text(encoding='utf-8')
        for line in toc.splitlines():
            if line.strip() and not line.startswith('#'):
                self.assertTrue((ROOT/line.strip()).is_file(),line)
        self.assertNotIn('mountGUID.lua',toc)
        self.assertNotIn('IsMounted,',toc)
        xml=ET.parse(ROOT/'ItemRackSets.xml')
        register=next(node for node in xml.getroot().iter() if node.attrib.get('name')=='ItemRack_RegisterFrame')
        self.assertFalse(any(node.tag.endswith('OnUpdate') for node in register.iter()))


if __name__ == "__main__":
    unittest.main(verbosity=2)

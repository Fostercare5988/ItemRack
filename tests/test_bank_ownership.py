"""Exact bank-transfer ownership and persistence regressions.

Uses the existing Lua harness; no native DLL, server or rendering is simulated.
Run: python -B tests/test_bank_ownership.py [directory-containing-lupa]
"""
import os
import subprocess
import sys
import unittest
from pathlib import Path

if len(sys.argv)>1 and Path(sys.argv[1]).is_dir():
    sys.path.insert(0,sys.argv.pop(1))
import test_regressions as base

if os.environ.get('ITEMRACK_TEST_REVISION'):
    base.SOURCE=subprocess.check_output(['git','show',os.environ['ITEMRACK_TEST_REVISION']+':ItemRack.lua'],cwd=base.ROOT,text=True,encoding='utf8')

def bank_runtime():
    lua=base.swap_runtime()
    lua.execute('''
        strfind=string.find
        ItemRack.BankSlots={-1}; ItemRack.BankIsOpen=1
        ItemRack.BankedItems={['123:0:0']=1}
        bags[-1]={}; bankMoves={}
        function GetContainerNumSlots(bag) return (bag==0 or bag==-1) and 4 or 0 end
        function GetContainerItemLink(bag,slot)
            local id=bags[bag] and bags[bag][slot]
            return id and ('|Hitem:'..id..':0|h[Same name]|h')
        end
        function Rack.ValidBag(bag) return bag==0 or bag==-1 end
        function C_Container.SwapItems(b,s,db,ds)
            bankMoves[#bankMoves+1]={bag=b,slot=s,destBag=db,destSlot=ds}
            if closeDuringSend then Rack.BankClosed() end
            if cursorDuringSend then cursorType='spell' end
            return not rejectSend
        end
        ItemRack_MenuFrame=frame()
        Rack_User.test.Sets.A={[11]={id='123:0:0',name='Same name'},[12]={id='123:0:0',name='Same name'}}
    ''')
    return lua

class BankOwnershipTests(unittest.TestCase):
    def test_bank_lookup_requires_exact_id_not_a_link_substring(self):
        lua=bank_runtime()
        lua.execute('''
            bags[-1][1]='1123:0:0'; bags[-1][2]='123:0:01'; bags[-1][3]='123:0:0'
            local b,s=Rack.FindBankedItem('123:0:0'); assert(b==-1 and s==3)
            Rack.PullSetFromBank('A')
            assert(#bankMoves==1 and bankMoves[1].slot==3)
        ''')

    def test_pull_reserves_distinct_sources_before_server_updates(self):
        lua=bank_runtime()
        lua.execute('''
            bags[-1][1]='123:0:0'; bags[-1][2]='123:0:0'
            Rack.PullSetFromBank('A')
            assert(#bankMoves==2 and bankMoves[1].slot~=bankMoves[2].slot)
            assert(bankMoves[1].destSlot~=bankMoves[2].destSlot)
        ''')

    def test_push_reserves_distinct_sources_before_server_updates(self):
        lua=bank_runtime()
        lua.execute('''
            bags[0][1]='123:0:0'; bags[0][2]='123:0:0'
            Rack.PushSetToBank('A')
            assert(#bankMoves==2 and bankMoves[1].slot~=bankMoves[2].slot)
            assert(bankMoves[1].destSlot~=bankMoves[2].destSlot)
        ''')

    def test_bank_push_rejects_same_name_with_different_saved_identity(self):
        lua=bank_runtime()
        lua.execute('''
            bags[0][1]='123:999:0'
            function Rack.FindItem() return nil,0,1 end
            Rack.PushSetToBank('A'); assert(#bankMoves==0)
        ''')

    def test_closed_bank_and_active_swap_preserve_reservations(self):
        lua=bank_runtime()
        lua.execute('''
            bags[0][1]='123:0:0'; bags[-1][1]='123:0:0'
            Rack.LockList[0][4]=1; ItemRack.BankIsOpen=nil
            Rack.PullSetFromBank('A'); Rack.PushSetToBank('A')
            assert(#bankMoves==0 and Rack.LockList[0][4]==1)
            ItemRack.BankIsOpen=1; Rack.SetSwapping='Other'
            Rack.PullSetFromBank('A'); Rack.PushSetToBank('A')
            assert(#bankMoves==0 and Rack.LockList[0][4]==1)
        ''')

    def test_bank_close_cursor_and_rejected_send_stop_remaining_moves(self):
        for condition in ('closeDuringSend','cursorDuringSend','rejectSend'):
            lua=bank_runtime()
            lua.execute('''
                bags[-1][1]='123:0:0'; bags[-1][2]='123:0:0'
            '''+condition+'''=true
                Rack.PullSetFromBank('A'); assert(#bankMoves==1)
            ''')

    def test_late_bank_slot_event_does_not_reopen_bank_ownership(self):
        lua=bank_runtime()
        lua.execute('local cacheInvalid=false\n'+base.section('function ItemRack_OnEvent','function ItemRack_SlashHandler'))
        lua.execute('''
            Rack.StartTimer=function() end
            ItemRack_OnEvent('BANKFRAME_CLOSED')
            ItemRack_OnEvent('PLAYERBANKSLOTS_CHANGED')
            assert(not ItemRack.BankIsOpen and next(ItemRack.BankedItems)==nil)
            ItemRack_OnEvent('BANKFRAME_OPENED'); assert(ItemRack.BankIsOpen)
        ''')

    def test_signed_suffix_identity_is_retained_in_inventory_and_bank_index(self):
        lua=bank_runtime()
        lua.execute('''
            bags[-1][1]='123:45:-67'
            function GetItemInfo(link) return 'Same name',link,3,60,'Weapon','Sword',1,'INVTYPE_WEAPON','texture' end
            function GetInventoryItemQuality() return 3 end
        ''')
        lua.execute(base.section('function Rack.GetItemInfo','-- returns the name of an item in bag,slot'))
        lua.execute(base.section('function Rack.GetNameByID','-- returns true if the bagid'))
        lua.execute('''
            local _,id=Rack.GetItemInfo(-1,1); assert(id=='123:45:-67')
            Rack.PopulateBank(); assert(ItemRack.BankedItems['123:45:-67']==1)
            assert(Rack.GetNameByID('123:45:-67')=='Same name')
        ''')

    def test_saved_numeric_values_are_normalized_without_changing_valid_choices(self):
        lua=base.runtime()
        lua.execute('''
            function UnitClass() return 'Rogue','ROGUE' end
            ItemRack_Users.test={MainScale='old',XPos='123',YPos=false,Visible='OFF'}
        ''')
        lua.execute("local user='test'\nlocal ItemRackOpt_Defaults={MainScale=1,XPos=400,YPos=350}\n"+
                    base.legacy_loops(base.section('local function initialize_data()','local function initialize_display()'))+'\nLoadData=initialize_data')
        lua.execute('''
            LoadData(); local p=ItemRack_Users.test
            assert(p.MainScale==1 and p.XPos==123 and p.YPos==350 and p.Visible=='OFF')
            p.MainScale=1.35; p.XPos=-100; LoadData()
            assert(p.MainScale==1.35 and p.XPos==-100)
        ''')

    def test_normal_display_and_reset_use_valid_settings_and_preserve_bar(self):
        lua=base.runtime()
        lua.execute('''
            function UnitClass() return 'Rogue','ROGUE' end
            function uiFrame()
                local f=frame()
                f.SetScale=function(s,v) assert(type(v)=='number' and v>0); s.scale=v end
                f.ClearAllPoints=function() end
                f.SetPoint=function() end
                f.SetText=function(s,v) s.text=v end
                return f
            end
            ItemRack_InvFrame=uiFrame(); ItemRack_MenuFrame=uiFrame()
            ItemRack_IconFrame=uiFrame(); ItemRack_SetsFrame=uiFrame()
            ItemRackInv0Count=uiFrame(); CharacterAmmoSlotCount=uiFrame()
            ItemRack.OptInfo={}; Rack={StartTimer=function() end}
            function really_setpoint(f,p,r,rp,x,y) assert(type(x)=='number' and type(y)=='number') end
            function set_lock() end
            function update_keybindings() end
            function move_control() end
            function move_icon() end
            function make_escable() end
            function ItemRack_ChangeEventFont() end
            function draw_inv() draws=(draws or 0)+1 end
            function initialize_events() end
            ItemRack_Users.test={MainScale='old',XPos={},YPos=false,Bar={13,14},Visible='OFF'}
        ''')
        code=(base.section('local ItemRackOpt_Defaults = {','local user =')+"\nlocal user='test'\n"+
              base.section('local function initialize_data()','-- displays a quick tooltip note')+
              base.section('function ItemRack_Reset()','local function remove_inv')+
              '\nLoadData=initialize_data; LoadDisplay=initialize_display')
        lua.execute(base.legacy_loops(code))
        lua.execute('''
            LoadData(); LoadDisplay()
            assert(ItemRack_InvFrame.scale==1 and not ItemRack_InvFrame:IsShown() and draws==1)
            ItemRack_Users.test.MainScale=1.2; LoadData(); LoadDisplay()
            assert(ItemRack_MenuFrame.scale==1.2)
            ItemRack_Reset()
            assert(ItemRack_Users.test.MainScale==1 and #ItemRack_Users.test.Bar==2 and draws==3)
        ''')

if __name__=='__main__':
    unittest.main(verbosity=2)

"""Headless selection checks for the macro-facing poison swap helper.

Run: python -B tests/test_poison_swap.py [directory-containing-lupa]
The actual ClassicAPI equip request still needs in-game verification.
"""

from pathlib import Path
import sys
import unittest

if len(sys.argv) > 1:
    sys.path.insert(0, sys.argv.pop(1))
from lupa.lua51 import LuaRuntime


SOURCE = (Path(__file__).resolve().parents[1] / "PoisonSwap.lua").read_text(encoding="utf-8")


def runtime():
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute("""
        worn = {[17] = {id = 777, enchant = 101}}
        bags = {[0] = {}, [1] = {}, [2] = {}, [3] = {}, [4] = {}}
        messages, moves = {}, {}
        swapActive = false
        Rack = {IsEquipmentSwapActive = function() return swapActive end}
        DEFAULT_CHAT_FRAME = {
            AddMessage = function(_, message) table.insert(messages, message) end
        }
        function GetContainerNumSlots(_) return 4 end
        local function itemAt(location)
            if location.equipmentSlotIndex then
                return worn[location.equipmentSlotIndex]
            end
            return bags[location.bagID][location.slotIndex]
        end
        C_Item = {
            GetItemID = function(location)
                local item = itemAt(location)
                return item and item.id
            end,
            GetItemTempEnchantInfo = function(location)
                local item = itemAt(location)
                if item and item.enchant then
                    return true, 1800000, 40, item.enchant
                end
                return false, 0, 0, 0
            end,
            EquipItemByName = function(location, slot)
                table.insert(moves, {bag = location.bagID, bagSlot = location.slotIndex, slot = slot})
                worn[slot], bags[location.bagID][location.slotIndex] =
                    bags[location.bagID][location.slotIndex], worn[slot]
            end
        }
    """)
    lua.execute(SOURCE)
    return lua


class PoisonSwapTests(unittest.TestCase):
    def test_toggles_exact_copy_after_bag_rearrangement(self):
        lua = runtime()
        lua.execute("""
            bags[0][1] = {id = 777, enchant = 202}
            bags[0][3], bags[0][1] = bags[0][1], nil
            ItemRack_SwapPoison()
            assert(worn[17].enchant == 202)
            assert(bags[0][3].enchant == 101)
            assert(moves[1].bag == 0 and moves[1].bagSlot == 3 and moves[1].slot == 17)
            ItemRack_SwapPoison()
            assert(worn[17].enchant == 101)
            assert(bags[0][3].enchant == 202)
            assert(#moves == 2)
        """)

    def test_ambiguous_candidates_require_explicit_poison(self):
        lua = runtime()
        lua.execute("""
            bags[0][1] = {id = 777, enchant = 202}
            bags[1][2] = {id = 777, enchant = 303}
            ItemRack_SwapPoison()
            assert(#moves == 0 and #messages == 1)
            ItemRack_SwapPoison(17, 303)
            assert(#moves == 1 and moves[1].bag == 1 and moves[1].bagSlot == 2)
            assert(worn[17].enchant == 303)
        """)

    def test_refuses_missing_poison_and_active_set_swap(self):
        lua = runtime()
        lua.execute("""
            bags[0][1] = {id = 777, enchant = 202}
            swapActive = true
            ItemRack_SwapPoison()
            swapActive = false
            worn[17].enchant = nil
            ItemRack_SwapPoison()
            worn[17].enchant = 101
            bags[0][1].enchant = nil
            ItemRack_SwapPoison()
            assert(#moves == 0 and #messages == 3)
        """)

    def test_ignores_other_item_ids_and_same_poison(self):
        lua = runtime()
        lua.execute("""
            bags[0][1] = {id = 888, enchant = 202}
            bags[0][2] = {id = 777, enchant = 101}
            ItemRack_SwapPoison()
            assert(#moves == 0 and #messages == 1)
        """)


if __name__ == "__main__":
    unittest.main()

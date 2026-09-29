# ItemRack User Guide

Detailed configuration, equipment set management, and usage guide for **ItemRack**.

---

## 1. Creating and Managing Sets

### Saving a New Set
1. Open your Character Sheet (`C`).
2. Click the ItemRack minimap button or the Sets button on your ItemRack bar to open the Sets window.
3. Select which equipment slots to include in the set. Click individual slots to toggle whether they are part of the set (dimmed slots are ignored when equipping).
4. Enter a name, select an icon, and click **Save**.

### Setting Up the Equipment Bar
- **Adding / Removing Slots**: Hold `Alt` and Left-Click any equipment slot on your Character Sheet to add or remove that slot on the ItemRack bar.
- **Adding the Sets Button**: Hold `Alt` and Left-Click your character's 3D portrait model on the Character Sheet.
- **Moving the Bar**: Hold `Alt` and drag the bar to reposition it. Positions are saved per character.

### Flyout Menus
- **Hover Menus**: Moving your mouse over any slot on the ItemRack bar (or on the Character Sheet) displays a flyout showing all compatible items in your inventory.
- **Unequipping**: Click the `(empty)` slot option in a flyout menu to remove an item into your bags.

---

## 2. Combat Queue & Verified Swaps

- **Combat Restrictions**: In WoW 1.12.1, weapons and off-hands can be swapped during combat, but armor, rings, and trinkets cannot.
- **The Combat Queue**: Attempting to equip a set or armor piece during combat stages the items in ItemRack's combat queue. A small clock/gear indicator shows that items are queued. As soon as combat ends, ItemRack automatically equips the queued gear.
- **Transaction Safety**: ItemRack verifies that items are actually in place on your character before confirming a swap. If bags are full or an item is unavailable, the swap aborts cleanly without leaving your gear in a mismatched state.

---

## 3. Poison-Aware Weapon Swapping

Rogues often carry identical daggers or weapons with different active poisons (e.g. Wound Poison vs Crippling Poison). Standard macros cannot distinguish between two weapons with the same name. ItemRack solves this with `ItemRack_SwapPoison()`.

### Setup & Macro
Equip one poisoned weapon in your off-hand (slot 17) and keep an identical copy with a different poison anywhere in your bags. Create this macro:

```text
#showtooltip 17
/run ItemRack_SwapPoison()
```

- When activated, ItemRack inspects the active temporary enchants and equips the matching bagged copy into your off-hand. The previously worn weapon returns to your bag while retaining its poison.
- To swap main-hand weapons instead, use `/run ItemRack_SwapPoison(16)` with `#showtooltip 16`.
- If you carry multiple copies with different poisons, specify the target enchant ID explicitly: `/run ItemRack_SwapPoison(17, 323)`.

---

## 4. Automated Event Swapping

ItemRack can automatically equip sets when specific game events occur (mounting, swimming, entering combat, stance/shapeshift changes, or low mana):
- Open the ItemRack Sets window and select **Events**.
- Check the desired triggers and bind them to your saved sets.
- Built-in mount detection uses enhanced-client `IsMounted()` telemetry.
- For creating custom Lua event scripts, refer to the [Event Scripting Guide](EVENTS.md).

---

## 5. Integration with Bagnon and TrinketMenu

- **Bagnon**: If Bagnon is loaded, items stored in your bank belonging to an ItemRack set display a blue border in ItemRack menus. Item tooltips in Bagnon also display their ItemRack set membership (`ItemRack: <Set Names>`).
- **TrinketMenu**: If you use TrinketMenu for automated trinket management, you can exclude slots 13 and 14 from your ItemRack sets to allow TrinketMenu to manage trinkets independently.

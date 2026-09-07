# ItemRack Event Scripting Guide

ItemRack features a powerful event-driven scripting engine that allows you to automatically equip, save, or toggle gear sets in response to World of Warcraft engine events.

---

## 1. Overview & Setup

All event configuration is managed directly in-game:
1. Open the ItemRack configuration window (`/itemrack` or click the minimap icon).
2. Navigate to the **Events** tab.
3. Enable the master toggle: **"Enable Events"**.
4. In the event list, click the red question mark (`?`) next to an event to associate a gear set with that event trigger.
5. An event remains inactive until a set is linked to it.

To restore default events at any time without affecting custom events:
```text
/itemrack reset events
```
*(Default event definitions are maintained modularly in `Events.lua`)*

---

## 2. Event Structure

Clicking **New** or **Edit** in the Events tab opens the script editor with four configuration fields:

| Field | Description |
| :--- | :--- |
| **Name** | Display name in the event list. Prefix with `Class:` (e.g. `Warrior:Overpower`) to restrict visibility to that specific class unless "Show All" is checked. |
| **Trigger** | The game event that triggers the script (e.g. `UNIT_AURA`, `PLAYER_REGEN_DISABLED`). |
| **Delay** | Debounce delay in seconds. Setting `0` runs immediately on every event. Setting `> 0` debounces high-frequency events and runs once after activity settles. |
| **Script** | The Lua code to execute when the event triggers. |

---

## 3. Debounce Delay Mechanics

Many World of Warcraft events fire in rapid bursts (e.g. `BAG_UPDATE` or `UNIT_AURA` can fire dozens of times during zoning or buff application):
- **Delay = 0**: The script executes synchronously on every single event frame.
- **Delay > 0**: Debounces the trigger. The script only executes **once** after the specified time has elapsed since the last event occurrence.
  - Recommended for aura changes: `0.5` to `1.0` seconds.
  - Useful for temporary ability windows (e.g. Warrior Overpower: trigger on dodge with `Delay = 0` to equip, and another event with `Delay = 5` to unequip).

---

## 4. Scripting API & Helper Functions

ItemRack exposes dedicated helper functions for event scripts:

### Gear Set Operations
```lua
-- Associated Set Operations (operates on the set linked to the current event)
EquipSet()             -- Equips the associated set
SaveSet()              -- Records current gear in the associated set's slots
LoadSet()              -- Re-equips gear previously recorded by SaveSet()
ToggleSet()            -- Toggles between (SaveSet -> EquipSet) and LoadSet

-- Named Set Operations (targets a specific set by name)
EquipSet("setname")    -- Equips the set named "setname"
SaveSet("setname")     -- Records current gear for "setname"
LoadSet("setname")     -- Re-equips gear previously saved for "setname"
ToggleSet("setname")   -- Toggles "setname"
```

> **Note:** If another addon shadows these globals, use `ItemRack_EquipSet`, `ItemRack_SaveSet`, `ItemRack_LoadSet`, or `ItemRack_ToggleSet`.

### Engine & Form Helpers
```lua
-- Direct Mount Detection (Modernized via native IsMounted() and C_UnitAuras)
local mounted = ItemRack_PlayerMounted()

-- Current Stance / Shapeshift Form
local form = ItemRack_GetForm() -- Returns localized form: "Bear Form", "Battle Stance", etc.
```

### Custom Event Triggers
In addition to standard WoW client events, ItemRack dispatches internal events:
- **`ITEMRACK_NOTIFY`**: Fired when an item readiness notification occurs (`arg1` = item name).
- **`ITEMRACK_ITEMUSED`**: Fired when an item on the bar is activated (`arg1` = item name, `arg2` = slot ID).
- **`ITEMRACK_BUFFS_CHANGED`**: Fired when player buffs update (`arg1` = table indexed by buff texture and buff name).

### Tooltip Annotations
Include bracketed comments anywhere in your script to display helpful notes in the event's in-game tooltip:
```lua
--[[ Equips fire resistance gear when entering Molten Core ]]
```

---

## 5. Practical Script Examples

### Mount Swapping (Zero-Latency Engine Integration)
```lua
-- Trigger: UNIT_AURA | Delay: 0.1
if ItemRack_PlayerMounted() then
    EquipSet()
else
    LoadSet()
end
```

### Druid Shapeshifting (Stance Dancing)
```lua
-- Trigger: UPDATE_SHAPESHIFT_FORMS | Delay: 0
local form = ItemRack_GetForm()
if form == "Cat Form" then
    EquipSet("Cat")
elseif form == "Bear Form" or form == "Dire Bear Form" then
    EquipSet("Tank")
else
    LoadSet()
end
```

### Low Mana Rest / Drinking
```lua
-- Trigger: UNIT_AURA | Delay: 0.5
if UnitMana("player") / UnitManaMax("player") < 0.20 and not UnitAffectingCombat("player") then
    EquipSet("Spirit Regen")
else
    LoadSet()
end
```

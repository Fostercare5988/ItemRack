# ItemRack (Enhanced 1.12.1 Client)

[![Interface](https://img.shields.io/badge/Interface-1.12.1%20%28Build%205875%29-blue.svg)](https://github.com/Fostercare5988/ItemRack)
[![Version](https://img.shields.io/badge/Version-2.0.0-brightgreen.svg)](https://github.com/Fostercare5988/ItemRack)
[![Engine](https://img.shields.io/badge/Engine-ClassicAPI%20%7C%20SuperWoW-orange.svg)](https://github.com/Fostercare5988/ItemRack)
[![License](https://img.shields.io/badge/License-GPL--2.0-green.svg)](LICENSE)

**ItemRack** is an inventory management, item set, and quick-swapping addon engineered for the **World of Warcraft 1.12.1 Enhanced Client** (ClassicAPI v1.15.8+, SuperWoW v2.2+).

Originally created by Gello, with modern enhancements and maintenance by **[Fostercare5988](https://github.com/Fostercare5988)** (with contributions from McPewPew, Khalil, and the community).

---

## Features

- **Dynamic Equipment Bar:** Add, remove, and arrange gear slots and sets on a customizable HUD bar.
- **Context Menus:** Mouse over any equipped slot on the bar or character sheet to open a flyout menu showing all eligible items from your inventory.
- **Automated Event Triggers:** Automatically equip gear sets in response to in-game triggers (mounting, swimming, combat stance changes, shapeshifts, buffs, low mana, resting, etc.).
- **Mount and Buff Detection:** Uses `IsMounted()` for mount state and structured `C_UnitAuras` data for buff-triggered automation.
- **Goblin Brainwashing Device (GBD) Support:** Automatic specialization gear set swapping when interacting with the Goblin Brainwashing Device.
- **Combat Queue:** Queue non-swappable items (armor, rings, trinkets) during combat or death, then resume when equipment changes are allowed.
- **Verified Set Completion:** Equipment is checked against the requested state before the current set changes. Failed prerequisites abort, missed events are reconciled, and stalled swap stages time out.
- **Keybinding Support:** Bind individual gear sets or usable equipment slots to hotkeys.
- **Minimap Button & Profiles:** Clean minimap launcher with rotation, scaling, and character-specific profiles.

---

## System Requirements

- **Client Version:** World of Warcraft 1.12.1 (Build 5875)
- **Engine Extension Stack:**
  - **ClassicAPI:** `v1.15.8+` (structured aura and container APIs, `hooksecurefunc`, `table.wipe`, and enhanced Lua syntax)
  - **SuperWoW:** `v2.2+` (required by ItemRack's startup guard)

Bagnon and TrinketMenu integrations are optional; they are not required to use ItemRack. No additional DLL dependency is required for these integrations.

---

## Installation

1. Download or clone this repository.
2. Place the `ItemRack` folder into your `Interface\AddOns\` directory:
   ```
   World of Warcraft\Interface\AddOns\ItemRack\
   ```
3. Ensure both `ClassicAPI.dll` and `SuperWoW.dll` are active in your client.
4. Launch the client and enable **ItemRack** on the AddOn selection screen.

---

## Usage

- `/itemrack` — Toggle ItemRack bar visibility
- `/itemrack equip <setname>` — Equip a saved gear set
- `/itemrack toggle <setname>` — Toggle a gear set
- `/itemrack reset` — Reset bar position and settings
- `/itemrack reset events` — Restore default automated events from `Events.lua`
- `/itemrack reset everything` — Restore addon to default state

### Creating a Set
1. Open the Character Sheet (`C`).
2. Click the ItemRack minimap button or bar settings to open the Sets dialog.
3. Select which gear slots to include, choose a name and an icon, then click **Save**.

### Setting Up the Bar
- `Alt + Click` any slot on your character sheet to add or remove it from the bar.
- `Alt + Click` your 3D character model on the sheet to add the Sets button to the bar.
- `Alt + Drag` to move the bar when locked.

---

## Suite Synergy: The Inventory & Equipment Trio

ItemRack exposes integration points for **[Bagnon](https://github.com/Fostercare5988/Bagnon)** and **[TrinketMenu](https://github.com/Fostercare5988/TrinketMenu)**. Both addons are optional:

- **Bagnon Bank & Bag Coordination**:
  - **Bank Detection**: ItemRack uses native `BANKFRAME_OPENED` and `BANKFRAME_CLOSED` events to track access to bank items.
  - **Visual Bank Borders**: Items in your bank belonging to an ItemRack set or slot menu display a distinct **blue border** in ItemRack menus.
  - **Tooltip Set Indicators**: ItemRack exports `Rack.GetSetsWithItem(link)` so cooperating addons can query which saved sets contain an item.
  - **Inventory Refresh**: ItemRack responds to native inventory and bag events, including `BAG_UPDATE` and `PLAYERBANKSLOTS_CHANGED`.
- **TrinketMenu Cooperative Queueing**:
  - **Item-Use Hooks**: ItemRack uses ClassicAPI `hooksecurefunc` for `UseInventoryItem` and `UseAction` on the required enhanced client.
  - **Swap Activity**: `Rack.SetSwapping` exposes the active set transaction to cooperating addons.
  - **Wear Notification**: When the swap queue finishes or aborts, ItemRack calls `TrinketMenu.UpdateWornTrinkets()` if that callback is available.
  - **Trinket Slot Independence**: Exclude slots 13 and 14 when saving a set to leave those slots under separate management.

---

## Event Scripting

ItemRack includes a full event-driven scripting engine for automated gear swaps (mounting, shapeshifting, auras, low mana, combat stances).

Detailed scripting API documentation, debounce configuration, and examples are available in the **[Event Scripting Guide](EVENTS.md)**.

Delayed events retain their triggering payload and set association. Disabling an event, changing its association, or opening the settings window cancels pending work. Script errors are reported with the event name, and dispatch context is restored after execution.

The UI, automation, and bundled Rack equipment engine remain in `ItemRack.lua`. `Constants.lua` supplies text and bindings, `Events.lua` supplies default automation scripts, and XML defines the frames. Swap requests, weapon prerequisites, and combat/undo scratch requirements are runtime state; user settings, set definitions, and saved undo fields retain the existing SavedVariables format. Equipment events drive swap progress, with a one-second reconciliation check and a ten-second deadline for each stage.

---

## Changelog

### Version 2.0.0 (Comprehensive ItemRack Modernization)

- **Runtime Weapon Prerequisites**: Two-handed and off-hand preparation no longer rewrites saved set requirements. Replacement main-hand equipment is verified before a dependent off-hand move proceeds.
- **Clean Failure Handling**: Full bags, unavailable equipment, and failed prerequisite moves abort the transaction and release its queue, timer, and reservation state.
- **Authoritative Swap Verification**: Each stage checks actual equipped items and empty slots; an unrelated unlock event alone cannot advance a swap.
- **Reconciliation and Timeouts**: A periodic check reconciles missed or delayed equipment events. Stalled stages have an explicit ten-second timeout, leaving the addon able to accept another request.
- **Verified Current Set**: `CurrentSet` is published only after the complete requested equipment state is observed. Combat/death deferral and undo use the same completion rule.
- **Request Ownership**: Queued requests retain their snapshots. Duplicate lifecycle events, superseded requests, and late completion events cannot publish an older request as a newer one.
- **Deferred Work Cleanup**: Aborting or cancelling a request removes its owned deferred equipment without discarding unrelated manual queue entries.
- **Retryable Undo**: Undo history is committed after successful completion and retained when restoration fails. Retrying a failed undo does not depend on rebuilding lost history.
- **Runtime Scratch Requirements**: Combat and undo scratch sets stay in runtime tables. Existing SavedVariables declarations and saved-set requirements remain compatible.
- **Structured Aura Handling**: Buff automation enumerates structured aura slots, clears stale entries, and uses enhanced-client mount state directly.
- **Event Script Lifecycle**: Pending event payloads are released on cancellation; script failures are reported without leaking dispatch context into later events. Rebuilding a shorter event list clears stale entries.
- **Flyout and Bank Correctness**: Menu caches account for modifiers, menu origin, bank access, and relevant options. Bank transfers use and revalidate the selected item's actual location.
- **Dependency and Load-Graph Reconciliation**: The ClassicAPI minimum is now `v1.15.8+`, alongside SuperWoW `v2.2+` on WoW 1.12.1 Build 5875. The obsolete, unloaded `Bootstrap.lua` guard was removed, requirements were reconciled across the README and in-game help, and `Bindings.xml` retains its client-managed loading mechanism.
- **Validation Scope**: The release has 31 headless regression tests plus Lua/XML syntax, XML callback, manifest, and static checks. These use mocked client interfaces and do not establish in-game timing, compatibility with other addons, or measured performance; in-game verification remains required.

### Version 1.99.3 (Item Quality Borders)
- **Native Quality Borders**: Items in flyout menus (`ItemRackMenu` buttons) and on the main bar (`ItemRackInv` buttons) now display crisp `UI-Tooltip-Border` rarity borders — the same vibrant palette used in Bagnon:
  - Uncommon: Vibrant Emerald Green
  - Rare: Radiant Electric Sky Blue
  - Epic: Vivid Neon Purple
  - Legendary: Flaming Orange
- **No Additional Border Library**: Quality borders use native `SetBackdrop`; no additional library is required for this feature.
- **Lazy Frame Creation**: `qualityBorder` sub-frames are created on demand and reused.
- **Settings Toggle**: Added `QualityBorders` setting (ON by default) to the ItemRack settings scroll list to show or hide borders without a reload.
- **Rack.GetItemInfo Extension**: Now returns `itemQuality` as a 5th return value, with a dual-tier resolution fallback (`GetInventoryItemQuality` → `GetItemInfo` → `C_Container.GetContainerItemID`).

### Version 1.99.2 (Character Sheet Flyout Menus)
- **PaperDoll Equipment Flyouts**: Hovering over any worn or available equipment slot in the Character Sheet (`PaperDollFrame`) displays an instant flyout menu containing all eligible items in inventory plus an empty slot for unequipped items.
- **Side-by-Side Tooltip Layout**: Re-anchored item tooltips dynamically beside the flyout menu, preventing tooltip overlap and ensuring both worn item stats and flyout items remain fully visible.
- **Empty Slot Unequip**: Added an explicit `(empty)` slot with an informative "Unequip" tooltip, allowing instant 1-click gear removal into the best available bag slot.
- **Settings Toggle**: Added `CharSheetMenu` setting (toggleable in ItemRack settings) to easily enable or disable character sheet hover flyouts.

### Version 1.99.1 (Inventory Trio Synergy & Hook Modernization)
- **Non-Destructive Hooking Pipeline**: Replaced legacy global function overwrites (`UseInventoryItem = ...`, `UseAction = ...`) with native ClassicAPI `hooksecurefunc` and safe fallback.
- **Hardware-Accelerated Action Inspection**: Modernized `UseAction` monitoring to inspect `GetActionInfo(slot)` Item IDs directly, bypassing tooltip scanning.
- **Public Set Inspection API**: Added `Rack.GetSetsWithItem(itemIdentifier)` to query all active equipment sets containing an item (by link, ID, or name).
- **TrinketMenu Synchronization**: Calls `TrinketMenu.UpdateWornTrinkets()` when set swaps finish.
- **Safe Table Traversal**: Converted legacy bank slot iterators to standard Lua `ipairs(ItemRack.BankSlots)` loops.

### Version 1.99.0 (Modern Engine Stack)
- **High-Cohesion Modular Architecture**: Eradicated the legacy `localization.lua` misnomer. Decoupled UI strings and keybindings into `Constants.lua` and automated set triggers into `Events.lua`.
- **Module Initialization**: Initialized defensive tables (`ItemRack = ItemRack or {}`) across modules; the TOC loads data, runtime code, and then XML frames.
- **Direct Engine Mount Detection**: Replaced legacy tooltip-scanning hacks with native C++ `IsMounted()` and `C_UnitAuras`.
- **Lock-Sequenced Combat Queue**: Used `ITEM_LOCK_CHANGED` to advance post-combat equipment swaps. Result verification and stalled-stage timeouts are described in the v2.0.0 entry above.
- **Enhanced Lua Syntax**: Adopted the `#` length operator and `table.wipe` supplied by the enhanced client.
- **Library Purge**: Eradicated obsolete legacy Ace2, Dewdrop, and Tablet library dependencies (`ItemRackFu`).
- **In-Game Help Redesign**: Updated help documentation in the `[?]` tab with explicit engine prerequisites and author attribution.
- **Documentation Overhaul**: Modernized event scripting manual into standard Markdown (`EVENTS.md`) and eradicated legacy text files.

---

## Credits & License

- **Original Author**: Gello
- **Modernization & Maintenance**: [Fostercare5988](https://github.com/Fostercare5988)
- **Enhanced Client Contributors**: McPewPew, Khalil, Sleepybear
- **License**: GNU General Public License v2 (GPL-2.0)

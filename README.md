# ItemRack (Enhanced 1.12.1 Client)

[![Interface](https://img.shields.io/badge/Interface-1.12.1%20%28Build%205875%29-blue.svg)](https://github.com/Fostercare5988/ItemRack)
[![Version](https://img.shields.io/badge/Version-1.99-brightgreen.svg)](https://github.com/Fostercare5988/ItemRack)
[![Engine](https://img.shields.io/badge/Engine-ClassicAPI%20%7C%20SuperWoW%20%7C%20DXVK-orange.svg)](https://github.com/Fostercare5988/ItemRack)
[![License](https://img.shields.io/badge/License-GPL--2.0-green.svg)](LICENSE)

**ItemRack** is an inventory management, item set, and quick-swapping addon engineered for the **World of Warcraft 1.12.1 Enhanced Engine Stack** (ClassicAPI v1.14.0+, SuperWoW v2.2+, DXVK Vulkan runtime).

Originally created by Gello, with modern enhancements and maintenance by **[Fostercare5988](https://github.com/Fostercare5988)** (with contributions from McPewPew, Khalil, and the community).

---

## Features

- **Dynamic Equipment Bar:** Add, remove, and arrange gear slots and sets on a customizable HUD bar.
- **Context Menus:** Mouse over any equipped slot on the bar or character sheet to open a flyout menu showing all eligible items from your inventory.
- **Automated Event Triggers:** Automatically equip gear sets in response to in-game triggers (mounting, swimming, combat stance changes, shapeshifts, buffs, low mana, resting, etc.).
- **Direct Engine Mount Detection:** Built-in integration with native `IsMounted()` and `C_UnitAuras` for instantaneous mount set swapping with zero tooltip scraping or latency.
- **Goblin Brainwashing Device (GBD) Support:** Automatic specialization gear set swapping when interacting with the Goblin Brainwashing Device.
- **Combat Queue:** Queue non-swappable items (armor, rings, trinkets) while in combat; items swap automatically the moment combat ends.
- **Keybinding Support:** Bind individual gear sets or usable equipment slots to hotkeys.
- **Minimap Button & Profiles:** Clean minimap launcher with rotation, scaling, and character-specific profiles.

---

## System Requirements

- **Client Version:** World of Warcraft 1.12.1 (Build 5875)
- **Engine Extension Stack:**
  - **ClassicAPI:** `v1.14.0+` (C_UnitAuras, C_Timer, C++ memory management)
  - **SuperWoW:** `v2.2+` (GUID targeting and entity tracking)
  - **DXVK:** Direct3D 9 to Vulkan translation layer

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

## Banking Integration & Bagnon Compatibility

ItemRack operates with **zero coupling and 100% interoperability** alongside **[Bagnon](https://github.com/Fostercare5988/Bagnon)**:
- **Universal Bank Detection**: ItemRack listens directly to engine-level `BANKFRAME_OPENED` and `BANKFRAME_CLOSED` events rather than inspecting Blizzard's default UI frames. When Bagnon's unified bank window (`Banknon`) opens, ItemRack activates its banking mode automatically with zero frame conflict.
- **Visual Bank Borders**: Items in your bank that belong to a gear set or slot menu display a distinct **blue border** in ItemRack flyout menus.
- **Bi-Directional Transfer**: Selecting a banked item or set from an ItemRack menu pulls it into your bags (space permitting); selecting an unbanked item or set while at the bank pushes it into your bank bags.
- **Real-Time State Synchronization**: All equipment swaps and bank movements update Bagnon's unified bags and bank frames instantaneously via native `BAG_UPDATE` and `PLAYERBANKSLOTS_CHANGED` engine dispatches.

---

## Event Scripting

ItemRack includes a full event-driven scripting engine for automated gear swaps (mounting, shapeshifting, auras, low mana, combat stances).

Detailed scripting API documentation, debounce configuration, and examples are available in the **[Event Scripting Guide](EVENTS.md)**.

---

## Changelog

### Version 1.99.0 (Modern Engine Stack)
- **High-Cohesion Modular Architecture**: Eradicated the legacy `localization.lua` misnomer. Decoupled UI strings and keybindings into `Constants.lua` and automated set triggers into `Events.lua`.
- **Decoupled Load Order**: Initialized defensive tables (`ItemRack = ItemRack or {}`) across all modules, eliminating temporal load-order coupling in `ItemRack.toc`.
- **Direct Engine Mount Detection**: Replaced legacy tooltip-scanning hacks with native C++ `IsMounted()` and `C_UnitAuras`.
- **Lock-Sequenced Combat Queue**: Synchronized post-combat swaps to the `ITEM_LOCK_CHANGED` engine event with automatic timeouts, completely eliminating concurrent swap race conditions.
- **Modern Lua 5.1 Syntax**: Replaced all 27 instances of `table.getn(t)` with the native `#` bytecode operator and manual loop wipes with native C++ `table.wipe(t)`.
- **Library Purge**: Eradicated obsolete legacy Ace2, Dewdrop, and Tablet library dependencies (`ItemRackFu`).
- **In-Game Help Redesign**: Updated help documentation in the `[?]` tab with explicit engine prerequisites and author attribution.
- **Documentation Overhaul**: Modernized event scripting manual into standard Markdown (`EVENTS.md`) and eradicated legacy text files.

---

## Credits & License

- **Original Author**: Gello
- **Modernization & Maintenance**: [Fostercare5988](https://github.com/Fostercare5988)
- **Enhanced Client Contributors**: McPewPew, Khalil, Sleepybear
- **License**: GNU General Public License v2 (GPL-2.0)

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

## Credits & License

- **Original Author**: Gello
- **Modernization & Maintenance**: [Fostercare5988](https://github.com/Fostercare5988)
- **Enhanced Client Contributors**: McPewPew, Khalil, Sleepybear
- **License**: GNU General Public License v2 (GPL-2.0)

# ItemRack

An inventory management, equipment set, and quick-swapping add-on for World of Warcraft 1.12.1.

## Features

- **Equipment Bar & Flyouts**: Configurable on-screen HUD bar for your gear slots and sets. Hovering over any slot opens a flyout menu of all eligible inventory items.
- **Custom Equipment Sets**: Save complete or partial gear sets with custom names and icons; easily bind sets or individual slots to hotkeys.
- **Automated Event Triggers**: Automatically equip sets in response to gameplay events such as mounting, swimming, shapeshifting, combat stances, or low mana.
- **Combat Queue & Verified Swaps**: Queue non-swappable items (armor, rings, trinkets) during combat for automatic equipping upon combat exit. Gear changes are verified transactions that ensure items are confirmed worn before completing.
- **Poison-Aware Weapon Swapping**: Swap between identical weapons carrying different active poisons via macro without relying on fixed bag slots.
- **Suite Integration**: Cooperates cleanly with Bagnon (bank set indicators and tooltip set tags) and TrinketMenu (coordinated trinket queueing).

## Requirements

- **World of Warcraft 1.12.1** (Build 5875)
- [ClassicAPI v1.15.15+](https://github.com/brues-code/ClassicAPI) (`ClassicAPI.dll`)
- [SuperWoW v2.2+](https://github.com/balakethelock/SuperWoW) (`SuperWoWhook.dll` / `SuperWoWlauncher.exe`)

> Note: Completely restart the game client after installing or updating DLLs. `/reload` cannot reload DLLs.

## Installation

1. Copy or clone this repository into your WoW add-on directory:
   ```text
   World of Warcraft/Interface/AddOns/ItemRack/
   ```
2. Verify that `ItemRack.toc` is located directly at `Interface/AddOns/ItemRack/ItemRack.toc`.
3. Launch WoW using the SuperWoW launcher.
4. Ensure ItemRack is checked on the character selection AddOn screen.

## Useful Commands & Shortcuts

| Command | Description |
| :--- | :--- |
| `/itemrack` | Toggle ItemRack bar visibility |
| `/itemrack equip <setname>` | Equip a saved gear set |
| `/itemrack toggle <setname>` | Toggle a gear set on or off |
| `/itemrack reset` | Reset bar position and frame settings |
| `/itemrack reset events` | Restore default event scripts |
| `/itemrack reset everything` | Reset addon to fresh default state |

| Shortcut | Context | Action |
| :--- | :--- | :--- |
| `Alt` + `Click` Slot | Character Sheet | Add or remove an equipment slot on the bar |
| `Alt` + `Click` Model | Character Sheet | Add the Sets button to the bar |
| `Alt` + Drag | ItemRack Bar | Reposition the equipment bar |
| `Hover` over Slot | Bar or Character Sheet | Open inventory flyout menu |

## Limitations & Notes

- **Combat Restrictions**: Armor, rings, and trinkets cannot be swapped during combat. ItemRack places them into the combat queue and equips them immediately when combat ends.
- **Transaction Safety**: ItemRack treats gear changes as verified transactions. If bags are full or an item is unavailable, the swap aborts cleanly to prevent partial or mismatched sets.
- **Poison Swaps**: The `ItemRack_SwapPoison()` helper swaps identical weapons with distinct active temporary enchants. If multiple candidate weapons carry different poisons, specify the target enchant ID explicitly to prevent ambiguous choices.

---

For detailed set management, bar setup, and poison swap macros, see the [User Guide](docs/USER_GUIDE.md). Custom event scripting is documented in the [Event Scripting Guide](EVENTS.md), and technical architecture notes are available in [INTEGRATION_REVIEW_2026-09-29.md](INTEGRATION_REVIEW_2026-09-29.md).

## License & Credits

Original author: Gello. Maintained by [Fostercare5988](https://github.com/Fostercare5988). Enhanced client contributions by McPewPew, Khalil, Sleepybear. Licensed under GNU General Public License v2 (GPL-2.0).

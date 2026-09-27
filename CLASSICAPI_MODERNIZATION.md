# ItemRack ClassicAPI modernization review

## Task

- Type: modernization audit and bounded implementation.
- Objective: replace custom work where the installed enhanced client supplies a verified equivalent, retaining ItemRack's set-selection and completion rules.
- Starting ItemRack revision: 3d8e940dd59efd7ef130f4acc8d1453c32eb47ef.
- Target: WoW 1.12.1 Build 5875 / Interface 11200, server-agnostic enhanced client.
- Framework contract and selective ClassicAPI reference, workflow, task/review/retrospective templates consulted.
- Existing aura, set transaction, combat/death, undo, bank/menu and poison-swap tests reused.
- Scope: ItemRack runtime, bundled scripts, TOC/XML wiring, affected docs and tests.
- Out of scope: other addons, framework changes, importing native equipment sets, changes to user set format, DLL installation, version/release changes.
- Git authorization for this task: no commit or push requested.
- Stop condition: implementation, headless validation and complete diff reconciled; client testing remains explicitly pending.

## Verified replacements

Evidence here is [SOURCE-VERIFIED]. Headless tests exercise addon behavior using mocks; they are not [EMPIRICALLY VERIFIED] evidence from Niko's client.

Official API reference: [ClassicAPI v1.15.15 docs/API.md](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/docs/API.md).
The APIs used were also checked against the official v1.15.14 reference; its existing enforced minimum covers all replacements. v1.15.15 remains recommended.

| Former ItemRack work | Replacement / resulting behavior |
|---|---|
| Equipped/bag weapon enchant scans, English icon-name matching and global GetWeaponEnchantInfo format guessing | C_Item.GetItemTempEnchantInfo for the exact item location; GetEnchantInfo and C_Spell.GetSpellTexture for a supported spell icon. Equipped and bag overlays share one duration/charge formatter. |
| Red-tooltip-text equip eligibility | C_PlayerInfo.CanUseItem, retaining the separate offhand eligibility gate. This checks actual proficiency, level, class/race, skill/spell, honor and reputation requirements; on-use spell usability is a different question. |
| Soulbound tooltip strings | C_Item.IsBound plus static bindType/flags for the existing quest/conjured exceptions. Static item flags and per-instance binding flags are distinct. |
| Name extraction from container links / used-item notification links | C_Item.GetItemName at the actual item location, including random suffixes. |
| Action identity by rendered tooltip title | GetActionInfo and GetInventoryItemID; unresolved bag-item/macro actions use GameTooltip:GetItem's structured itemID after SetAction. Spell and equipmentset actions are excluded. |
| Compact tooltip line scanning | Structured tooltip identity, equipped/container durability and native cooldown readers; ItemRack formats the compact display. |
| Bag-to-equipment and equipment-to-equipment pickup pairs | Explicit-slot C_Item.EquipItemByName with exact locations for supported slots 1..19; selected copy is retained. Queue completion still depends on observed equipment. |
| Bag/bank pickup pairs | C_Container.SwapItems for the selected source/destination. Send is not proof of server acceptance. |
| Item-data availability used as free-space check | HasContainerItem tests actual occupancy, including uncached occupied items. |
| Positive-interval per-frame timer loop | C_Timer.NewTimer callbacks with cancellation and generation ownership; callback errors are reported. A repeating interval starts from the last callback, preserving no-catch-up behavior. |
| Delayed event-script per-frame polling | One cancellable timer per delayed event; payload and set association retained. Old callbacks cannot consume a newer event's state. |
| Multiple mount API fallbacks and breath-bar UI inspection | IsMounted directly; Swimming responds to the BREATH mirror-timer payload. Only unchanged default scripts are migrated. |
| Global use-function fallback overwrites, dead mount dictionary and unused pair-swap helper | Removed. hooksecurefunc is required by the enhanced client. |

### Source details that affect decisions

- [Equipment.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/item/Equipment.cpp): even explicit-slot equip clears preexisting cursor state before resolving the source. ItemRack therefore waits for an empty GetCursorInfo result and checks between moves. It only clears residual cursors from its own remaining pickup pairs. The poison helper also refuses a busy cursor or spell targeting.
- [SwapItems.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/container/SwapItems.cpp): atomic bag-slot primitive; return true means the request was sent.
- [WeaponEnchant.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/item/WeaponEnchant.cpp) and [EnchantInfo.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/item/EnchantInfo.cpp): per-instance temporary enchant state; spellID exists only for applicable enchant effects. Enchants without a usable spell texture show a neutral question mark rather than a guessed poison icon. The stock global GetWeaponEnchantInfo is not the namespaced extended API.
- [CanUseItem.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/player/CanUseItem.cpp) and [Bound.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/item/Bound.cpp): equip/use requirements and instance soulbound bit.
- [HasItem.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/container/HasItem.cpp): occupancy does not depend on item-cache contents.
- [Tooltip.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/item/Tooltip.cpp) and [action/Info.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/action/Info.cpp): GetItem provides itemID; GetActionInfo can identify a bag item without supplying an itemID. A tooltip identity reader is therefore still useful for that unresolved action.
- [Timer.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/time/Timer.cpp): cancellable handles, no callback arguments, reentrant scheduling, callback references released after cancellation. The native dispatcher swallows callback errors; ItemRack reports its timer errors itself.
- [ItemPrototype.h](https://github.com/cmangos/mangos-classic/blob/master/src/game/Entities/ItemPrototype.h): the classic static CONJURED flag is 0x2; quest bindType is 4. These preserve existing filter exceptions rather than introducing another dependency.

## Deliberately retained code

- ItemRack set storage, exact enchant/suffix identifiers, snapshots, undo, event associations, combat/death deferral, weapon prerequisites and authoritative completion. C_EquipmentSet manages a different native-set store and does not replace these policies wholesale.
- Native pickup for unequip into a chosen bag and ammo slot 0. Explicit ClassicAPI equip supports destination slots 1..19; no verified public equivalent was found for these remaining moves.
- Per-frame minimap dragging; it is visual cursor-following work, not a delay scheduler.
- Native GetItemInfo/cooldown/FrameXML primitives where already appropriate. Namespace renaming alone would not improve behavior.
- UI click interception for Alt-click behavior and Goblin Brainwashing Device selection rules. These are addon behavior, not item-state polyfills.
- The default Skinning script's insufficient-skill tooltip cue. No verified ClassicAPI API exposes that complete condition. Replacing it with merely a dead/skinnable-unit flag would change when the equipment set is used.
- Existing custom scripts, including user-supplied API fallbacks. Migration matches the exact former bundled script, trigger and delay; it does not rewrite arbitrary saved Lua.

## Integration review

- Correctness: direct moves use exact locations; rejected/partial set requests cannot claim completion. Equip eligibility now uses the player's actual requirements. Existing queue-abort notification test was failing at HEAD; TrinketMenu is refreshed after owned swap state is fully cleared.
- Ownership: cancelled/restarted timer generations, delayed-event handles, payload cleanup, reentrant scripts and foreign cursors tested. Existing supersession/late-event/undo tests retained.
- Persistence: TOC SavedVariables unchanged. Timer handles and scratch requests are runtime-only. Exact-match standard-script upgrades preserve edits and associations.
- Load graph: removed mountGUID.lua and its TOC entry; removed obsolete optional IsMounted addon metadata; removed RegisterFrame OnUpdate XML binding. Root Bindings.xml remains client-managed.
- Dependencies: existing ClassicAPI v1.15.14 and SuperWoW v2.2 guards retained; v1.15.15 recommended. No DLL added.
- Performance: obsolete polling and tooltip parsing removed; no measured CPU/FPS claim.
- Files: ItemRack.lua, Events.lua, PoisonSwap.lua, Constants.lua, ItemRack.toc, ItemRackSets.xml, README.md, EVENTS.md, this review, and two test files changed; mountGUID.lua deleted. No other addon or VanillaForge implementation changed.
- Result: static/headless review passed; client behavior remains pending verification.

## Validation

- Full regression suite: 45 tests passed (including Lua/XML compilation, XML handlers, bundled-script syntax and TOC paths).
- Poison-swap suite: 5 tests passed.
- VanillaForge linter: 0 errors, 0 warnings.
- Former HEAD Mount, Mount(Not ZG/AQ) and Swimming scripts independently loaded and checked against the migration; all three upgraded exactly.
- Existing capability floor checked for all 16 newly consumed/modernized API contracts.
- Complete cumulative diff, whitespace checks, SavedVariables, TOC and repository status reviewed.
- All tests use a Lua 5.1 harness with only the legacy Lua 5.0 table iteration syntax adapted. They do not emulate the native DLL or server.

## Client verification [UNVERIFIED - TEST FIRST]

1. Fully restart after changing the DLL; test with ClassicAPI v1.15.15 and /luaerrors 1.
2. Swap rings/trinkets and similarly named weapons with different enchants/suffixes. Check the exact intended item, undo, current-set publication and timeout recovery.
3. Test 2H/offhand transitions, full bags, armor deferral in combat/death, and ammo slot 0.
4. Check enchant badges on the bar, character sheet and weapon menu: both hands, poisons, oils/stones, low charges, expiry, bag sorting and a non-English client. A non-spell enchant may intentionally use the question mark.
5. Test bank-to-bag and bag-to-bank moves from each bank container; confirm rejection does not look like a successful completed move.
6. Hold an item/spell/money/native-set cursor while requesting a set or poison swap. The cursor must remain yours.
7. Check item actions, item macros, normal spell actions, native equipment-set buttons and TrinketMenu coexistence/readiness notifications.
8. Check compact tooltips on worn/bag/bank gear, including broken items, cooldowns, and uncached item data.
9. Test mount/dismount and breath timer with replaced UI bars. Check custom scripts/delays/associations after /reload.
10. Test delayed scripts, menu hide, scaling, minimap dragging and cooldown overlays after /reload. No gameplay timing or visual claim is considered empirically verified until these tests pass.

## Retrospective

- Sources needed: selective ClassicAPI item/container/timer/action contracts, pinned implementations and the classic static item flag definition.
- Useful checks: running the baseline first exposed the existing TrinketMenu shutdown defect; the old queue and ownership tests remained useful across native API replacement.
- Rework: precise durability signature was corrected during source review; source verification also prevented falsely assuming explicit equip preserves a busy cursor.
- Exploration cost: reading unrelated whole source files was unnecessary; future reviews should retrieve the relevant function and its contract first.
- Framework lesson gate: cursor/async ownership and capability-specific floors are already covered by VanillaForge. No new Known Pattern or framework change is required.

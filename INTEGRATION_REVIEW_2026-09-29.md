# ItemRack integration review — 2026-09-29

Task: audit, bounded implementation, final integration review. Actual baseline
`bcbc6b88586c5fbfdc00b509916130513a12088f` was clean and matched remote main.
Reused `CLASSICAPI_MODERNIZATION.md`, existing transaction/poison tests and pinned
native source. The later Dissolvent/Corrosive icon customization is intentional
presentation and is preserved, including its regression test.

## Architecture

TOC: Constants, bundled Events, ItemRack runtime, PoisonSwap helper, main XML,
set/event/options XML. Four Lua and two XML files; root Bindings.xml is managed
by the client. SavedVariables are `ItemRack_Users`, `ItemRack_Settings`,
`ItemRack_Events`, `Rack_User`. Set format, custom scripts, defaults migration,
undo policy and the account/character division remain unchanged. Queue entries,
source/destination reservations and timers are runtime state.

The main runtime owns equipment bar/flyout/character hooks, settings and set UI;
Rack owns set snapshots, staged swaps, deferred combat/death work, verification
and bank commands. PoisonSwap separately selects an unambiguous exact location
by item and temporary-enchant ID. Native item/cooldown and bag/bank events trigger
refresh. Named cancellable timers own delays/periodic jobs; minimap dragging
retains its visual OnUpdate. Aura-driven event scripts consume structured data.

ClassicAPI supplies C_Item, C_Container, C_PlayerInfo eligibility, C_Spell icons,
C_UnitAuras, C_Timer, action identity and hooks. Existing SuperWoW guard remains;
no new NamPower/UnitXP/DXVK requirement. Optional Bagnon/ButtonHole/TrinketMenu
integration remains. Minimum ClassicAPI 1.15.15 is unchanged. Native equipment
sets still do not replace ItemRack's set storage, undo or completion semantics.

## Findings and fixes

Locations refer to the baseline. All are [SOURCE-VERIFIED], with Lua mock
reproduction. No gameplay result is labeled empirically verified.

| Priority | Location | Reproduction / consequence | Correction |
| --- | --- | --- | --- |
| P1 | `ItemRack.lua:5713,5755` | Bank search for `123:0:0` also matches `1123:0:0` or `123:0:01`. Push can accept the general lookup's same-name fallback despite a different saved enchant/suffix identity. Wrong gear can move. | Compare full stored item identity in bank lookup and revalidate push results before any move. |
| P2 | `ItemRack.lua:5731,5755` | Two set slots require identical copies; native requests are asynchronous, so the first source can be selected twice before bag state changes. | Reserve each source as well as the existing destination reservation; later entries select a different available copy. Stop on rejected native sends. |
| P2 | `ItemRack.lua:1592,2163,5724,5747` | A late bank-slot event reasserts BankIsOpen. Bank commands can clear reservations belonging to an active equipment swap, or continue after bank closure/cursor change. | Only BANKFRAME_OPENED establishes bank ownership. Slot events refresh only while open. Check bank/transaction/cursor state before clearing reservations and between set transfers; flyout transfers respect active swaps. |
| P2 | `ItemRack.lua:4385,4448,5629` | Signed random-suffix/unique fields fail unsigned link patterns and disappear from set/bank identity. | Preserve signed fields; bank indexing uses the same item reader. Existing saved identity remains item/enchant/suffix, without adding persistent GUIDs. |
| P2 | `ItemRack.lua:1408` | Old/manual MainScale/XPos/YPos strings, invalid scale or nonfinite values reach native setters. | Normalize these three values once during data initialization; preserve valid scales/coordinates and other user choices. |

The current custom enchant icons are not removed merely because metadata APIs
exist. Their availability rules still come from exact temporary-enchant state;
the custom label/icon override is an accepted display choice.

## Native contract recheck

Pinned ClassicAPI `71805db62f1e8a154477033dc1f50960c535af8b`:
[SwapItems.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/container/SwapItems.cpp)
returns true when a request is sent, not when the server completes it.
[Swap.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/item/Swap.cpp)
encodes the source GUID and bag/slot pair; the addon must still choose the correct
source. Existing
[Equipment.cpp](https://github.com/brues-code/ClassicAPI/blob/71805db62f1e8a154477033dc1f50960c535af8b/src/item/Equipment.cpp)
cursor-clearing and slot limits remain covered by the retained suite. No unverified
transaction replacement or new API was introduced.

## Integration and validation

- Correctness/ownership: PASS for the covered addon flows. Explicit bank lifetime,
  exact stored identity, source reservations and current native-send result are
  checked. Set completion/undo still depends on actual observed equipment.
- APIs/dependencies: PASS; unchanged providers and floor, verified native calls.
- Persistence: PASS; three numeric fields normalize; set/event format and custom
  scripts remain. No source reservation or handle enters SavedVariables.
- Hot paths/UI: PASS by inspection; no new polling or cadence. Ordinary display,
  reset preserving bar contents, structured enchant redraw and custom icons are
  covered. No measured performance claim.
- 61 tests pass: 46 existing regression tests, five poison tests, ten new bank/UI
  tests. All ten new cases fail behavior assertions on the starting commit.
  The existing flyout test also now checks active-swap exclusion.
- Four Lua files compile; six TOC/XML entries resolve, no orphan Lua. The suite
  also checks XML handlers, bindings and bundled event-script syntax.
- Strict VanillaForge lint: zero errors/advisories. Complete diff and whitespace
  check pass. Runtime implementation change is confined to ItemRack.lua.

READY for publication of these bounded fixes. Mocks adapt legacy Lua 5.0 table
iteration for Lua 5.1; they do not simulate native packet acceptance or rendering.

## In-game acceptance — pending

1. Back up SavedVariables while logged out. Try an old malformed MainScale value,
   open bar/flyout/options, reset the bar, drag/scale, reload and verify set/bar
   contents and valid positions survive. Recheck native cooldown/enchant redraw.
2. Bank items with overlapping numeric IDs or names and different enchant/suffix
   identities. Pull/push the set and inspect exactly which copies moved.
3. Transfer two identical rings/weapons required by two slots with a delayed
   server response. Verify two distinct sources and destinations, full-bag
   behavior, rejected moves, rapid repeated clicks, and close bank during a move.
4. Request a set while holding each supported cursor kind, in combat/death, or
   during a pending swap. Bank/flyout operations must not clear its ownership.
   Retest 2H/offhand prerequisites, undo, supersession and timeout recovery.
5. Verify signed-suffix gear remains selectable/indexed after reload. Late
   bank-slot events after bank closure must not enable transfers.
6. Retest Dissolvent/Corrosive icons, ordinary poisons/oils, expiry/charges, exact
   poison swaps, native equipment-set actions and TrinketMenu coordination.

[UNVERIFIED - TEST FIRST] Rapid repeated bank commands and concurrent external
inventory operations still need real-client packet/event testing. This patch
does not introduce an asynchronous bank-completion/rollback engine or claim
server confirmation from a successful send.

## Retrospective

The earlier equipment audit remained useful; bank batch selection was less
covered than the staged equip queue. Boundary tests exposed substring identity,
reused asynchronous sources and bank lifetime independently. Existing framework
identity/ownership principles already cover the lesson, so no framework edit is
proposed. Keep custom presentation choices separate from authoritative state.

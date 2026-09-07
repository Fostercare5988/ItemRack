--[[ Constants.lua - UI copy, text definitions, and static assets for ItemRack ]]

ItemRack = ItemRack or {}
ItemRackText = ItemRackText or {}

-- These three strings are the only ones required for the mod to work in other languages.  The rest are translations of benign text.
-- The above is no longer true, due to the addition of the Goglin Brainwashing Device 
ItemRackText.INVTYPE_CONTAINER = "Bag"
ItemRackText.MOUNTCHECK = "^Increases speed" -- used only for checking if a mount buff is a real one
ItemRackText.MOUNTCHECK2 = "^Speed scales with your Riding skill%.$"
ItemRackText.MOUNTCHECK3 = "^Slow and steady%.%.%.$"

--Goblin Brainwashing Device (GBD) integration
ItemRackText.GBD = "Goblin Brainwashing Device"

--ignore "Save..." lines
ItemRackText.GBDSave = "Save"

--spec number pattern "Activate ..." line
ItemRackText.GBDSpec = "Activate (%d).. Specialization"

--currently unused
--spec name pattern (GNS)
--example: "Activate HolyProclaim (16/35/0)"
--ItemRackText.GNS = "^Activate%s*(.+) %([%d/]+%)$"


--[[ Key bindings ]]--

-- Bindings are created dynamically in the mod and are stored per-character with the binding attached to the set.
-- To add more bindings, change .MaxKeyBindings to the desired amount and add more _EQUIPSET here and in Bindings.xml
-- The key bindings is arguably the most complex part of the mod -- localize with care or hold off localizing until last
ItemRackText.BINDINGFORMAT = "Equip Set: %s"
ItemRackText.BINDINGSEARCH = "Equip Set: (.+)"
ItemRackText.MaxKeyBindings = 10
BINDING_HEADER_ItemRack = "ItemRack"
BINDING_NAME_EQUIPSET1 = "Equip Set: 1" -- these values change to string.format of BINDINGFORMAT on the binding owner's set
BINDING_NAME_EQUIPSET2 = "Equip Set: 2"
BINDING_NAME_EQUIPSET3 = "Equip Set: 3"
BINDING_NAME_EQUIPSET4 = "Equip Set: 4"
BINDING_NAME_EQUIPSET5 = "Equip Set: 5"
BINDING_NAME_EQUIPSET6 = "Equip Set: 6"
BINDING_NAME_EQUIPSET7 = "Equip Set: 7"
BINDING_NAME_EQUIPSET8 = "Equip Set: 8"
BINDING_NAME_EQUIPSET9 = "Equip Set: 9"
BINDING_NAME_EQUIPSET10 = "Equip Set: 10"

-- options text. none of the text below will affect how the mod runs.  It's just displayed text.

ItemRackText.CONTROL_ROTATE_TEXT = "Rotate"
ItemRackText.CONTROL_ROTATE_tooltip	= "Change the orientation of the bar between vertical or horizontal."
ItemRackText.CONTROL_LOCK_TEXT = "Lock"
ItemRackText.CONTROL_LOCK_TOOLTIP = "Lock or unlock the window.  While locked, hold ALT and move the mouse over the bar to access controls."
ItemRackText.CONTROL_OPTIONS_TEXT = "Settings"
ItemRackText.CONTROL_OPTIONS_TOOLTIP = "Change ItemRack settings."
ItemRackText.OPT_TOOLTIPFOLLOW_TEXT = "Tooltips at pointer"
ItemRackText.OPT_TOOLTIPFOLLOW_TOOLTIP = "Check this to make tooltips follow the pointer instead of displaying at the default location."
ItemRackText.OPT_COOLDOWNNUMBERS_TEXT = "Cooldown numbers"
ItemRackText.OPT_COOLDOWNNUMBERS_TOOLTIP = "Check this to display the numerical time left in an item's cooldown."
ItemRackText.OPT_SOULBOUND_TEXT = "Hide tradables"
ItemRackText.OPT_SOULBOUND_TOOLTIP = "Check this to only display soulbound, quest or conjured items in the menus.  Bind-On-Equip and tradable items will be ignored to prevent showing up as you loot through an instance."
ItemRackText.OPT_BINDINGS_TEXT = "Show key bindings"
ItemRackText.OPT_BINDINGS_TOOLTIP = "Check this to display any key bindings on the bar."
ItemRackText.OPT_MENUSHIFT_TEXT = "Menu on Shift only"
ItemRackText.OPT_MENUSHIFT_TOOLTIP = "Check this to prevent the menu from appearing unless you're holding the Shift key."
ItemRackText.OPT_CLOSE_TEXT = "Close Options"
ItemRackText.OPT_CLOSE_TOOLTIP = "Exit options.  To close ItemRack completely, remove all items from the bar or /itemrack."
ItemRackText.INVFRAME_RESIZE_TEXT = "Resize"
ItemRackText.INVFRAME_RESIZE_TOOLTIP = "Drag the 'grip' in the lower right corner to resize the window."
ItemRackText.OPT_SHOWEMPTY_TEXT = "Allow empty slots"
ItemRackText.OPT_SHOWEMPTY_TOOLTIP = "Check this to add empty slots to the swap menu.  Items will be dropped in the left-most available bag slot, if one exists.  You cannot queue empty slots.  Trinkets will not show empty slots if TrinketMenu Clicks is enabled."
ItemRackText.OPT_FLIPMENU_TEXT = "Flip menu"
ItemRackText.OPT_FLIPMENU_TOOLTIP = "The menu grows towards the middle of the screen by default.  Check this to make the menu grow from the opposite side that it automatically chooses."
ItemRackText.OPT_RIGHTCLICK_TEXT = "TrinketMenu mode"
ItemRackText.OPT_RIGHTCLICK_TOOLTIP = "Check this to make left-clicking a trinket go to the top trinket slot (as displayed on your character screen), and right-click to go to the bottom trinket slot.  Trinket pairs on the bar together will share one menu as well."
ItemRackText.OPT_TINYTOOLTIP_TEXT = "Use tiny tooltips"
ItemRackText.OPT_TINYTOOLTIP_TOOLTIP = "Check this to make item tooltips only show name, durability and cooldown."
ItemRackText.OPT_SHOWTOOLTIPS_TEXT = "Show tooltips"
ItemRackText.OPT_SHOWTOOLTIPS_TOOLTIP = "Check this to show tooltips."
ItemRackText.OPT_NOTIFY_TEXT = "Notify when ready"
ItemRackText.OPT_NOTIFY_TOOLTIP = "Check this to display a message when a used item has finished cooldown."
ItemRackText.OPT_ROTATEMENU_TEXT = "Rotate menu"
ItemRackText.OPT_ROTATEMENU_TOOLTIP = "The menu grows perpendicular to the bar by default.  Check this to make it grow parallel to the bar."
ItemRackText.OPT_SHOWICON_TEXT = "Minimap button"
ItemRackText.OPT_SHOWICON_TOOLTIP = "Check this to display a button around the edge of the minimap to access options and sets."
ItemRackText.OPT_DISABLETOGGLE_TEXT = "Minimap sets menu"
ItemRackText.OPT_DISABLETOGGLE_TOOLTIP = "Check this to toggle the set menu on left click.  Uncheck to toggle the bar on left click."
ItemRackText.OPT_FLIPBAR_TEXT = "Flip bar growth"
ItemRackText.OPT_FLIPBAR_TOOLTIP = "The bar grows down or to the right by default.  Check this to make it grow leftwards or upwards."
ItemRackText.OPT_ENABLEEVENTS_TEXT = "Enable Events"
ItemRackText.OPT_ENABLEEVENTS_TOOLTIP = "Check this to allow automated events enabled below to swap gear based on conditions defined within the events.\n\nUncheck to stop all event processing."
ItemRackText.OPT_SHOWALLEVENTS_TEXT = "Show All"
ItemRackText.OPT_SHOWALLEVENTS_TOOLTIP = "Check this to show all events for all classes.\n\nUncheck to prevent sets for other classes from listing."
ItemRackText.OPT_COMPACTLIST_TEXT = "Compact"
ItemRackText.OPT_COMPACTLIST_TOOLTIP = "Check this to list sets in a more compact form to see more at once."
ItemRackText.OPT_SAVEDSETSCLOSE_TEXT = "Cancel"
ItemRackText.OPT_SAVEDSETSCLOSE_TOOLTIP = "Cancel choosing a set."
ItemRackText.OPT_NOTIFYTHIRTY_TEXT = "Notify at 30 secs"
ItemRackText.OPT_NOTIFYTHIRTY_TOOLTIP = "Check this to notify at the 30-second mark instead of when an item's cooldown ends."
ItemRackText.OPT_ALLOWHIDDEN_TEXT = "Allow hidden items"
ItemRackText.OPT_ALLOWHIDDEN_TOOLTIP = "Check this to allow menu items to be hidden with ALT+click.  To recover a hidden item on the menu, hold ALT as you enter the bar and ALT+click the item again."
ItemRackText.OPT_LARGEFONT_TEXT = "Large Font"
ItemRackText.OPT_LARGEFONT_TOOLTIP = "Check this to use a bigger font in the script edit window below."
ItemRackText.OPT_SQUAREMINIMAP_TEXT = "Square minimap"
ItemRackText.OPT_SQUAREMINIMAP_TOOLTIP = "Check this to have the minimap button drag around the full square of the minimap."
ItemRackText.OPT_BIGCOOLDOWN_TEXT = "Large cooldown"
ItemRackText.OPT_BIGCOOLDOWN_TOOLTIP = "Check this to make cooldown numbers bigger, resembling Cooldown Count."
ItemRackText.OPT_SETLABELS_TEXT = "Show set icon labels"
ItemRackText.OPT_SETLABELS_TOOLTIP = "Check this to show set labels on set icons."
ItemRackText.OPT_AUTOTOGGLE_TEXT = "Auto toggle sets"
ItemRackText.OPT_AUTOTOGGLE_TOOLTIP = "Check this to make chosing a set always toggle it: If equipped it will revert to gear it replaced. If unequipped it will equip the set.\nThis is the same as choosing a set while Shift is held.\nNote: This behavior does not happen while in combat or dead, since it can't be sure what you're going to wear in the future."

ItemRackText.SETS_CLOSE_TEXT = "Close Set Builder"
ItemRackText.SETS_CLOSE_TOOLTIP = "Exit Set Builder.  To close ItemRack completely, remove all items from the bar or /itemrack."
ItemRackText.SETS_NAMELABEL_TEXT = "Choose a name and icon:"
ItemRackText.SETS_HIDESET_TEXT = "Hide"
ItemRackText.SETS_HIDESET_TOOLTIP = "When checked, this set will not appear in the popup menu on the rack.  Note: The set icon on the rack will always reflect the last set equipped, hidden or not.\n\nHold ALT while you mouseover sets on the bar to see hidden sets.  You can ALT+click sets in the menu to toggle their hidden status."
ItemRackText.SETS_BINDBUTTON_TEXT = "Bind Key"
ItemRackText.SETS_BINDBUTTON_TOOLTIP = "Bind a key to this set."
ItemRackText.SETS_SAVEBUTTON_TEXT = "Save"
ItemRackText.SETS_SAVEBUTTON_TOOLTIP = "Save this set as the name given above.  Except for key bindings, changes made to an existing set are not permanent until you save."
ItemRackText.SETS_REMOVEBUTTON_TEXT = "Remove"
ItemRackText.SETS_REMOVEBUTTON_TOOLTIP = "Remove this set definition.  To keep a set but prevent it from showing on the menu, check Hide below the set's icon and then save."
ItemRackText.SETS_LOADBUTTON_TEXT = "Equip"
ItemRackText.SETS_LOADBUTTON_TOOLTIP = "Equip the selected set."

ItemRackText.READY = "%s ready!"
ItemRackText.READYTHIRTY = "%s ready soon!"
ItemRackText.QUEUED = "Queued: %s"
ItemRackText.SAVED = "Set %s saved with %d items."
ItemRackText.BINDCLEAR = "Binding cleared for this set."
ItemRackText.BINDSET = "Set bound to key %s"

ItemRackText.ERROR_MISSING = "ItemRack: Some items were not found: "
ItemRackText.ERROR_NOROOM = "ItemRack: Not enough free bag space to complete swap."

ItemRackText.COUNTFORMAT = "%s slots"
ItemRackText.NOSAVEDSETS = "No saved sets."
ItemRackText.SETTOOLTIPFORMAT = "Set: %s"
ItemRackText.SETREMOVE = "Set %s removed."
ItemRackText.EMPTYSET = ""
ItemRackText.SETTOOLTIPCOUNT = "%s items"
ItemRackText.SETTOOLTIPMISSING = "%s missing"
ItemRackText.EVENTSSUSPENDED = "Note: Event processing is suspended\nwhile this window is up."

ItemRackText.UNDEFINEDEVENT_TEXT = "Not Defined Yet"
ItemRackText.UNDEFINEDEVENT_TOOLTIP = "Click here to associate a set with this event.  You can edit the event to use multiple sets per event, but all events must have one set associated with it before it can be used."
ItemRackText.ENABLEEVENT_TEXT = "Enable Event"
ItemRackText.ENABLEEVENT_TOOLTIP = "Check this to enable this particular event.  Uncheck to disable the event.  Use the 'Enable' checkbox at the top as a master on/off for events."

ItemRackText.EVENTSDELETE_TEXT = "Delete Event"
ItemRackText.EVENTSDELETE_TOOLTIP = "Delete this event.  If any other characters on this account use this event, it will revert to an undefined state for this character."
ItemRackText.EVENTSEDIT_TEXT = "Edit Event"
ItemRackText.EVENTSEDIT_TOOLTIP = "Edit this event.\n\nSome knowledge of lua or WoW macros helps immensely in dealing with events.\n\nYou cannot associate a set with this event by editing it.  Click the set icon in the list above to associate a set."
ItemRackText.EVENTSNEW_TEXT = "New Event"
ItemRackText.EVENTSNEW_TOOLTIP = "Create a new event.\n\nSome knowledge of lua or WoW macros helps immensely in dealing with events."

ItemRackText.EVENTSSAVE_TEXT = "Save Event"
ItemRackText.EVENTSSAVE_TOOLTIP = "Save this event.  You can save unfinished events, just be sure not to associate them with any set until it's ready.\n\nIf the name of an existing event is changed, a COPY is made under the new name."
ItemRackText.EVENTSTEST_TEXT = "Test Script"
ItemRackText.EVENTSTEST_TOOLTIP = "Test the above script by running it once now.  This is mostly to catch syntax or other errors that would produce a red error window.  It can't test the trigger or ensure the script will have desired results."
ItemRackText.EVENTSCANCEL_TEXT = "Return to Events"
ItemRackText.EVENTSCANCEL_TOOLTIP = "This will cancel any unsaved changes and return to the events list."
ItemRackText.EVENTNAME_TEXT = "Event Name"
ItemRackText.EVENTNAME_TOOLTIP = "This is the name of the event as listed in the previous window.  ie, \"Riding\", \"Warrior:Berserker\", etc\n\nPrefix a name with Class: to let the 'Show All' option filter events by classes, ie, \"Priest:Shadowform\""
ItemRackText.EVENTTRIGGER_TEXT = "Event Trigger"
ItemRackText.EVENTTRIGGER_TOOLTIP = "This is the trigger fired from WoW when you want the event to occur.\n\nSome common ones:\nPLAYER_AURAS_CHANGED : When your buffs or forms change.\nPLAYER_REGEN_DISABLED : When you enter combat mode.\nPLAYER_REGEN_ENABLED : When you leave combat mode.\n\nwww.wowwiki.com/Events lists them all."
ItemRackText.EVENTDELAY_TEXT = "Event Delay"
ItemRackText.EVENTDELAY_TOOLTIP = "This is the time (in seconds) after the latest trigger before performing this event.  A zero here will immediately perform the event each trigger.  Some triggers can happen many times in a flurry, such as BAG_UPDATE.  A delay here will ensure the event runs a single time once the flurry of triggers are over."

ItemRackText.RESETBUTTON_TEXT = "Reset Bar"
ItemRackText.RESETBUTTON_TOOLTIP = "Click this to restore the windows and scales to a default state in the event you lose them off the screen or shrink them too small to resize.  Events, sets and items on the bar are not affected."
ItemRackText.RESETEVENTSBUTTON_TEXT = "Reset Events"
ItemRackText.RESETEVENTSBUTTON_TOOLTIP = "Click this to restore events (Mount, Plaguelands, etc) to their default state.  Custom events will be removed.  NOTE: THIS WILL REMOVE CUSTOM EVENTS"

ItemRackText.DisableToggleText = {
	["ON"] = "Left click: toggle sets menu\nRight click: toggle config\nDrag: move icon",
	["OFF"] = "Left click: toggle bar\nRight click: toggle config\nDrag: move icon"
}

ItemRackText.HELP = "This is a mod to make swapping equipment easier.  You add equipment slots to a bar and mouseover on the bar will create a menu of all items in your bags that can go in that slot.\n\nTo move the minimap button, drag it like you would an ordinary window.\n\nTo set up:\n1. Open your character sheet. (C key is default)\n2. Alt+Click slots in the character sheet to add them to the bar.\n3. Alt+Click yourself in the character sheet to add sets to the bar.\n4. Use Alt+Click to remove slots/sets from the bar as well.\n\nTo use:\nMouseover a slot you added to the bar and it will present a menu of all items in your bags that can go in that slot.\nClick an item in the menu to swap to that item.\nClick an item on the bar to use that item if it's usable.\n\nTo create a set:\n1. Select which slots to save by clicking the slots around this window.\n2. Highlighted slots will save to the set, darkened slots will be ignored.\n3. If needed, swap to the gear you want to save to this set.\n4. Enter a name at the top of the sets window.\n5. Choose an icon below the name.\n6. Click Save.\n\nTo use a set, one of:\n- Bind a key to the set with 'Bind Key' button.\n- Swap from the bar as you would an item.\n- /script EquipSet(\"setname\") in a macro."



--[[ Extra Icons 

	Here you can add more icons available for use in the set builder.
	There are two ways to add an icon:

	1. Draw your own 64x64 uncompressed 32-bit TGA file and put it into Interface\Icons

	2. Use a "built-in" icon by adding its exact path/name to the list below.

	The icons below will list immediately after the icons for the worn gear in the order
	they are listed here.  If you draw your own icon and put it into Interface\Icons,
	you do not need to list it here.  They will be picked up automatically.

]]

ItemRackExtraIcons = {
	"Interface\\Icons\\INV_Banner_02",
	"Interface\\Icons\\INV_Banner_03",
	-- add new icons here in this format: "Interface\\Icons\\(ExactIconName)",
}

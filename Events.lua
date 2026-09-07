--[[ Events.lua - Default automated gear-swapping event definitions for ItemRack ]]

ItemRack = ItemRack or {}

--[[ Events

	These are the default events.  They are locale-specific.
	/itemrack reset events : Will restore events to a default state
]]

ItemRack_DefaultEvents = {
	["Druid:Caster Form"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "if not ItemRack_GetForm() and IR_FORM then EquipSet() IR_FORM=nil end --[[Equip a set when not in an animal form.]]",
	},
	["Druid:Aquatic Form"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local form=ItemRack_GetForm() if form==\"Aquatic Form\" and IR_FORM~=form then EquipSet() IR_FORM=form end --[[Equip a set when in aquatic form.]]",
	},
	["Druid:Moonkin Form"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local form=ItemRack_GetForm() if form==\"Moonkin Form\" and IR_FORM~=form then EquipSet() IR_FORM=form end --[[Equip a set when in moonkin form.]]",
	},
	["Insignia Used"] = {
		["trigger"] = "ITEMRACK_ITEMUSED",
		["delay"] = 0.5,
		["script"] = "if arg1==\"Insignia of the Alliance\" or arg1==\"Insignia of the Horde\" then EquipSet() end --[[Equips a set when the Insignia of the Alliance/Horde has been used.]]",
	},
	["Plaguelands"] = {
		["trigger"] = "ZONE_CHANGED_NEW_AREA",
		["delay"] = 1,
		["script"] = "local zone = GetRealZoneText(),0\nif (zone==\"Western Plaguelands\" or zone==\"Eastern Plaguelands\" or zone==\"Scholomance\" or zone==\"Stratholme\") and not IR_PLAGUE then\n    EquipSet() IR_PLAGUE=1\nelseif IR_PLAGUE then\n    LoadSet() IR_PLAGUE=nil\nend\n--[[Equips set to be worn while in plaguelands.]]",
	},
	["Druid:Cat Form"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local form=ItemRack_GetForm() if form==\"Cat Form\" and IR_FORM~=form then EquipSet() IR_FORM=form end --[[Equip a set when in cat form.]]",
	},
	["Low Mana"] = {
		["trigger"] = "UNIT_MANA",
		["delay"] = 0.5,
		["script"] = "local mana = UnitMana(\"player\") / UnitManaMax(\"player\")\nif mana < .5 and not IR_OOM then\n  SaveSet()\n  EquipSet()\n  IR_OOM = 1\nelseif IR_OOM and mana > .75 then\n  LoadSet()\n  IR_OOM = nil\nend\n--[[Equips a set when mana is below 50% and re-equips previous gear at 75% mana. Remember: You can't swap non-weapons in combat.]]",
	},
	["Rogue:Stealth"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local _,_,isActive = GetShapeshiftFormInfo(1)\nif isActive and not IR_FORM then\n  EquipSet() IR_FORM=1\nelseif not isActive and IR_FORM then\n  LoadSet() IR_FORM=nil\nend\n--[[Equips set to be worn while stealthed.]]",
	},
	["Mage:Evocation"] = {
		["trigger"] = "ITEMRACK_BUFFS_CHANGED",
		["delay"] = 0.25,
		["script"] = "local evoc=arg1[\"Interface\\\\Icons\\\\Spell_Nature_Purge\"]\nif evoc and not IR_EVOC then\n  EquipSet() IR_EVOC=1\nelseif not evoc and IR_EVOC then\n  LoadSet() IR_EVOC=nil\nend\n--[[Equips a set to wear while channeling Evocation.]]",
	},
	["Warrior:Berserker"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local _,_,isActive = GetShapeshiftFormInfo(3) if isActive and IR_FORM~=\"Berserker\" then EquipSet() IR_FORM=\"Berserker\" end --[[Equips set to be worn in Berserker stance.]]",
	},
	["Druid:Bear Form"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local form = ItemRack_GetForm()\nif (form==\"Dire Bear Form\" or form==\"Bear Form\") and IR_FORM~=\"Bear Form\" then EquipSet() IR_FORM=\"Bear Form\" end --[[Equip a set when in bear form.]]",
	},
	["Priest:Spirit Tap Begin"] = {
		["trigger"] = "PLAYER_REGEN_ENABLED",
		["delay"] = 0.25,
		["script"] = "local found=ItemRack.Buffs[\"Interface\\\\Icons\\\\Spell_Shadow_Requiem\"]\nif not IR_SPIRIT and found then\nEquipSet() IR_SPIRIT=1\nend\n--[[Equips a set when you leave combat with Spirit Tap. Associate a set of spirit gear to this event.]]",
	},
	["Priest:Spirit Tap End"] = {
		["trigger"] = "ITEMRACK_BUFFS_CHANGED",
		["delay"] = 0.5,
		["script"] = "local found=arg1[\"Interface\\\\Icons\\\\Spell_Shadow_Requiem\"]\nif IR_SPIRIT and not found then\nLoadSet() IR_SPIRIT = nil\nend\n--[[Returns to normal gear when Spirit Tap ends. Associate the same spirit set as Spirit Tap Begin.]]",
	},
	["Warrior:Battle"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local _,_,isActive = GetShapeshiftFormInfo(1) if isActive and IR_FORM~=\"Battle\" then EquipSet() IR_FORM=\"Battle\" end --[[Equips set to be worn in battle stance.]]",
	},
	["Skinning"] = {
		["trigger"] = "UPDATE_MOUSEOVER_UNIT",
		["delay"] = 0,
		["script"] = "if UnitIsDead(\"mouseover\") and GameTooltipTextLeft3:GetText()==UNIT_SKINNABLE then\n  local r,g,b = GameTooltipTextLeft3:GetTextColor()\n  if r>.9 and g<.2 and b<.2 and not IR_SKIN then\n    EquipSet() IR_SKIN=1\n  end\nelseif IR_SKIN then\n  LoadSet() IR_SKIN=nil\nend\n--[[Equips a set when you mouseover something that can be skinned but you have insufficient skill.]]\n",
	},
	["Warrior:Overpower End"] = {
		["trigger"] = "CHAT_MSG_COMBAT_SELF_MISSES",
		["delay"] = 5,
		["script"] = "--[[Equip a set five seconds after opponent dodged: your normal weapons. ]]\nif IR_OVERPOWER==1 then\nEquipSet()\nIR_OVERPOWER=nil\nend",
	},
	["Druid:Travel Form"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local form=ItemRack_GetForm() if form==\"Travel Form\" and IR_FORM~=form then EquipSet() elseif form~=\"Travel Form\"  then LoadSet() end IR_FORM=form --[[Equip a set when in travel form.]]",
	},
	["Mount"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local mount = (IsMounted and IsMounted()) or (UnitIsMounted and UnitIsMounted(\"player\")) or ItemRack_PlayerMounted()\nif not IR_MOUNT and mount then\n  EquipSet()\nelseif IR_MOUNT and not mount then\n  LoadSet()\nend\nIR_MOUNT=mount\n--[[Equips set to be worn while mounted.]]",
	},
	["Swimming"] = {
		["trigger"] = "MIRROR_TIMER_START",
		["delay"] = 0,
		["script"] = "local i,found\nfor i=1,3 do\n  if getglobal(\"MirrorTimer\"..i):IsVisible() and getglobal(\"MirrorTimer\"..i..\"Text\"):GetText() == BREATH_LABEL then\n    found = 1\n  end\nend\nif found then\n  EquipSet()\nend\n--[[Equips a set when the breath gauge appears. NOTE: This will not re-equip gear when you leave water.  There's no reliable way to know when you leave water. Also note: Won't work with eCastingBar.]]",
	},
	["Eating-Drinking"] = {
		["trigger"] = "ITEMRACK_BUFFS_CHANGED",
		["delay"] = 0,
		["script"] = "local found=arg1[\"Interface\\\\Icons\\\\INV_Misc_Fork&Knife\"] or arg1[\"Drink\"]\nif not IR_DRINK and found then\nEquipSet() IR_DRINK=1\nelseif IR_DRINK and not found then\nLoadSet() IR_DRINK=nil\nend\n--[[Equips a set while eating or drinking.]]",
	},
	["Warrior:Defensive"] = {
		["trigger"] = "PLAYER_AURAS_CHANGED",
		["delay"] = 0,
		["script"] = "local _,_,isActive = GetShapeshiftFormInfo(2) if isActive and IR_FORM~=\"Defensive\" then EquipSet() IR_FORM=\"Defensive\" end --[[Equips set to be worn in Defensive stance.]]",
	},
	["Insignia"] = {
		["trigger"] = "ITEMRACK_NOTIFY",
		["delay"] = 0,
		["script"] = "if arg1==\"Insignia of the Alliance\" or arg1==\"Insignia of the Horde\" then EquipSet() end --[[Equips a set when the Insignia of the Alliance/Horde finishes cooldown.]]",
	},
	["Priest:Shadowform"] = {
		["trigger"] = "ITEMRACK_BUFFS_CHANGED",
		["delay"] = 0,
		["script"] = "local f=arg1[\"Interface\\\\Icons\\\\Spell_Shadow_Shadowform\"]\nif not IR_Shadowform and f then\n  EquipSet() IR_Shadowform=1\nelseif IR_Shadowform and not f then\n  LoadSet() IR_Shadowform=nil\nend\n--[[Equips a set while under Shadowform]]",
	},

	["Warrior:Overpower Begin"] = {
		["trigger"] = "CHAT_MSG_COMBAT_SELF_MISSES",
		["delay"] = 0,
		["script"] = "--[[Equip a set when the opponent dodges.  Associate a heavy-hitting 2h set with this event. ]]\nlocal _,_,i = GetShapeshiftFormInfo(1)\nif string.find(arg1 or \"\",\"^You.+dodge[sd]\") and i then\nEquipSet()\nIR_OVERPOWER=1\nend",
	},
	["About Town"] = {
		["trigger"] = "PLAYER_UPDATE_RESTING",
		["delay"] = 0,
		["script"] = "if IsResting() and not IR_TOWN then EquipSet() IR_TOWN=1 elseif IR_TOWN then LoadSet() IR_TOWN=nil end\n--[[Equips a set while in a city or inn.]]"
	},
	["Brainwashing 1"] = {
    ["trigger"] = "ITEMRACK_GBD",
    ["delay"] = 0.1,
    ["script"] =
        "local spec = tonumber(arg1)\n" ..
        "if spec == 1 then\n" ..
        "  EquipSet()\n" ..
        "  DEFAULT_CHAT_FRAME:AddMessage(\"ItemRack - 1st Goblin Brainwashing Device set equipped\")\n" ..
        "end",
	},
	["Brainwashing 2"] = {
    ["trigger"] = "ITEMRACK_GBD",
    ["delay"] = 0.1,
    ["script"] =
        "local spec = tonumber(arg1)\n" ..
        "if spec == 2 then\n" ..
        "  EquipSet()\n" ..
        "  DEFAULT_CHAT_FRAME:AddMessage(\"ItemRack - 2nd Goblin Brainwashing Device set equipped\")\n" ..
        "end",
	},
	["Brainwashing 3"] = {
    ["trigger"] = "ITEMRACK_GBD",
    ["delay"] = 0.1,
    ["script"] =
        "local spec = tonumber(arg1)\n" ..
        "if spec == 3 then\n" ..
        "  EquipSet()\n" ..
        "  DEFAULT_CHAT_FRAME:AddMessage(\"ItemRack - 3rd Goblin Brainwashing Device set equipped\")\n" ..
        "end",
	},
	["Brainwashing 4"] = {
    ["trigger"] = "ITEMRACK_GBD", 
    ["delay"] = 0.1,
    ["script"] =
        "local spec = tonumber(arg1)\n" ..
        "if spec == 4 then\n" ..
        "  EquipSet()\n" ..
        "  DEFAULT_CHAT_FRAME:AddMessage(\"ItemRack - 4th Goblin Brainwashing Device set equipped\")\n" ..
        "end",
	},
	["Mount(Not ZG/AQ)"] = {
	["trigger"] = "PLAYER_AURAS_CHANGED",
	["delay"] = 0,
	["script"] =
		"local mount = (IsMounted and IsMounted()) or (UnitIsMounted and UnitIsMounted(\"player\")) or ItemRack_PlayerMounted()\n"..
		"local zone = GetRealZoneText()\n"..
		"local outdoorRaid = (zone == \"Ahn'Qiraj\" or zone == \"Zul'Gurub\" or zone == \"Ruins of Ahn'Qiraj\")\n"..
		"\n"..
		"if outdoorRaid then\n"..
		"  if IR_MOUNT and not mount then\n"..
		"    LoadSet()\n"..
		"  end\n"..
		"  IR_MOUNT = mount\n"..
		"  return\n"..
		"end\n"..
		"if not IR_MOUNT and mount then\n"..
		"  EquipSet()\n"..
		"elseif IR_MOUNT and not mount then\n"..
		"  LoadSet()\n"..
		"end\n"..
		"IR_MOUNT = mount\n"..
		"--[[Equips mount set as normal unless in ZG or AQ]]",
	},
}

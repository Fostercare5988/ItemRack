-- Enhanced Client startup contract for ItemRack.
local MIN_CLASSIC_API = 11400

ItemRack_EngineReady = CLASSIC_API_VERSION
	and SUPERWOW_VERSION
	and type(CLASSIC_API_VERSION) == "number"
	and CLASSIC_API_VERSION >= MIN_CLASSIC_API
	and C_Timer
	and C_Timer.NewTicker
	and C_Container
	and C_Container.GetContainerItemID
	and C_UnitAuras
	and C_UnitAuras.GetAuraSlots
	and C_UnitAuras.GetAuraDataBySlot
	and table.wipe
	and hooksecurefunc

if not ItemRack_EngineReady then
	if DEFAULT_CHAT_FRAME then
		DEFAULT_CHAT_FRAME:AddMessage("|cffff2020[ItemRack Fatal Error]|r ItemRack requires the Enhanced 1.12.1 engine (ClassicAPI v1.14.0+ and SuperWoW v2.2+).", 1, 0.2, 0.2)
	end
	return
end

-- Swap between identical weapons carrying different temporary enchants.
-- Called from a macro; no bag-position or item-GUID state is persisted.

if not Rack then return end

local function poison_swap_message(message)
	DEFAULT_CHAT_FRAME:AddMessage("|cFFFFFF00ItemRack Poison Swap:|r " .. message)
end

function ItemRack_SwapPoison(slot, targetEnchantID)
	slot = slot or 17
	if slot ~= 16 and slot ~= 17 then
		poison_swap_message("Use equipment slot 16 (main hand) or 17 (off hand).")
		return
	end
	if targetEnchantID ~= nil and (type(targetEnchantID) ~= "number" or targetEnchantID <= 0 or targetEnchantID ~= math.floor(targetEnchantID)) then
		poison_swap_message("Target poison must be a positive enchant ID.")
		return
	end
	if Rack.IsEquipmentSwapActive() then
		poison_swap_message("An ItemRack equipment swap is already active.")
		return
	end

	local wornLocation = { equipmentSlotIndex = slot }
	local itemID = C_Item.GetItemID(wornLocation)
	if not itemID then
		poison_swap_message("Equip one copy of the weapon first.")
		return
	end

	local hasWornEnchant, _, _, wornEnchantID = C_Item.GetItemTempEnchantInfo(wornLocation)
	if not hasWornEnchant or not wornEnchantID or wornEnchantID == 0 then
		poison_swap_message("The equipped weapon has no active poison.")
		return
	end
	if targetEnchantID == wornEnchantID then
		poison_swap_message("That poison is already equipped.")
		return
	end

	local candidate
	for bag = 0, 4 do
		for bagSlot = 1, GetContainerNumSlots(bag) do
			local location = { bagID = bag, slotIndex = bagSlot }
			if C_Item.GetItemID(location) == itemID then
				local hasEnchant, _, _, enchantID = C_Item.GetItemTempEnchantInfo(location)
				if hasEnchant and enchantID and enchantID ~= 0 and enchantID ~= wornEnchantID
					and (not targetEnchantID or enchantID == targetEnchantID) then
					if candidate then
						poison_swap_message("Multiple matching weapons found; specify a target enchant ID.")
						return
					end
					candidate = location
				end
			end
		end
	end

	if not candidate then
		poison_swap_message("No identical bagged weapon with the requested active poison was found.")
		return
	end

	-- Explicit destination uses ClassicAPI's direct, cursor-free equipment swap.
	-- The engine may still reject the request; equipment events own completion.
	C_Item.EquipItemByName(candidate, slot)
end

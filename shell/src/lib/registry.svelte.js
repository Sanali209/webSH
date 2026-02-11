
// Global Registry State
class SlotRegistry {
    slots = $state(new Map());

    register(slotId, item) {
        if (!this.slots.has(slotId)) {
            this.slots.set(slotId, []);
        }
        const items = this.slots.get(slotId);
        items.push(item);
        // Sort by priority (higher is better)
        items.sort((a, b) => (b.priority || 0) - (a.priority || 0));
        this.slots.set(slotId, items);
    }

    unregister(slotId, itemId) {
        if (!this.slots.has(slotId)) return;
        const items = this.slots.get(slotId).filter(i => i.id !== itemId);
        this.slots.set(slotId, items);
    }

    getItems(slotId) {
        return this.slots.get(slotId) || [];
    }
}

export const registry = new SlotRegistry();

import type { Widget } from '../stores/ui.svelte.ts';

/**
 * Checks if placing an item at (x, y) would overlap with any existing items.
 * Ignores the item itself if it exists in the list (based on ID).
 */
export const isValidPosition = (items: Widget[], item: Partial<Widget> & { id: string, w: number, h: number }, x: number, y: number): boolean => {
    // Check bounds (optional, but good practice. Assuming positive coordinates)
    if (x < 0 || y < 0) return false;

    // Check intersection with other items
    for (const other of items) {
        if (other.id === item.id) continue;

        // Rect 1: Proposed position
        const r1Left = x;
        const r1Right = x + item.w;
        const r1Top = y;
        const r1Bottom = y + item.h;

        // Rect 2: Existing item
        const r2Left = other.x;
        const r2Right = other.x + other.w;
        const r2Top = other.y;
        const r2Bottom = other.y + other.h;

        // Check for overlap
        const overlaps = !(r1Right <= r2Left ||
                           r1Left >= r2Right ||
                           r1Bottom <= r2Top ||
                           r1Top >= r2Bottom);

        if (overlaps) {
            return false;
        }
    }
    return true;
};

/**
 * Finds the first available spot for an item of size w x h.
 * Scans row by row, then column by column.
 */
export const findEmptySpot = (items: Widget[], w: number, h: number, cols: number = 12, maxRows: number = 100): { x: number, y: number } | null => {
    for (let y = 0; y < maxRows; y++) {
        // Only iterate x such that the item fits within cols
        for (let x = 0; x <= cols - w; x++) {
            // Create a dummy object for validation
            const dummy = { id: 'temp_search', w, h };
            if (isValidPosition(items, dummy, x, y)) {
                return { x, y };
            }
        }
    }
    return null;
};

/**
 * Places an item at (x, y) if valid.
 * Returns a new array of widgets with the item updated or added.
 * Throws an error if the position is invalid (overlap).
 */
export const placeItem = (items: Widget[], item: Widget, x: number, y: number): Widget[] => {
    if (!isValidPosition(items, item, x, y)) {
        throw new Error(`Cannot place item at (${x}, ${y}): Overlap detected.`);
    }

    const index = items.findIndex(i => i.id === item.id);
    const updatedItem = { ...item, x, y };

    if (index !== -1) {
        // Update existing
        const newItems = [...items];
        newItems[index] = updatedItem;
        return newItems;
    } else {
        // Add new
        return [...items, updatedItem];
    }
};

/**
 * Re-packs items into the grid based on the current order, updating x and y coordinates.
 * This simulates a dense packing or standard flow layout.
 */
export const packItems = (items: Widget[], cols: number = 12): Widget[] => {
    const placed: Widget[] = [];

    for (const item of items) {
        // Ensure item width doesn't exceed columns
        const w = Math.min(item.w, cols);

        // Find the first available spot for this item considering already placed items
        // Increase maxRows to handle large grids
        const spot = findEmptySpot(placed, w, item.h, cols, 1000);

        if (spot) {
            placed.push({ ...item, w, x: spot.x, y: spot.y });
        } else {
            // Fallback: place at the bottom
            const maxY = placed.length > 0 ? Math.max(...placed.map(p => p.y + p.h)) : 0;
            placed.push({ ...item, w, x: 0, y: maxY });
        }
    }
    return placed;
};

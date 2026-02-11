import { describe, it, expect } from 'vitest';
import { isValidPosition, findEmptySpot, placeItem, packItems } from './gridManager';
import type { Widget } from '../stores/ui.svelte.ts';

describe('gridManager', () => {
    const mockWidget: Widget = {
        id: '1',
        x: 0,
        y: 0,
        w: 1,
        h: 1,
        type: 'icon'
    };

    describe('isValidPosition', () => {
        it('should return true for empty grid', () => {
            expect(isValidPosition([], mockWidget, 0, 0)).toBe(true);
        });

        it('should return false if overlapping', () => {
            const items = [{ ...mockWidget, x: 0, y: 0 }];
            const newItem = { ...mockWidget, id: '2' };
            expect(isValidPosition(items, newItem, 0, 0)).toBe(false);
        });

        it('should return true if not overlapping', () => {
            const items = [{ ...mockWidget, x: 0, y: 0 }];
            const newItem = { ...mockWidget, id: '2' };
            expect(isValidPosition(items, newItem, 1, 0)).toBe(true);
        });

        it('should ignore itself', () => {
            const items = [{ ...mockWidget, x: 0, y: 0 }];
            expect(isValidPosition(items, mockWidget, 0, 0)).toBe(true);
        });
    });

    describe('findEmptySpot', () => {
        it('should return (0, 0) for empty grid', () => {
            expect(findEmptySpot([], 1, 1)).toEqual({ x: 0, y: 0 });
        });

        it('should skip occupied spots', () => {
            const items = [{ ...mockWidget, x: 0, y: 0 }];
            // (0,0) is taken. Next is (1,0)
            expect(findEmptySpot(items, 1, 1)).toEqual({ x: 1, y: 0 });
        });

        it('should handle multi-cell widgets', () => {
            // Place a 2x1 widget at (0,0). Covers (0,0) and (1,0).
            const items = [{ ...mockWidget, w: 2, h: 1, x: 0, y: 0 }];
            // Next spot should be (2,0)
            expect(findEmptySpot(items, 1, 1)).toEqual({ x: 2, y: 0 });
        });

        it('should wrap to next row if no space in col', () => {
            // Fill first row (assuming 12 cols)
            const items = [];
            for(let i=0; i<12; i++) {
                items.push({ ...mockWidget, id: `${i}`, x: i, y: 0 });
            }
            expect(findEmptySpot(items, 1, 1)).toEqual({ x: 0, y: 1 });
        });
    });

    describe('placeItem', () => {
        it('should place item if valid', () => {
            const items = [];
            const newItems = placeItem(items, mockWidget, 5, 5);
            expect(newItems).toHaveLength(1);
            expect(newItems[0]).toEqual({ ...mockWidget, x: 5, y: 5 });
        });

        it('should throw error if invalid', () => {
            const items = [{ ...mockWidget, x: 0, y: 0 }];
            expect(() => placeItem(items, { ...mockWidget, id: '2' }, 0, 0)).toThrow();
        });

        it('should update existing item', () => {
             const items = [{ ...mockWidget, x: 0, y: 0 }];
             const newItems = placeItem(items, mockWidget, 2, 2);
             expect(newItems).toHaveLength(1);
             expect(newItems[0]).toEqual({ ...mockWidget, x: 2, y: 2 });
        });
    });

    describe('packItems', () => {
        it('should pack items tightly', () => {
            const items = [
                { ...mockWidget, id: '1', w: 1, h: 1 },
                { ...mockWidget, id: '2', w: 1, h: 1 },
                { ...mockWidget, id: '3', w: 1, h: 1 }
            ];
            const packed = packItems(items, 2);
            // Should be (0,0), (1,0), (0,1)
            expect(packed[0]).toMatchObject({ x: 0, y: 0 });
            expect(packed[1]).toMatchObject({ x: 1, y: 0 });
            expect(packed[2]).toMatchObject({ x: 0, y: 1 });
        });

        it('should handle large items', () => {
            const items = [
                { ...mockWidget, id: '1', w: 2, h: 1 }, // takes (0,0), (1,0)
                { ...mockWidget, id: '2', w: 1, h: 1 }  // takes (0,1) because row 0 full
            ];
            const packed = packItems(items, 2);
            expect(packed[0]).toMatchObject({ x: 0, y: 0 });
            expect(packed[1]).toMatchObject({ x: 0, y: 1 });
        });
    });
});

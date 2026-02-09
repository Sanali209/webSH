/**
 * E2E Tests for Plugin Loading and APIs
 * 
 * Tests that plugins load correctly and APIs work
 */
import { test, expect } from '@playwright/test';
import { navigateAndWait } from './setup';

test.describe('Plugin System', () => {
  test('should load plugins on startup', async ({ page }) => {
    // Listen for console messages about plugin loading
    const messages: string[] = [];
    page.on('console', msg => {
      messages.push(msg.text());
    });
    
    await navigateAndWait(page);
    
    // Check that ModuleLoader initialized
    const hasInitMessage = messages.some(msg => 
      msg.includes('ModuleLoader initialized') || 
      msg.includes('Successfully loaded plugin')
    );
    expect(hasInitMessage).toBe(true);
  });
  
  test('plugins API endpoint returns active plugins', async ({ page }) => {
    const response = await page.request.get('/api/plugins');
    expect(response.ok()).toBe(true);
    
    const plugins = await response.json();
    expect(Array.isArray(plugins)).toBe(true);
    expect(plugins.length).toBeGreaterThan(0);
    
    // Check for system plugins
    const pluginIds = plugins.map((p: any) => p.id);
    expect(pluginIds).toContain('system_fs');
    expect(pluginIds).toContain('system_llm');
    expect(pluginIds).toContain('system_dashboard');
  });
  
  test('system_llm plugin API works', async ({ page }) => {
    const response = await page.request.get('/api/plugins/system_llm/info');
    expect(response.ok()).toBe(true);
    
    const info = await response.json();
    expect(info.model).toBe('all-MiniLM-L6-v2');
    expect(info.dimension).toBe(384);
    expect(info.capabilities).toContain('llm.embed');
  });
  
  test('system_llm embed endpoint works', async ({ page }) => {
    const response = await page.request.post('/api/plugins/system_llm/embed', {
      data: { text: 'Hello, world!' }
    });
    expect(response.ok()).toBe(true);
    
    const result = await response.json();
    expect(result.embedding).toBeDefined();
    expect(Array.isArray(result.embedding)).toBe(true);
    expect(result.embedding.length).toBe(384);
    expect(result.dimension).toBe(384);
  });
  
  test('system_dashboard config endpoint works', async ({ page }) => {
    const response = await page.request.get('/api/plugins/system_dashboard/config');
    expect(response.ok()).toBe(true);
    
    const config = await response.json();
    expect(config.grid_columns).toBe(12);
    expect(config.row_height).toBeDefined();
    expect(config.gap).toBeDefined();
  });
});

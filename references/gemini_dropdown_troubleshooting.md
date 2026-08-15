# Gemini Dropdown Troubleshooting (Radix UI)

When selecting the Gemini Omni Flash model in Google Flow, the dropdown uses Radix UI components with dynamically generated role attributes (`role="option"` or `role="menuitem"`). Direct CSS selectors like `:has-text()` are not supported in Playwright's auto-selector engine, causing `InvalidSelectorError`.

## Verified approaches

1. **Iterate over options by innerText**:
   ```python
   option_locator = page.locator('[role="option"], [role="menuitem"]')
   for i in range(min(await option_locator.count(), 20)):
       opt = option_locator.nth(i)
       text = await opt.inner_text()
       if 'Gemini Omni Flash' in text or 'Gemini Omni Flash'.lower() in text.lower():
           await opt.click()
           break
   ```

2. **Fallback to first option**:
   If the target text is not found, clicking the first option often selects a default model; verify via UI that the correct model is now active.

3. **Direct evaluation**:
   ```javascript
   () => {
       const options = Array.from(document.querySelectorAll('[role="option"], [role="menuitem"]'));
       for (const opt of options) {
           if (opt.innerText.trim() === 'Gemini Omni Flash') {
               opt.click();
               return true;
           }
       }
       return false;
   }
   ```
   Use `page.evaluate()` to run the script and check the boolean result.

4. **Coordinate‑based click** (rare):
   If the element is visually present but not interactable, obtain its bounding box and click at `(x + width/2, y + height/2)`.

## Debugging tips

- Log `await page.inner_text('body')` to verify the dropdown markup contains the expected label.
- Use `page.screenshot()` after clicking ULTRA to confirm the dropdown opened.
- Exclude reCAPTCHA elements (`id*="g-recaptcha"` or `class*="g-recaptcha"`) when searching for input fields.

This reference should be consulted whenever the selection step fails, to replace generic retry loops with the precise iteration logic above.
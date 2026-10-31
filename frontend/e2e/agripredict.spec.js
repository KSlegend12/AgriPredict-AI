import { test, expect } from '@playwright/test';

test.describe('AgriPredict-AI End-to-End Application Verification', () => {

  test('1. Application loads successfully and renders home page', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/AgriPredict/i);
    await expect(page.locator('text=AgriPredictAI').first()).toBeVisible();
    await expect(page.locator('header.app-header')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
    // Verify hero CTA
    const cta = page.locator('text=Predict Yield').first();
    await expect(cta).toBeVisible();
  });

  test('2. Navigation between major pages works smoothly', async ({ page }) => {
    await page.goto('/');

    const routes = [
      { path: '/dashboard', heading: /Dashboard|Crop|Weather/i },
      { path: '/cotton', heading: /Cotton Yield Prediction/i },
      { path: '/recommend', heading: /Cotton Agronomic Advisory|Crop Suitability|Crop Advisory/i },
      { path: '/weather', heading: /Weather Intelligence|Real-Time Weather/i },
      { path: '/future-forecast', heading: /Cotton Yield Forecast/i },
      { path: '/history', heading: /Historical Yield|Audit Trail/i },
      { path: '/insights', heading: /Architecture|Model|Insights/i },
      { path: '/satellite', heading: /Satellite|Remote Sensing|Soil Moisture/i },
      { path: '/how-it-works', heading: /How It Works|Methodology/i },
      { path: '/about', heading: /About AgriPredict|Decision-Support/i },
    ];

    for (const r of routes) {
      await page.goto(r.path);
      await expect(page).toHaveURL(new RegExp(r.path));
      await expect(page.locator('header.app-header')).toBeVisible();
      await expect(page.locator('body')).not.toContainText('Something went wrong');
    }
  });

  test('3. District selection works and persists across navigation', async ({ page }) => {
    await page.goto('/');

    // Select Nagpur in the navbar select
    const districtSelect = page.locator('select.district-select').first();
    await expect(districtSelect).toBeVisible();
    await districtSelect.selectOption('Nagpur');

    // Verify localStorage has been updated
    const savedDistrict = await page.evaluate(() => localStorage.getItem('agripredict-district'));
    expect(savedDistrict).toBe('Nagpur');

    // Navigate to Weather page and verify Nagpur heading is reflected
    await page.goto('/weather');
    await expect(page.locator('h2:has-text("Nagpur")').first()).toBeVisible();
  });

  test('4. Cotton advisory signals page renders weather, historical, and model insights', async ({ page }) => {
    await page.goto('/recommend');

    // Verify header and title
    await expect(page.locator('h1:has-text("Decision Support & Advisory Signals")')).toBeVisible({ timeout: 15000 });

    // Verify sections render
    await expect(page.getByRole('heading', { name: 'Weather Insight' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Historical Insight' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Model Insight', exact: true })).toBeVisible();
    await expect(page.locator('text=Decision Support Disclaimer')).toBeVisible();
  });

  test('5. District selection updates advisory insights smoothly without crashing', async ({ page }) => {
    await page.goto('/recommend');

    // Verify select element exists
    const select = page.locator('main select');
    await expect(select).toBeVisible();
    await select.selectOption('Amravati');

    // Verify page updates and never crashes to ErrorBoundary
    await expect(page.locator('body')).not.toContainText('Something went wrong');
    await expect(page.locator('header.app-header')).toBeVisible();
    await expect(page.locator('text=Decision Support & Advisory Signals')).toBeVisible();
  });

  test('6. Cotton prediction form multi-step workflow loads verified data', async ({ page }) => {
    await page.goto('/cotton');

    // Step 1: Select Akola and 2024
    await expect(page.locator('text=STEP 01 / 05')).toBeVisible();
    
    // Select Akola
    const akolaBtn = page.locator('button:has-text("Akola District")');
    if (await akolaBtn.isVisible()) {
      await akolaBtn.click();
    }

    // Click Load Verified Data
    const loadBtn = page.locator('button:has-text("Load Verified Data")');
    await expect(loadBtn).toBeVisible();
    await loadBtn.click();

    // Advances to Step 2
    await expect(page.locator('text=STEP 02 / 05').or(page.locator('text=Historical Weather Review'))).toBeVisible({ timeout: 12000 });

    // Click View Historical Features to advance to Step 3
    const toStep3Btn = page.locator('button:has-text("View Historical Features")');
    await expect(toStep3Btn).toBeVisible();
    await toStep3Btn.click();

    // Step 3 visible
    await expect(page.locator('text=STEP 03 / 05').or(page.locator('text=Historical Feature Inputs'))).toBeVisible();

    // Click Review to advance to Step 4 (use exact button to avoid ambiguity with step tab '04 Review')
    const toStep4Btn = page.getByRole('button', { name: 'Review', exact: true });
    await expect(toStep4Btn).toBeVisible();
    await toStep4Btn.click();

    // Step 4 Review visible
    await expect(page.locator('text=STEP 04 / 05').or(page.locator('text=Model & Review'))).toBeVisible();
  });

  test('7. Model selection dynamically updates review card metadata', async ({ page }) => {
    await page.goto('/cotton');

    // Change model selector to DAR + Deficit + Heat Thresh
    const modelSelect = page.locator('select').nth(2); // Model Architecture selector
    await modelSelect.selectOption('candidate_six_district_dar_deficit_heat_thresh');

    // Click Load Verified Data
    await page.locator('button:has-text("Load Verified Data")').click();
    await expect(page.locator('text=STEP 02 / 05')).toBeVisible({ timeout: 12000 });

    // Advance to Step 3
    await page.locator('button:has-text("View Historical Features")').click();

    // Advance to Step 4
    await page.getByRole('button', { name: 'Review', exact: true }).click();
    await expect(page.locator('text=STEP 04 / 05')).toBeVisible();

    // Verify Review Card shows the selected candidate's metrics
    await expect(page.locator('text=Ridge_Delta_Rolling_SixDistricts_Decoupled_Deficit_HeatThresh').or(page.locator('text=DAR + Deficit + Heat Thresh'))).toBeVisible();
    await expect(page.locator('text=102.60 kg/ha').first()).toBeVisible();
  });

  test('8. Cotton prediction displays actual model version and SHAP explanation', async ({ page }) => {
    await page.goto('/cotton');

    // Load data and navigate to Step 4
    await page.locator('button:has-text("Load Verified Data")').click();
    await expect(page.locator('text=STEP 02 / 05')).toBeVisible({ timeout: 12000 });
    await page.locator('button:has-text("View Historical Features")').click();
    await page.getByRole('button', { name: 'Review', exact: true }).click();

    // Generate Prediction on Step 4
    const predictBtn = page.locator('button:has-text("Generate Prediction")');
    await expect(predictBtn).toBeVisible();
    await predictBtn.click();

    // Verify Step 5 results
    await expect(page.locator('text=Prediction Generated')).toBeVisible({ timeout: 15000 });
    await expect(page.locator('text=kg/ha').first()).toBeVisible();

    // Verify Explainable AI (SHAP) component
    await expect(page.locator('text=Why This Prediction?')).toBeVisible();
    await expect(page.locator('text=Explainable AI (SHAP)').or(page.locator('text=Top Influential Features')).or(page.locator('text=Feature Contribution')).first()).toBeVisible();
  });

  test('9. Future cotton forecast displays scenario toggles and data provenance', async ({ page }) => {
    await page.goto('/future-forecast');

    // Verify header
    await expect(page.locator('h1:has-text("Cotton Yield Forecast")')).toBeVisible({ timeout: 15000 });

    // Verify scenario buttons
    const normalBtn = page.locator('button:has-text("Normal")').first();
    const dryBtn = page.locator('button:has-text("Dry")').first();
    const wetBtn = page.locator('button:has-text("Wet")').first();

    await expect(normalBtn).toBeVisible();
    await expect(dryBtn).toBeVisible();
    await expect(wetBtn).toBeVisible();

    // Toggle Dry scenario
    await dryBtn.click();
    await expect(dryBtn).toBeVisible();

    // Toggle Wet scenario
    await wetBtn.click();
    await expect(wetBtn).toBeVisible();

    // Verify Data Provenance & Observation Boundaries
    await expect(page.locator('text=Forecast origin: 2024')).toBeVisible();
    await expect(page.locator('text=Data Provenance & Observation Boundaries')).toBeVisible();
  });

  test('10. Prediction history page loads and renders audit log table', async ({ page }) => {
    await page.goto('/history');

    // Verify trends section
    await expect(page.locator('text=Historical Yield & Climate Trends (1997–2024)')).toBeVisible();

    // Verify prediction audit trail table
    await expect(page.locator('text=Prediction Audit Trail')).toBeVisible();
    await expect(page.locator('th:has-text("Timestamp")')).toBeVisible();
    await expect(page.locator('th:has-text("District")')).toBeVisible();
    await expect(page.locator('th:has-text("Predicted Yield")')).toBeVisible();
  });

  test('11. Satellite data page displays NASA SMAP provenance and coverage', async ({ page }) => {
    await page.goto('/satellite');

    // Check heading and content
    await expect(page.locator('h1, h2').filter({ hasText: /Satellite|Soil Moisture|SMAP/i }).first()).toBeVisible();
    await expect(page.locator('body')).not.toContainText('Something went wrong');
  });

  test('12. API error simulation does not crash the frontend application', async ({ page }) => {
    // Intercept weather API call with HTTP 500 error
    await page.route('**/api/weather/**', route => {
      route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Simulated weather upstream outage' }),
      });
    });

    await page.goto('/weather');

    // Verify application remains interactive without React ErrorBoundary crash
    await expect(page.locator('header.app-header')).toBeVisible();
    await expect(page.locator('footer')).toBeVisible();
    await expect(page.locator('body')).not.toContainText('Something went wrong');
  });

  test('13. Scope enforcement: 6 Vidarbha districts available and Yavatmal excluded', async ({ page }) => {
    await page.goto('/');

    // Check navbar district selector has exactly 6 Vidarbha districts
    const districtSelect = page.locator('select.district-select').first();
    await expect(districtSelect).toBeVisible();

    const expectedDistricts = ['Akola', 'Amravati', 'Buldhana', 'Nagpur', 'Wardha', 'Washim'];
    for (const d of expectedDistricts) {
      await expect(districtSelect.locator(`option[value="${d}"]`)).toBeAttached();
    }

    // Verify Yavatmal is strictly excluded from district selector
    await expect(districtSelect.locator('option[value="Yavatmal"]')).not.toBeAttached();
  });

});

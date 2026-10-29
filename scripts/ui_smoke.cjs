const { chromium } = require('../.tools/node_modules/@playwright/test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
(async () => {
  fs.mkdirSync('artifacts', {recursive:true});
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1366,height:900}});
  const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:8011/home');
  await page.waitForFunction(()=>window.App && App.tours.length > 0);
  await page.waitForTimeout(500);
  await page.evaluate(()=>App.openGuestBookingModal());
  assert(await page.locator('#guest-booking-modal').isVisible());
  await page.evaluate(()=>App.closeModal('guest-booking-modal'));
  await page.evaluate(()=>App.openGuestBookingModal());
  assert(await page.locator('#guest-booking-modal').isVisible());
  await page.keyboard.press('Escape');
  assert(!(await page.locator('#guest-booking-modal').isVisible()));
  await page.evaluate(()=>App.openGuestBookingModal());
  await page.fill('#guest-cust-name', "Khách O'Neil");
  await page.fill('#guest-cust-phone', '0909999123');
  await page.fill('#guest-cust-email', 'guest@example.com');
  await page.evaluate(()=>Promise.all([App.submitGuestBooking(), App.submitGuestBooking()]));
  await page.waitForSelector('#booking-confirmation');
  assert((await page.locator('#booking-confirmation').textContent()).includes('REQ-'));
  await page.evaluate(()=>{
    const el=document.createElement('div'); el.id='xss-probe'; document.body.append(el);
    el.innerHTML='<img src=x onerror="window.xss=1"><script>window.xss=2</script>';
  });
  await page.waitForTimeout(100);
  assert.equal(await page.evaluate(()=>window.xss),undefined);
  await page.locator('#xss-probe').evaluate(el=>el.remove());
  await page.screenshot({path:'artifacts/home-desktop.png',fullPage:true});
  for(const width of [360,390,768]) {
    await page.setViewportSize({width,height:844});
    await page.screenshot({path:`artifacts/home-${width}.png`,fullPage:true});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth+1),`horizontal overflow at ${width}`);
  }
  await page.setViewportSize({width:390,height:844});
  await page.locator('#sidebar-toggle-btn').click();
  assert(await page.locator('#main-sidebar').isVisible());
  await page.keyboard.press('Escape');
  await page.goto('http://127.0.0.1:8011/login');
  await page.fill('#input-username','admin'); await page.fill('#input-password','admin123');
  await page.click('#btn-submit-login'); await page.waitForURL('**/home');
  for(const path of ['tours','departures','queue','bookings','payments','guides','feedbacks','analytics','users','ai']) {
    await page.goto(`http://127.0.0.1:8011/${path}`);
    await page.waitForFunction(()=>window.App && App.currentUser);
    await page.waitForTimeout(350);
    assert(await page.locator(`#view-${path}`).isVisible(),`${path} view hidden`);
  }
  await page.evaluate(()=>AIHub.switchSubTab('desc'));
  await page.fill('#ai-gen-title','Tour kiểm thử'); await page.fill('#ai-gen-dest','Nha Trang');
  await page.evaluate(()=>AIHub.handleGenerateDescription());
  assert(await page.locator('#ai-gen-result-box').isVisible());
  await page.evaluate(()=>AIHub.applyGeneratedToTourForm());
  await page.waitForURL('**/tours');
  await page.waitForFunction(()=>document.getElementById('tour-form-title')?.value==='Tour kiểm thử');
  assert.deepEqual(errors,[]);
  console.log('UI smoke passed: modals, sanitizer, 3 small viewports, navigation, 10 staff pages; no JS errors.');
  await browser.close();
})().catch(error=>{console.error(error);process.exit(1);});

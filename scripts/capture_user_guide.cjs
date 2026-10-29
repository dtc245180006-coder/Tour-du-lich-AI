const { chromium } = require('../.tools/node_modules/@playwright/test');
const fs = require('node:fs');
(async () => {
  const out = 'artifacts/user-guide/screenshots';
  fs.mkdirSync(out, {recursive:true});
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({viewport:{width:1440,height:980}, deviceScaleFactor:1});
  await page.route('https://**/*', route=>route.abort());
  async function shot(name) { await page.waitForTimeout(400); await page.screenshot({path:`${out}/${name}.png`}); }
  await page.goto('http://127.0.0.1:8011/home');
  await page.waitForFunction(()=>window.App && App.tours.length);
  await shot('01-home');
  await page.evaluate(()=>App.openGuestBookingModal());
  await shot('02-request');
  await page.evaluate(()=>App.closeModal('guest-booking-modal'));
  await page.evaluate(()=>App.openGuestTrackingModal());
  await shot('14-tracking');
  await page.goto('http://127.0.0.1:8011/login');
  await shot('03-login');
  await page.fill('#input-username','admin');
  await page.fill('#input-password','admin123');
  await page.click('#btn-submit-login');
  await page.waitForURL('**/home');
  for(const [i,tab] of ['tours','departures','queue','bookings','payments','guides','feedbacks','analytics','users','ai'].entries()) {
    await page.goto(`http://127.0.0.1:8011/${tab}`);
    await page.waitForFunction(()=>window.App && App.currentUser);
    await page.locator(`#view-${tab}`).waitFor({state:'visible'});
    await shot(`${String(i+4).padStart(2,'0')}-${tab}`);
    if(tab==='tours') {
      await page.evaluate(()=>App.openAddTourModal());
      await shot('15-create-tour');
    }
    if(tab==='departures') {
      await page.evaluate(()=>App.openDepartureCustomersModal(App.departures[0].id));
      await page.locator('#departure-customers-modal').waitFor({state:'visible'});
      await shot('16-customers');
    }
    if(tab==='feedbacks') {
      await page.evaluate(()=>App.openAddFeedbackModal());
      await shot('17-feedback-form');
    }
  }
  const info = await page.evaluate(()=>({title:document.title,role:App.currentUser.role}));
  fs.writeFileSync('artifacts/user-guide/capture.json',JSON.stringify(info,null,2));
  await browser.close();
  console.log('Captured 17 screenshots using isolated demo data.');
})().catch(e=>{console.error(e);process.exit(1)});

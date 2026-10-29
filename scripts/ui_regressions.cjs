const {chromium}=require('../.tools/node_modules/@playwright/test');
const assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch({headless:true});
  try {
    const page=await browser.newPage();
    const errors=[];page.on('pageerror',error=>errors.push(error.message));
    const base='http://127.0.0.1:8011';
    async function login(username,password){
      await page.goto(base+'/home');
      await page.evaluate(async({username,password})=>{
        const r=await fetch('/api/v1/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username,password})});
        const data=await r.json();localStorage.setItem('vietjourney_token',data.access_token);localStorage.setItem('vietjourney_user',JSON.stringify(data.user));
      },{username,password});
    }
    await login('admin','admin123');
    await page.goto(base+'/departures');await page.waitForFunction(()=>App.currentTab==='departures'&&App.tours.length);
    const money=await page.evaluate(async()=>{
      const headers={'Content-Type':'application/json',Authorization:`Bearer ${App.token}`};
      let r=await fetch('/api/v1/tours',{method:'POST',headers,body:JSON.stringify({code:'UI-REG-'+Date.now(),title:'Regression',destination:'Test',base_price:100001})});const tour=await r.json();
      r=await fetch('/api/v1/departures',{method:'POST',headers,body:JSON.stringify({tour_id:tour.id,departure_date:'2099-06-01',return_date:'2099-06-03',total_slots:5,price_override:0})});const dep=await r.json();
      await App.fetchInitialData();App.openEditDepartureModal(dep.id);
      const zero=document.getElementById('dep-form-price').value;
      const locked=document.getElementById('dep-form-tour-id').disabled;
      App.closeModal('departure-modal');
      await fetch(`/api/v1/departures/${dep.id}`,{method:'PUT',headers,body:JSON.stringify({price_override:null})});
      await App.fetchInitialData();App.openBookingModalForTour(tour.id);
      const amount=document.getElementById('modal-booking-initial-pay');
      const result={zero,locked,deposit:amount.value,valid:amount.checkValidity()};
      App.closeModal('booking-modal');
      App.openGuestBookingModal();alert('Old error');App.closeModal('guest-booking-modal');App.openGuestBookingModal();
      result.oldError=!!document.querySelector('#guest-booking-modal [data-form-error]');App.closeModal('guest-booking-modal');
      const pending=App.fetchInitialData();result.loadingHidden=document.getElementById('data-load-status').hidden;await pending;
      return result;
    });
    assert.equal(money.zero,'0');assert.equal(money.locked,true);
    assert.equal(money.deposit,'30000');assert.equal(money.valid,true);
    assert.equal(money.oldError,false);assert.equal(money.loadingHidden,false);
    await login('tuvan','tuvan123');await page.goto(base+'/bookings');
    await page.waitForFunction(()=>App.currentTab==='bookings'&&App.bookings.length);
    assert.equal(await page.locator('[data-action="openPaymentModal"]').count(),0);
    assert.deepEqual(errors,[]);
    console.log('UI regressions passed: integer deposit, zero price, locked tour, modal error reset, loading refresh, role-based payment.');
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exit(1)});

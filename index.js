function getUpdateTimes() {
  const lastUpdateEl = document.querySelector('h1[data-last-update]');
  const periodEl = document.querySelector('h1[data-update-period]');
  const nextUpdateEl = lastUpdateEl && periodEl ? lastUpdateEl + periodEl : null; // if needed, see note below

  const lastUpdate = Number(lastUpdateEl.dataset.lastUpdate);
  const period = Number(periodEl.dataset.updatePeriod);

  const hoursPerEpoch = 1 / (60 * 60);
  const now = Date.now() / 1000;

  const hoursSinceLast = (now - lastUpdate) * hoursPerEpoch;
  const nextUpdate = lastUpdate + period;
  const hoursUntilNext = (nextUpdate - now) * hoursPerEpoch;
  
  console.log(`Period: ${period}`);
  console.log(`Last Update: ${lastUpdate}`);
  console.log(`Now: ${now}`);
  console.log(`Now - Last Update: ${now - lastUpdate}`);
  console.log(`Next Update - Now: ${nextUpdate - now}`);

  document.getElementById('last-update').innerHTML =
    "Last Update: " + hoursSinceLast.toFixed(1) + "hrs ago";
  document.getElementById('next-update').innerHTML =
    "Next Update: " + hoursUntilNext.toFixed(1) + "hrs away";
}

document.addEventListener("DOMContentLoaded", () => {
  getUpdateTimes();
});

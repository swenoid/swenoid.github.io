const viewer = document.querySelector('#simulation-viewer');
const reset = document.querySelector('#reset-model-view');
const error = document.querySelector('#model-error');
const initialOrbit = viewer.getAttribute('camera-orbit');
let started = false;

function failed() {
  error.hidden = false;
  reset.disabled = true;
}
viewer.addEventListener('error', failed);
viewer.addEventListener('load', () => {
  error.hidden = true;
  reset.disabled = false;
});
reset.addEventListener('click', () => {
  viewer.cameraOrbit = initialOrbit;
  viewer.cameraTarget = 'auto auto auto';
  viewer.fieldOfView = '30deg';
  if (matchMedia('(prefers-reduced-motion: reduce)').matches) viewer.jumpCameraToGoal();
});

async function start() {
  if (started) return;
  started = true;
  try {
    await import('./assets/vendor/model-viewer/model-viewer.min.js');
  } catch {
    failed();
  }
}
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    if (entries.some(entry => entry.isIntersecting)) {
      observer.disconnect();
      start();
    }
  }, { rootMargin: '200px' });
  observer.observe(viewer);
} else {
  start();
}

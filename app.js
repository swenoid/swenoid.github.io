const gallery = document.querySelector('#videos');
const dialog = document.querySelector('#video-dialog');
const player = document.querySelector('#dialog-player');
const comparison = document.querySelector('#wave-comparison');
const wavePlayer = document.querySelector('#wave-player');
const waveIds = new Set(comparison.dataset.videoIds.split(' '));
let media = [];
let trigger = null;

// All five stages are encoded into one video, so play, seek, pause and loop
// always affect exactly the same frame in every stage.
const narrowScreen = window.matchMedia('(max-width: 700px)');
let layoutVersion = 0;
function chooseWaveLayout() {
  const layout = narrowScreen.matches ? 'mobile' : 'desktop';
  const source = `assets/videos/wave-comparison-${layout}.mp4`;
  if (wavePlayer.getAttribute('src') === source) return;
  const version = ++layoutVersion;
  const time = wavePlayer.currentTime || 0;
  const resume = !wavePlayer.paused && !wavePlayer.ended;
  wavePlayer.pause();
  wavePlayer.poster = `assets/posters/wave-comparison-${layout}.webp`;
  wavePlayer.preload = time || resume ? 'metadata' : 'none';
  wavePlayer.src = source;
  if (time || resume) {
    wavePlayer.addEventListener('loadedmetadata', () => {
      if (version !== layoutVersion) return;
      wavePlayer.currentTime = Math.min(time, Math.max(0, wavePlayer.duration - 0.02));
      if (resume) wavePlayer.play().catch(() => {});
    }, { once: true });
  }
  if (time || resume) wavePlayer.load();
}
chooseWaveLayout();
narrowScreen.addEventListener('change', chooseWaveLayout);
function openVideo(id, opener) {
  const item = media.find(video => video.id === id);
  if (!item) return;
  for (const video of document.querySelectorAll('.video-section video, #gallery video')) video.pause();
  trigger = opener;
  player.poster = item.poster;
  player.src = item.src;
  player.setAttribute('aria-label', item.title);
  dialog.showModal();
  document.body.classList.add('modal-open');
  player.play().catch(() => { /* Native controls remain available if autoplay is blocked. */ });
}

document.querySelector('#close-dialog').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', event => {
  if (event.target !== dialog) return;
  const rect = dialog.getBoundingClientRect();
  if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
});
dialog.addEventListener('close', () => {
  player.pause();
  player.removeAttribute('src');
  player.load();
  document.body.classList.remove('modal-open');
  trigger?.focus({ preventScroll: true });
});
document.addEventListener('click', event => {
  const button = event.target.closest('[data-video]');
  if (button && media.some(item => item.id === button.dataset.video)) {
    event.preventDefault();
    openVideo(button.dataset.video, button);
  }
});

try {
  const response = await fetch('media.json');
  if (!response.ok) throw new Error('Media index is unavailable.');
  media = await response.json();
  for (const item of media) {
    if (waveIds.has(item.id)) continue;
    const card = document.createElement('article');
    card.className = 'video-card';
    const video = document.createElement('video');
    video.controls = true;
    video.playsInline = true;
    video.preload = 'none';
    video.src = item.src;
    video.poster = item.poster;
    video.dataset.videoId = item.id;
    video.setAttribute('aria-label', item.title);
    card.append(video);
    const row = document.querySelector(`[data-video-group="${item.category}"]`);
    row.append(card);
  }
} catch (error) {
  const message = document.createElement('p');
  message.textContent = 'The gallery could not load. ';
  const fallback = document.createElement('a');
  fallback.href = 'video-index.html';
  fallback.textContent = 'Watch the videos.';
  message.append(fallback);
  gallery.append(message);
  console.error(error);
}

const tabs = Array.from(document.querySelectorAll('[data-experiment]'));
function selectTab(tab) {
  for (const item of tabs) {
    const active = item === tab;
    item.setAttribute('aria-selected', String(active));
    item.tabIndex = active ? 0 : -1;
    document.getElementById(item.getAttribute('aria-controls')).hidden = !active;
  }
}
tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectTab(tab));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index + tabs.length - 1) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    selectTab(tabs[next]);
    tabs[next].focus();
  });
});


const citation = document.querySelector('#bibtex');
const copyButton = document.querySelector('#copy-citation');
const copyStatus = document.querySelector('#copy-status');
copyButton.addEventListener('click', async () => {
  try {
    await navigator.clipboard.writeText(citation.textContent.trim());
    copyStatus.textContent = 'Copied to clipboard.';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(citation);
    selection.removeAllRanges();
    selection.addRange(range);
    copyStatus.textContent = 'Text selected. Press ⌘C or Ctrl+C to copy.';
  }
});

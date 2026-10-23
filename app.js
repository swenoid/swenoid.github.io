const grid = document.querySelector('#video-grid');
const filters = document.querySelector('#filters');
const count = document.querySelector('#video-count');
const dialog = document.querySelector('#video-dialog');
const player = document.querySelector('#dialog-player');
let media = [];
let trigger = null;

function duration(seconds) {
  const rounded = Math.round(seconds);
  return `${Math.floor(rounded / 60)}:${String(rounded % 60).padStart(2, '0')}`;
}

function openVideo(id, opener) {
  const item = media.find(video => video.id === id);
  if (!item) return;
  trigger = opener;
  document.querySelector('#dialog-title').textContent = item.title;
  document.querySelector('#dialog-setting').textContent = `${item.category} / ${item.setting}`;
  document.querySelector('#dialog-description').textContent = item.description;
  const download = document.querySelector('#download-video');
  download.href = item.src;
  download.download = `swenoid-${item.id}.mp4`;
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
  if (button) openVideo(button.dataset.video, button);
});

function filterVideos(category) {
  let visible = 0;
  for (const card of grid.children) {
    card.hidden = category !== 'All videos' && card.dataset.category !== category;
    if (!card.hidden) visible++;
  }
  for (const button of filters.children) button.setAttribute('aria-pressed', String(button.dataset.category === category));
  count.textContent = `${visible} ${visible === 1 ? 'video' : 'videos'}`;
}

try {
  const response = await fetch('media.json');
  if (!response.ok) throw new Error('Media index is unavailable.');
  media = await response.json();
  for (const category of ['All videos', 'Locomotion', 'Motion tracking', 'Imitation', 'Manipulation', 'Retargeting']) {
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.category = category;
    button.textContent = category;
    button.addEventListener('click', () => filterVideos(category));
    filters.append(button);
  }
  for (const item of media) {
    const card = document.createElement('article');
    card.className = 'video-card';
    card.dataset.category = item.category;
    const button = document.createElement('button');
    button.type = 'button';
    button.dataset.video = item.id;
    button.setAttribute('aria-label', `Play ${item.title}, ${duration(item.duration)}`);
    const thumb = document.createElement('span');
    thumb.className = 'video-thumb';
    const image = document.createElement('img');
    image.src = item.poster;
    image.alt = '';
    image.loading = 'lazy';
    image.width = item.width;
    image.height = item.height;
    const play = document.createElement('span');
    play.className = 'thumb-play';
    play.textContent = '▶';
    play.setAttribute('aria-hidden', 'true');
    const time = document.createElement('span');
    time.className = 'duration';
    time.textContent = duration(item.duration);
    const category = document.createElement('span');
    category.className = 'video-category';
    category.textContent = `${item.category} / ${item.setting}`;
    const title = document.createElement('h3');
    title.textContent = item.title;
    thumb.append(image, play, time);
    button.append(thumb, category, title);
    card.append(button);
    grid.append(card);
  }
  filterVideos('All videos');
} catch (error) {
  const message = document.createElement('p');
  message.textContent = 'The gallery could not load. ';
  const fallback = document.createElement('a');
  fallback.href = 'video-index.html';
  fallback.textContent = 'Watch videos in the complete index.';
  message.append(fallback);
  grid.append(message);
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

document.querySelector('#copy-citation').addEventListener('click', async () => {
  const text = document.querySelector('#bibtex').textContent;
  const status = document.querySelector('#copy-status');
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = 'Citation copied.';
  } catch {
    const selection = window.getSelection();
    const range = document.createRange();
    range.selectNodeContents(document.querySelector('#bibtex'));
    selection.removeAllRanges();
    selection.addRange(range);
    status.textContent = 'Citation selected. Use your device’s copy command.';
  }
});

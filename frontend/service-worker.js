// Bump this whenever the caching strategy changes - the activate handler
// deletes every cache that doesn't match, which purges stale assets.
const CACHE_NAME = 'bharathashetra-v3';

// Only genuinely static, versioned-by-content assets belong here.
const PRECACHE = [
  '/icons/icon-192.png',
  '/icons/apple-touch-icon.png',
  '/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(PRECACHE))
      .catch(err => console.log('Precache skipped (non-critical):', err))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(names =>
      Promise.all(names.filter(n => n !== CACHE_NAME).map(n => caches.delete(n)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const { request } = event;

  if (request.method !== 'GET') return;

  let url;
  try {
    url = new URL(request.url);
  } catch (e) {
    return;
  }

  // Never cache API traffic. These responses are authenticated and
  // time-sensitive (payment status, attendance) - a stale hit would show a
  // parent the wrong balance, and the entries would linger on shared devices.
  if (url.pathname.startsWith('/api/')) return;

  // App shell: always network-first so a deploy reaches parents immediately.
  // This must cover "/" as well as *.html - the previous version only checked
  // for ".html", so "/" was served cache-first and users could stay pinned to
  // an old build indefinitely.
  const isAppShell =
    request.mode === 'navigate' ||
    url.pathname === '/' ||
    url.pathname.endsWith('.html');

  if (isAppShell) {
    event.respondWith(
      fetch(request)
        .then(response => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(c => c.put(request, copy)).catch(() => {});
          return response;
        })
        .catch(() =>
          caches.match(request).then(
            cached => cached || caches.match('/') ||
              new Response(
                '<h1 style="font-family:sans-serif;padding:2rem">You are offline</h1>' +
                '<p style="font-family:sans-serif;padding:0 2rem">Reconnect to load the portal.</p>',
                { status: 503, headers: { 'Content-Type': 'text/html' } }
              )
          )
        )
    );
    return;
  }

  // Static assets (icons, fonts, css/js): cache-first, refresh in background.
  event.respondWith(
    caches.match(request).then(cached => {
      const network = fetch(request)
        .then(response => {
          if (response && response.status === 200 && response.type !== 'error') {
            const copy = response.clone();
            caches.open(CACHE_NAME).then(c => c.put(request, copy)).catch(() => {});
          }
          return response;
        })
        .catch(() => cached);

      return cached || network;
    })
  );
});

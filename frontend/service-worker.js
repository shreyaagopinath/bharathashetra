const CACHE_NAME = 'bharathashetra-v1';
const URLS_TO_CACHE = [
  '/',
  '/index.html',
  '/login.html'
];

// Install event - cache essential files
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(URLS_TO_CACHE).catch(err => {
        console.log('Cache install error (non-critical):', err);
        // Don't fail installation if some files can't be cached
      });
    })
  );
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch event - network first, fall back to cache
self.addEventListener('fetch', event => {
  const { request } = event;

  // Skip non-GET requests and API calls (let them handle themselves)
  if (request.method !== 'GET') {
    return;
  }

  // For API requests, try network first
  if (request.url.includes('/api/')) {
    event.respondWith(
      fetch(request)
        .then(response => {
          if (response.ok) {
            const cache = caches.open(CACHE_NAME);
            cache.then(c => c.put(request, response.clone()));
          }
          return response;
        })
        .catch(() => {
          // If offline, try to return cached version
          return caches.match(request).then(cached => {
            return cached || new Response('Offline - API unavailable', { status: 503 });
          });
        })
    );
    return;
  }

  // For HTML/static files, use cache first strategy
  event.respondWith(
    caches.match(request).then(cached => {
      return cached || fetch(request)
        .then(response => {
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          const cache = caches.open(CACHE_NAME);
          cache.then(c => c.put(request, response.clone()));
          return response;
        })
        .catch(() => {
          return caches.match(request) || new Response('Offline - Page unavailable', { status: 503 });
        });
    })
  );
});

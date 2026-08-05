const CACHE_NAME = 'bharathashetra-v2';
const URLS_TO_CACHE = [
  '/'
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
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then(c => c.put(request, responseClone));
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

  // Skip caching HTML files (always fetch fresh)
  if (request.url.includes('.html')) {
    event.respondWith(fetch(request));
    return;
  }

  // For other static files, use cache first strategy
  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;

      return fetch(request)
        .then(response => {
          if (!response || response.status !== 200 || response.type === 'error') {
            return response;
          }
          // Clone and cache
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(c => c.put(request, responseClone));
          return response;
        })
        .catch(() => {
          return caches.match(request) || new Response('Offline', { status: 503 });
        });
    })
  );
});

// SERVICE WORKER VERSION 2.0 - FORCE UPDATE
const CACHE_VERSION = 'v2.0-production';
const CACHE_NAME = `crm-fusion-${CACHE_VERSION}`;

// Install: Skip waiting to activate immediately
self.addEventListener('install', (event) => {
  console.log(`[SW ${CACHE_VERSION}] Installing - forcing immediate activation`);
  self.skipWaiting();
});

// Activate: Clear all old caches
self.addEventListener('activate', (event) => {
  console.log(`[SW ${CACHE_VERSION}] Activating - clearing old caches`);
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log(`[SW ${CACHE_VERSION}] Deleting old cache:`, cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log(`[SW ${CACHE_VERSION}] Claiming all clients`);
      return self.clients.claim();
    })
  );
});

// Fetch: Network-first strategy for all requests - NO CACHING
self.addEventListener('fetch', (event) => {
  // ALWAYS fetch from network, never use cache
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Clone the response before returning
        return response;
      })
      .catch(error => {
        console.error(`[SW ${CACHE_VERSION}] Fetch failed:`, error);
        // Return a basic offline page or error response
        return new Response('Offline - Please check your internet connection', {
          status: 503,
          statusText: 'Service Unavailable',
          headers: new Headers({
            'Content-Type': 'text/plain'
          })
        });
      })
  );
});

// Message handler for force update
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    console.log(`[SW ${CACHE_VERSION}] Received SKIP_WAITING message`);
    self.skipWaiting();
  }
});

console.log(`[SW ${CACHE_VERSION}] Service Worker loaded`);

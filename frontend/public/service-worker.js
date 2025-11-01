const CACHE_VERSION = 'v1.0.5';
const CACHE_NAME = `ecj-trainer-${CACHE_VERSION}`;

// Assets que se cachean (imágenes, fonts, etc)
const STATIC_CACHE = `${CACHE_NAME}-static`;
// Páginas y API que siempre deben ser frescas
const DYNAMIC_CACHE = `${CACHE_NAME}-dynamic`;

const STATIC_ASSETS = [
  '/manifest.json',
  '/icon.svg',
  '/ecj_icon.svg'
];

// Install - cachea assets estáticos
self.addEventListener('install', (event) => {
  console.log('[SW] Installing new version:', CACHE_VERSION);
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting()) // Activa inmediatamente
  );
});

// Activate - limpia cachés viejos
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating new version:', CACHE_VERSION);
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // Borra cualquier caché que no sea de la versión actual
          if (cacheName.startsWith('ecj-trainer-') && cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim()) // Toma control inmediato
  );
});

// Fetch - estrategia inteligente
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Para API calls: SIEMPRE red primero (datos frescos)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request)
        .catch(() => new Response(JSON.stringify({ error: 'Sin conexión' }), {
          headers: { 'Content-Type': 'application/json' }
        }))
    );
    return;
  }

  // Para HTML: Network first, cache fallback
  if (request.headers.get('accept').includes('text/html')) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          // Cachea la nueva versión
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
          return response;
        })
        .catch(() => {
          // Si falla, usa caché
          return caches.match(request);
        })
    );
    return;
  }

  // Para assets estáticos (CSS, JS, imágenes): Cache first, network fallback
  event.respondWith(
    caches.match(request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          // Actualiza caché en segundo plano
          fetch(request).then((response) => {
            caches.open(STATIC_CACHE).then((cache) => {
              cache.put(request, response);
            });
          }).catch(() => {});
          return cachedResponse;
        }
        
        return fetch(request).then((response) => {
          // Cachea para próxima vez
          const responseClone = response.clone();
          caches.open(STATIC_CACHE).then((cache) => {
            cache.put(request, responseClone);
          });
          return response;
        });
      })
  );
});

// Mensaje para actualizar
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});

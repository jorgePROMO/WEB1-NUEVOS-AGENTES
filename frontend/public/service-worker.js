// Service Worker DESACTIVADO TEMPORALMENTE para debugging
self.addEventListener('install', (event) => {
  console.log('Service Worker DESACTIVADO - modo debugging');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker activado en modo debugging (sin cache)');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          console.log('Eliminando cache:', cacheName);
          return caches.delete(cacheName);
        })
      );
    }).then(() => self.clients.claim())
  );
});

// NO INTERCEPTAR NADA - dejar que todo pase directo
self.addEventListener('fetch', (event) => {
  // NO hacer nada - dejar pasar todos los requests
  return;
});

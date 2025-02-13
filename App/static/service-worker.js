const CACHE_NAME = 'meteo-cache-v1';
const urlsToCache = [
  '/',
  '/static/style.css',
  '/static/icons/cloudy_192.png',
  '/static/icons/cloudy_512.png'
];

// Lors de l'installation du service worker, on ajoute les fichiers à mettre en cache
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Lors de la récupération de ressources, on sert les fichiers du cache si disponibles
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((cachedResponse) => {
        if (cachedResponse) {
          return cachedResponse;
        }
        return fetch(event.request);
      })
  );
});

// Lors de la mise à jour du service worker, on supprime les anciens caches
self.addEventListener('activate', (event) => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (!cacheWhitelist.includes(cacheName)) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

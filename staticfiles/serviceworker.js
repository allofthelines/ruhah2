const CACHE_NAME = 'myapp-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/styles.css',
  '/static/js/scripts.js',
  '/static/offline.html',  // Add offline page to cache
  // add other URLs you want to cache
];

// Install event - caching the offline page
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serving the offline page when offline
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request).catch(() => {
      return caches.match(event.request)
        .then(response => {
          if (response) {
            return response;
          } else if (event.request.mode === 'navigate') {
            return caches.match('/static/offline.html');
          }
        });
    })
  );
});

const CACHE_NAME = 'myapp-cache-v1';
const urlsToCache = [
  '/',
  '/static/css/styles.css',
  '/static/js/scripts.js',
  '/offline/',  // Update to the correct offline URL served by Django
  // add other URLs you want to cache
];

// Install event - caching the offline page and other resources
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
            // Serve the offline page from the cache when navigating
            return caches.match('/offline/');
          }
        });
    })
  );
});
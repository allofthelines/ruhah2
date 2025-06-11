const CACHE_NAME = 'ruhah-cache-v1';
const urlsToCache = [
  '/',  // Cache the home page
  '/offline/',  // Offline page URL oxi to offline.html stoo static/ alla afto sto templates
  // Direct URLs to the static files at the root level
  // ta evala etsi giati gamimeno to static sta settings des bugs.txt
  'https://ruhahbucket.s3.amazonaws.com/core/styles.css',
  'https://ruhahbucket.s3.amazonaws.com/core/scripts.js',
  'https://ruhahbucket.s3.amazonaws.com/manifest.json',
];

// Install event - caching the offline page and other assets
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
            return caches.match('/offline/');
          }
        });
    })
  );
});
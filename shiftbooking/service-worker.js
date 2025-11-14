const CACHE_NAME = "shiftbooking-cache-v2";


const urlsToCache = [
  "/schedule/",
  "/static/css/schedule.css",

  "/static/shifts/manifest.json",
  "/static/shifts/icons/shiftbooking-192.png",
  "/static/shifts/icons/shiftbooking-512.png",
];



self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(urlsToCache);
    })
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.map(key => key !== CACHE_NAME && caches.delete(key)))
    )
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

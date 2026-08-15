const CACHE_NAME = "aqi-tracker-v1";

const FILES_TO_CACHE = [
    "/",
    "/static/style.css",
    "/static/manifest.json",
    "/static/icon.png"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => {
            return cache.addAll(FILES_TO_CACHE);
        })
    );
});

self.addEventListener("fetch", event => {
    event.respondWith(
        fetch(event.request).catch(() => caches.match(event.request))
    );
});

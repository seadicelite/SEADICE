var C='memo-v1';
self.addEventListener('install',function(e){e.waitUntil(caches.open(C).then(function(c){return c.addAll(['/memo/','/memo/manifest.json','/memo/icon-192.png'])}));self.skipWaiting()});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(k){return Promise.all(k.filter(function(n){return n!==C}).map(function(n){return caches.delete(n)}))}));self.clients.claim()});
self.addEventListener('fetch',function(e){var r=e.request;if(r.method!=='GET'||new URL(r.url).origin!==location.origin)return;e.respondWith(fetch(r).then(function(res){if(res.ok){var cp=res.clone();caches.open(C).then(function(c){c.put(r,cp)})}return res}).catch(function(){return caches.match(r,{ignoreSearch:true})}))});

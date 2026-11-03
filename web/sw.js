/* 전자전 재밍 시연 — 서비스 워커
 *
 * VERSION 줄은 도구/빌드.py 가 web/ 내용의 해시로 다시 써 넣는다.
 * 손으로 고치지 말 것. 내용이 바뀌면 버전이 바뀌고, 옛 캐시는 activate 에서 지워진다.
 *
 * 화면(navigate)은 네트워크 우선 — 다시 배포하면 바로 새 내용이 보이고,
 * 인터넷이 없을 때만 캐시에서 꺼낸다. 나머지 파일은 캐시 우선.
 */
const VERSION = '2e5ea18c';
const CACHE = 'ea-jam-' + VERSION;

const ASSETS = [
  './',
  './index.html',
  './01-comms.html',
  './02-gnss.html',
  './03-ppi.html',
  './04-sar.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png'
];

self.addEventListener('install', (e) => {
  e.waitUntil(
    caches.open(CACHE)
      .then((c) => c.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

function put(req, res) {
  const copy = res.clone();
  caches.open(CACHE).then((c) => c.put(req, copy)).catch(() => {});
  return res;
}

self.addEventListener('fetch', (e) => {
  const req = e.request;
  if (req.method !== 'GET') return;

  // 화면 이동: 네트워크 우선 → 실패하면 캐시 → 그것도 없으면 시작 화면
  if (req.mode === 'navigate') {
    e.respondWith(
      fetch(req)
        .then((res) => put(req, res))
        .catch(() => caches.match(req).then((r) => r || caches.match('./index.html')))
    );
    return;
  }

  // 같은 출처(아이콘·manifest 등): 캐시 우선
  if (new URL(req.url).origin === location.origin) {
    e.respondWith(
      caches.match(req).then((r) => r || fetch(req).then((res) => put(req, res)))
    );
    return;
  }

  // 외부(Google Fonts): 네트워크 우선, 실패하면 캐시. 글꼴이 없어도 페이지는 동작한다.
  e.respondWith(
    fetch(req).then((res) => put(req, res)).catch(() => caches.match(req))
  );
});

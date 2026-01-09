import http from "k6/http";
import { check, sleep } from "k6";

const BASE_URL = __ENV.LOAD_BASE_URL || "http://localhost:8080/api/v1";
const TELEGRAM_ID = __ENV.LOAD_TELEGRAM_ID || "446409091";
const SYMBOLS = ["btc", "eth", "sol", "xrp", "bnb", "usdt", "ada", "doge"];

export const options = {
  stages: [
    { duration: "30s", target: 50 },
    { duration: "4m", target: 50 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_failed: ["rate<0.05"],
    http_req_duration: ["p(95)<1500"],
  },
};

function pickSymbol() {
  return SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
}

export default function () {
  const headers = { "X-Telegram-ID": TELEGRAM_ID };
  const symbol = pickSymbol();
  const favSymbol = `LT${__VU}${__ITER}`.toUpperCase().slice(0, 10);

  let res = http.get(`${BASE_URL}/currencies?limit=50`);
  check(res, { "currencies ok": (r) => r.status === 200 });

  res = http.get(`${BASE_URL}/currencies/${symbol}`);
  check(res, { "currency ok": (r) => r.status === 200 });

  res = http.get(`${BASE_URL}/currencies/${symbol}/history?days=7`);
  check(res, { "history ok": (r) => r.status === 200 });

  res = http.get(`${BASE_URL}/portfolio`, { headers });
  check(res, { "portfolio ok": (r) => r.status === 200 || r.status === 404 });

  res = http.get(`${BASE_URL}/portfolio/stats`, { headers });
  check(res, { "stats ok": (r) => r.status === 200 });

  res = http.post(
    `${BASE_URL}/favorites`,
    JSON.stringify({ currency_symbol: favSymbol }),
    { headers: { ...headers, "Content-Type": "application/json" } }
  );
  check(res, { "favorite create ok": (r) => [200, 201].includes(r.status) });

  res = http.get(`${BASE_URL}/favorites`, { headers });
  check(res, { "favorites ok": (r) => r.status === 200 });

  res = http.del(`${BASE_URL}/favorites/${favSymbol}`, null, { headers });
  check(res, { "favorite delete ok": (r) => r.status === 200 });

  sleep(1);
}

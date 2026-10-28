// Runs inside the Uptime Kuma container, called by the host's homelab-site-stats.
// Prints the up/down heartbeat totals of all active monitors over the last 30 days as JSON.
// Opens Kuma's SQLite database read-only; uses the @louislam/sqlite3 module bundled with Kuma.
// Run: NODE_PATH=/opt/uptime-kuma/node_modules node kuma-uptime.js
"use strict";
const sqlite3 = require("@louislam/sqlite3");
const DB = process.env.KUMA_DB || "/opt/uptime-kuma/data/kuma.db";
const DAY = 86400;
const today = Math.floor(Date.now() / 1000 / DAY) * DAY;
const from = today - 29 * DAY;

const db = new sqlite3.Database(DB, sqlite3.OPEN_READONLY, (err) => {
  if (err) { console.log(JSON.stringify({ error: "open: " + err.message })); process.exit(0); }
  db.get(
    `SELECT COALESCE(SUM(s.up),0) AS up, COALESCE(SUM(s.down),0) AS down,
            MIN(s.timestamp) AS first_day,
            (SELECT COUNT(*) FROM monitor WHERE active = 1) AS monitors
       FROM stat_daily s JOIN monitor m ON m.id = s.monitor_id
      WHERE m.active = 1 AND s.timestamp >= ?`,
    [from],
    (err2, row) => {
      if (err2) console.log(JSON.stringify({ error: "query: " + err2.message }));
      else console.log(JSON.stringify(row));
      db.close();
    }
  );
});

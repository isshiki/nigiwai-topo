// Export the public fixed-condition peaks using the same name resolver as the map.
const fs = require('node:fs'), path = require('node:path'), vm = require('node:vm');
const assert = require('node:assert/strict'), crypto = require('node:crypto');
const root = process.argv[2] || 'data/distribution/foursquare-world-v6';
const out = process.argv[3] || 'exports/world-2026-09-15';
const context = vm.createContext({window: {}, area: {value: 'world'}, URL});
for (const name of ['japanese-names', 'world-japanese-names', 'world-name-overrides', 'world-reviewed-names', 'world-display-names', 'world-coordinate-names', 'unnamed-world-peak-names', 'world-peak-locality-names', 'world-station-peak-names', 'peak-quality']) {
  vm.runInContext(fs.readFileSync(`web/${name}.js`, 'utf8'), context);
}
const app = fs.readFileSync('web/app.js', 'utf8');
const start = app.indexOf('function applyPeakLocalityNames('), end = app.indexOf('const dataRoot');
assert(start >= 0 && end > start, 'Map resolver must be available');
vm.runInContext(app.slice(start, end) + ';this.resolve={applyPeakLocalityNames,peakName};', context);
const manifest = JSON.parse(fs.readFileSync(path.join(root, 'manifest.json'), 'utf8'));
const rows = [], seen = new Set(), representatives = new Map();
let total = 0;
for (const entry of manifest.packages) {
  const raw = JSON.parse(fs.readFileSync(path.join(root, entry.id, '200-all-peaks.json'), 'utf8')).features;
  total += raw.length;
  const named = context.resolve.applyPeakLocalityNames(raw);
  for (const f of named) {
    const p = f.properties;
    if (p.kind !== 'peak' || p.density < 800 || !context.window.nigiwaiPeakAllowed(f, 'world')) continue;
    const [lon, lat] = f.geometry.coordinates, name = context.resolve.peakName(p);
    assert(Number.isFinite(p.density) && Number.isFinite(lon) && Number.isFinite(lat));
    assert(lon >= -180 && lon <= 180 && lat >= -90 && lat <= 90);
    assert(name && !/付近|地名未登録/.test(name));
    assert(!/^[=+\-@\t\r]/.test(name), 'Unsafe spreadsheet cell');
    const coordinateKey = `${lon},${lat}`;
    assert(!seen.has(coordinateKey), 'Duplicate peak coordinate');
    seen.add(coordinateKey);
    const row = {name, density: p.density, lat, lon};
    rows.push(row);
    const prior = representatives.get(name);
    if (!prior || prior.density < row.density) representatives.set(name, row);
  }
}
const compare = (a, b) => b.density - a.density || a.lon - b.lon || a.lat - b.lat;
const cell = value => '"' + String(value).replace(/"/g, '""') + '"';
fs.mkdirSync(out, {recursive: true});
const files = [];
for (const [file, values] of [['world-peaks.csv', rows], ['world-place-representatives.csv', [...representatives.values()]]]) {
  values.sort(compare);
  const csv = '\ufeff地名,登録密度_件_per_km2,緯度,経度\r\n' + values.map(r => [r.name, r.density, r.lat, r.lon].map(cell).join(',')).join('\r\n') + '\r\n';
  const target = path.join(out, file);
  fs.writeFileSync(target, csv, 'utf8');
  files.push({file, rows: values.length, bytes: fs.statSync(target).size, sha256: crypto.createHash('sha256').update(fs.readFileSync(target)).digest('hex')});
}
const metadata = {snapshot: '2026-09-15', source: 'Foursquare OS Places', build: path.basename(root), category: 'all', sigma_m: 200, minimum_density_per_km2: 800, scanned_peaks: total, columns: ['地名', '登録密度_件_per_km2', '緯度', '経度'], coordinate_reference_system: 'WGS84 / EPSG:4326', representative_rule: 'Maximum density per map display name across the entire dataset; viewport representatives may differ.', files};
fs.writeFileSync(path.join(out, 'metadata.json'), JSON.stringify(metadata, null, 2) + '\n');
console.log(JSON.stringify(metadata));

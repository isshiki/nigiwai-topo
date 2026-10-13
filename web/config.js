// Public map data via existing CloudFront; S3 remains private.
window.NIGIWAI_CONFIG = {
  worldOnly: true,
  referenceIndex: 'https://re.masahiko.info/nigiwai-topo/world/2026-09-15-radius2/reference-index/index.json',
  dataBase: 'https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/',
  worldRaster: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
  areas: {
    // Immutable v6: validated density holds, delivered through CloudFront.
    world: {name:'世界（200m・すべて）',center:[0,20],dataBase:'https://re.masahiko.info/nigiwai-topo/world/2026-09-15-v6/'},
    'sg-singapore': {name:'シンガポール周辺（試作）',center:[103.82,1.35],dataBase:'https://re.masahiko.info/nigiwai-topo/pilots/sg-singapore/2026-09-15-v1/'},
    'gb-london': {name:'ロンドン周辺（試作）',center:[-.12,51.5],dataBase:'https://re.masahiko.info/nigiwai-topo/pilots/gb-london/2026-09-15-v1/'},
    'is-reykjavik': {name:'レイキャビク周辺（試作）',center:[-21.9,64.13],dataBase:'https://re.masahiko.info/nigiwai-topo/pilots/is-reykjavik/2026-09-15-v1/'}
  }
};

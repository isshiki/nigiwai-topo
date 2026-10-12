/* Exact viewport top-k: descend at edges, use summaries only inside the view. */
window.nigiwaiViewBoxes = bounds => {
  const west=bounds.getWest(),east=bounds.getEast(),south=bounds.getSouth(),north=bounds.getNorth();
  const norm=x=>((x+180)%360+360)%360-180;
  const w=norm(west),e=norm(east);
  return east-west>=360?[[-180,south,180,north]]:w<=e?[[w,south,e,north]]:[[w,south,180,north],[-180,south,e,north]];
};
window.nigiwaiContainsPoint = (bounds,point) => window.nigiwaiViewBoxes(bounds).some(([w,s,e,n])=>point[0]>=w&&point[0]<=e&&point[1]>=s&&point[1]<=n);
window.NigiwaiPeakIndex = class {
  constructor(root, index, read) {this.root = root; this.index = index; this.read = read; this.cache = new Map(); this.active=0; this.waiting=[];}
  async fetchNode(url) {
    if (this.active >= 4) await new Promise(resolve=>this.waiting.push(resolve));
    else this.active++;
    try {return await this.read(url);}
    finally {if(this.waiting.length) this.waiting.shift()(); else this.active--;}
  }
  async node(id) {
    if (!this.cache.has(id)) {
      const request = this.fetchNode(new URL(this.index.node_file_template.replace('{id}', id), this.root).href);
      this.cache.set(id, request);
      request.catch(() => this.cache.delete(id));
      if (this.cache.size > 128) this.cache.delete(this.cache.keys().next().value);
    }
    return this.cache.get(id) || this.fetchNode(new URL(this.index.node_file_template.replace('{id}', id), this.root).href);
  }
  async query(bbox, floor = 800, limit = 100, eligible = () => true, groupKey = null) {
    if (limit < 1 || limit > this.index.summary_limit) throw Error('峰索引の検索件数が範囲外です');
    const result = [];
    const [west,south,east,north] = bbox;
    const visit = async id => {
      const node = await this.node(id);
      const [a,b,c,d] = node.bbox;
      if (c < west || a > east || d < south || b > north) return;
      const contained = west <= a && c <= east && south <= b && d <= north;
      // A filtered summary must contain enough eligible entries; otherwise
      // descend to find lower-ranked replacements omitted from its top list.
      const eligibleTop=node.top?.filter(eligible) || [];
      const distinctTop=groupKey ? new Set(eligibleTop.map(groupKey)).size : eligibleTop.length;
      const summarySafe = !node.features && contained && (distinctTop >= limit || node.top.length < this.index.summary_limit);
      if (node.features || summarySafe) {
        for (const f of (node.features || node.top)) {
          const [lon,lat] = f.geometry.coordinates;
          if (lon >= west && lon <= east && lat >= south && lat <= north && f.properties.density >= floor && eligible(f)) result.push(f);
        }
      } else {
        // The shared fetch queue limits network requests to four.
        await Promise.all(node.children.map(visit));
      }
    };
    if (this.index.root !== null) await visit(this.index.root);
    const sorted=result.sort((a,b) => b.properties.density-a.properties.density);
    if(!groupKey)return sorted.slice(0,limit);
    const seen=new Set();
    return sorted.filter(f=>{const key=groupKey(f);if(seen.has(key))return false;seen.add(key);return true;}).slice(0,limit);
  }
};

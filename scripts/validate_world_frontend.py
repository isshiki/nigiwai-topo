"""Validate merged overview, manifest references, and complete global peak index."""
import argparse,gzip,json
from pathlib import Path
import mapbox_vector_tile as mvt
from pmtiles.reader import Reader,MmapSource,all_tiles
ROOT=Path('data/distribution/foursquare-world')
def main():
    global ROOT
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--report',type=Path,default=Path('data/validation/world-frontend.json'))
    args=parser.parse_args();ROOT=args.root
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    assert len(manifest['packages'])==2947
    index=json.loads((ROOT/'world-peak-index/index.json').read_text())
    count=0
    for i in range(index['node_count']):
        node=json.loads((ROOT/f'world-peak-index/{i}.json').read_text(encoding='utf-8'))
        if 'features' in node:count+=len(node['features'])
    assert count==index['count']==manifest['datasets'][0]['peaks']==json.loads((ROOT/'validation.json').read_text())['peaks']
    zooms={};tiles=0
    with (ROOT/'overview.pmtiles').open('rb') as f:
        source=MmapSource(f);reader=Reader(source)
        assert reader.header()['min_zoom']==0 and reader.header()['max_zoom']==8
        for (z,x,y),payload in all_tiles(source):
            features=mvt.decode(gzip.decompress(payload))['density']['features']
            assert all(p['properties']['kind']=='band' and p['properties']['density']>=800 for p in features)
            zooms[z]=zooms.get(z,0)+1;tiles+=1
        assert tiles==reader.header()['addressed_tiles_count']
    assert set(zooms)==set(range(9))
    for p in manifest['packages']:assert (ROOT/p['pmtiles']).is_file()
    report={'complete':True,'overview_tiles':tiles,'zooms':zooms,'overview_bytes':(ROOT/'overview.pmtiles').stat().st_size,'peak_count':count,'index_nodes':index['node_count']}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2))
    print(report)
if __name__=='__main__':main()

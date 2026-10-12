"""Extract active passenger station references from a pinned OSM country PBF."""
import hashlib,json
from pathlib import Path
import osmium
from world_names import station_candidate,reference_records
ROOT=Path('data/raw/world-names/kr-stations')
class Stations(osmium.SimpleHandler):
    def __init__(self):super().__init__();self.elements=[]
    def node(self,n):
        if n.tags.get('railway') not in ('station','halt') and n.tags.get('public_transport')!='station':return
        tags=dict(n.tags)
        if station_candidate(tags) and n.location.valid():self.elements.append({'type':'node','id':n.id,'lon':n.location.lon,'lat':n.location.lat,'tags':tags})
    def way(self,w):
        if w.tags.get('railway') not in ('station','halt') and w.tags.get('public_transport')!='station':return
        tags=dict(w.tags)
        if not station_candidate(tags):return
        coords=[(n.lon,n.lat) for n in w.nodes if n.location.valid()]
        if coords:self.elements.append({'type':'way','id':w.id,'center':{'lon':sum(p[0] for p in coords)/len(coords),'lat':sum(p[1] for p in coords)/len(coords)},'tags':tags})
def main():
    path=ROOT/'south-korea.osm.pbf';handler=Stations();handler.apply_file(str(path),locations=True,idx='flex_mem',filters=[osmium.filter.TagFilter(('railway','station'),('railway','halt'))])
    ROOT.joinpath('station-elements.json').write_text(json.dumps(handler.elements,ensure_ascii=False),encoding='utf-8')
    stations,_=reference_records(handler.elements)
    ROOT.joinpath('stations.json').write_text(json.dumps(stations,ensure_ascii=False,indent=2),encoding='utf-8')
    ROOT.joinpath('manifest.json').write_text(json.dumps({'source_url':'https://download.geofabrik.de/asia/south-korea-latest.osm.pbf','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'license':'OpenStreetMap / ODbL 1.0','elements':len(handler.elements),'stations':len(stations)},indent=2),encoding='utf-8')
    print(json.dumps({'stations':len(stations),'japanese':sum(s['name_key']=='name:ja' for s in stations)}))
if __name__=='__main__':main()

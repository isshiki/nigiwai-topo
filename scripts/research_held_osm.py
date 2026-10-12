"""Bounded, cached public OSM facility lookup for two remaining campus/camp peaks."""
import json,urllib.request,urllib.parse
from pathlib import Path
def main():
    items={}
    for key,lat,lon in [('phayao',19.0314,99.8901),('ridge-camp',-4.1085,137.1006)]:
        path=Path('data/name-research')/('held-osm-'+key+'.json')
        if path.exists():continue
        query=f'[out:json][timeout:25];nwr(around:3000,{lat},{lon})[name];out center tags;'
        request=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':query}).encode(),headers={'User-Agent':'NigiwaiTopo bounded place-name research'})
        try:
            with urllib.request.urlopen(request,timeout=40) as response:result=json.load(response)
            path.write_text(json.dumps({'query':query,'endpoint':request.full_url,'license':'ODbL; OpenStreetMap contributors','result':result},ensure_ascii=False,indent=2),encoding='utf-8')
            print(key,len(result['elements']),flush=True)
        except Exception as exc:print(key,type(exc).__name__,flush=True)
if __name__=='__main__':main()

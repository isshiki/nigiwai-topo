"""Upload only frontend-required world files to a new versioned S3 prefix."""
import argparse,json,subprocess,urllib.request,shutil
from pathlib import Path
ROOT=Path('data/distribution/foursquare-world');STAGE=Path('data/world-release')
PREFIX='nigiwai-topo/world/2026-09-15-v1/';BASE='https://re.masahiko.info/'+PREFIX
def aws(*args):
    r=subprocess.run(['aws',*args,'--profile','nigiwai-topo','--output','json'],check=True,capture_output=True,text=True,encoding='utf-8');return json.loads(r.stdout or '{}')
def main():
    global ROOT,STAGE,PREFIX,BASE
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--stage',type=Path,default=STAGE)
    parser.add_argument('--prefix',default=PREFIX)
    parser.add_argument('--frontend-report',type=Path,default=Path('data/validation/world-frontend.json'))
    parser.add_argument('--report',type=Path,default=Path('data/validation/world-published.json'))
    args=parser.parse_args();ROOT=args.root;STAGE=args.stage;PREFIX=args.prefix
    import re
    if not re.fullmatch(r'nigiwai-topo/world/[a-zA-Z0-9-]+/',PREFIX):raise ValueError('Invalid world release prefix')
    BASE='https://re.masahiko.info/'+PREFIX
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    assert json.loads((ROOT/'validation.json').read_text())['complete']
    frontend=json.loads(args.frontend_report.read_text())
    assert frontend['complete'] and frontend['overview_bytes']==(ROOT/'overview.pmtiles').stat().st_size
    expected={'manifest.json','regions.json','stations.json','overview.pmtiles','Foursquare-NOTICE.txt','Apache-2.0.txt','World-Names-NOTICE.txt','OSM-NOTICE.txt'}
    if manifest.get('density_quality'):expected.add(manifest['density_quality']['notice_file'])
    expected.update(p['pmtiles'] for p in manifest['packages'])
    expected.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'world-peak-index').glob('*.json'))
    for name in sorted(expected):
        dest=STAGE/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
    assert aws('sts','get-caller-identity')['Account']=='207364224120'
    existing=aws('s3api','list-objects-v2','--bucket','remasahiko','--prefix',PREFIX,'--max-keys','1')
    if existing.get('KeyCount',0):raise RuntimeError('Release prefix occupied; do not overwrite')
    print('Uploading',len(expected),'files',sum((STAGE/n).stat().st_size for n in expected),'bytes',flush=True)
    subprocess.run(['aws','s3','sync',str(STAGE),'s3://remasahiko/'+PREFIX,'--profile','nigiwai-topo','--region','ap-northeast-1','--no-progress','--only-show-errors'],check=True)
    contents=aws('s3api','list-objects-v2','--bucket','remasahiko','--prefix',PREFIX).get('Contents',[])
    actual={p['Key'][len(PREFIX):]:p['Size'] for p in contents}
    assert set(actual)==expected
    assert all(actual[n]==(STAGE/n).stat().st_size for n in expected)
    for name in ['manifest.json','world-peak-index/index.json','overview.pmtiles',manifest['packages'][0]['pmtiles']]:
        headers={'Origin':'https://example.github.io'}
        if name.endswith('.pmtiles'):headers['Range']='bytes=0-126'
        with urllib.request.urlopen(urllib.request.Request(BASE+name,headers=headers),timeout=60) as r:
            assert r.headers.get('Access-Control-Allow-Origin')=='*'
            if name.endswith('.pmtiles'):assert r.status==206 and r.read()[:7]==b'PMTiles'
            else:assert json.load(r)==json.loads((STAGE/name).read_text(encoding='utf-8'))
    with urllib.request.urlopen(urllib.request.Request(BASE+'overview.pmtiles',method='OPTIONS',headers={'Origin':'https://example.github.io','Access-Control-Request-Method':'GET','Access-Control-Request-Headers':'range,if-match'})) as r:
        assert r.status in (200,204) and r.headers.get('Access-Control-Allow-Origin')=='*'
        assert 'range' in r.headers.get('Access-Control-Allow-Headers','').lower()
    report={'complete':True,'files':len(expected),'bytes':sum(actual.values()),'base':BASE,'range_cors_verified':True}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2))
    print(report,flush=True)
if __name__=='__main__':main()

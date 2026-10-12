"""Validate and upload a versioned map release, verify CDN, then package Pages.

CloudFront/CORS setup is separate; this command never changes AWS policies.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import urllib.request


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--profile',default='nigiwai-topo')
    parser.add_argument('--bucket',default='remasahiko')
    parser.add_argument('--prefix',required=True,help='Versioned prefix, e.g. nigiwai-topo/japan/2026-09-15-v2/')
    parser.add_argument('--data-url',required=True,help='CloudFront HTTPS URL ending with /')
    parser.add_argument('--upload',action='store_true',help='Without this flag, print the plan only')
    parser.add_argument('--input',type=Path,default=Path('data/distribution/foursquare-japan'))
    parser.add_argument('--original',type=Path,default=Path('web/data/foursquare-japan'))
    parser.add_argument('--skip-package',action='store_true',help='Multiple-region releases package the frontend separately')
    args=parser.parse_args()
    if not args.prefix.startswith('nigiwai-topo/') or not args.prefix.endswith('/') or '..' in args.prefix:
        raise SystemExit('Use a release prefix below nigiwai-topo/, ending with /')
    if not args.data_url.startswith('https://') or not args.data_url.endswith('/'):
        raise SystemExit('Use an HTTPS data URL ending with /')
    source=args.input
    manifest=json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    expected={'manifest.json','stations.json','regions.json','Foursquare-NOTICE.txt','Apache-2.0.txt'}
    if manifest.get('reference_names'):
        expected.update(['places.json','OSM-NOTICE.txt'])
    for item in manifest['datasets']:
        expected.update([item['pmtiles_file'],item['peaks_file']])
        if item.get('peaks_index'):
            expected.add(item['peaks_index'])
            index_path=source/item['peaks_index']
            index=json.loads(index_path.read_text(encoding='utf-8'))
            expected.update(str((Path(item['peaks_index']).parent/index['node_file_template'].replace('{id}',str(i))).as_posix()) for i in range(index['node_count']))
    assert len(manifest['datasets']) in (9,12)
    assert {p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()}==expected
    print('Release:',len(expected),'files,',sum((source/n).stat().st_size for n in expected),'bytes')
    print('Destination:',f's3://{args.bucket}/{args.prefix}')
    if not args.upload:
        print('Plan only. Add --upload to execute.')
        return
    validation=[sys.executable,'scripts/validate_pmtiles.py','--input',str(source),'--original',str(args.original)]
    subprocess.run(validation,check=True)
    def aws(*command):
        result=subprocess.run(['aws',*command,'--profile',args.profile,'--output','json'],check=True,capture_output=True,text=True,encoding='utf-8')
        return json.loads(result.stdout) if result.stdout.strip() else {}
    assert aws('sts','get-caller-identity')['Account']=='207364224120'
    occupied=aws('s3api','list-objects-v2','--bucket',args.bucket,'--prefix',args.prefix,'--max-keys','1')
    if occupied.get('KeyCount',0):
        raise SystemExit('Release prefix already exists. Choose a new version to avoid stale caches and overwrites.')
    subprocess.run(['aws','s3','sync',str(source),f's3://{args.bucket}/{args.prefix}',
                    '--profile',args.profile,'--region','ap-northeast-1','--no-progress'],check=True)
    listing=aws('s3api','list-objects-v2','--bucket',args.bucket,'--prefix',args.prefix)
    uploaded={o['Key'][len(args.prefix):]:o['Size'] for o in listing.get('Contents',[])}
    assert set(uploaded)==expected
    for name in sorted(expected):
        assert uploaded[name]==(source/name).stat().st_size, name
    with urllib.request.urlopen(urllib.request.Request(args.data_url+'manifest.json',headers={'Origin':'https://example.github.io'})) as response:
        assert response.headers.get('Access-Control-Allow-Origin')=='*'
        assert json.load(response)==manifest
    preflight=urllib.request.Request(args.data_url+manifest['datasets'][0]['pmtiles_file'],method='OPTIONS',headers={
        'Origin':'https://example.github.io','Access-Control-Request-Method':'GET',
        'Access-Control-Request-Headers':'range,if-match'})
    with urllib.request.urlopen(preflight) as response:
        assert response.status in (200,204)
        assert response.headers.get('Access-Control-Allow-Origin')=='*'
        allowed=response.headers.get('Access-Control-Allow-Headers','').lower()
        assert 'range' in allowed and 'if-match' in allowed
    subprocess.run(validation+['--http-base',args.data_url],check=True)
    if not args.skip_package:
        subprocess.run([sys.executable,'scripts/package_pages.py','--data-url',args.data_url],check=True)
    print('Upload and CDN verification succeeded; '+('frontend packaging skipped.' if args.skip_package else 'Pages package prepared.')+' GitHub deployment is separate.')


if __name__ == '__main__':
    main()

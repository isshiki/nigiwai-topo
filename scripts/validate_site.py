"""Validate the deployable static site without raw data or third-party packages."""
import argparse
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.references = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        for key in ('src', 'href'):
            if key in attrs:
                self.references.append(attrs[key])


def validate(root):
    root = root.resolve()
    checked = 0
    for name in ('index.html', 'about.html', 'station-tier.html'):
        page = Page()
        page.feed((root / name).read_text(encoding='utf-8'))
        assert len(page.ids) == len(set(page.ids)), f'Duplicate IDs in {name}'
        for reference in page.references:
            url = urlsplit(reference)
            if url.scheme or url.netloc:
                assert url.scheme in ('https', 'mailto'), reference
                continue
            target = (root / unquote(url.path or name)).resolve()
            assert target.is_relative_to(root), reference
            if target.is_dir():
                target /= 'index.html'
            assert target.is_file(), f'Missing local link: {reference}'
            checked += 1
    config = (root / 'config.js').read_text(encoding='utf-8')
    assert 'worldOnly: true' in config
    assert 'https://re.masahiko.info/nigiwai-topo/world/' in config
    assert not re.search(r'localhost|127\.0\.0\.1', config)
    files = [p for p in root.rglob('*') if p.is_file()]
    assert not any(p.suffix in ('.pmtiles', '.parquet', '.pem', '.key')
                   or p.name.startswith('.env') for p in files)
    return {'complete': True, 'files': len(files),
            'bytes': sum(p.stat().st_size for p in files), 'local_links': checked}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    print(json.dumps(validate(parser.parse_args().root)))

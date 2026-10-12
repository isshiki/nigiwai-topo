"""Local Pages + external tile-storage equivalent, supporting HTTP byte ranges."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re

WEB = Path('web').resolve()
STORAGE = Path('data/distribution').resolve()


class Handler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        if path.split('?')[0].startswith('/tiles/'):
            suffix = path.split('?')[0][len('/tiles/'):]
            target = (STORAGE/suffix).resolve()
            if not target.is_relative_to(STORAGE):
                return str(STORAGE/'missing')
            return str(target)
        return super().translate_path(path)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Expose-Headers', 'ETag, Content-Range, Accept-Ranges')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Methods','GET, HEAD, OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Range, If-Match')
        self.end_headers()

    def send_head(self):
        self.remaining = None
        path = Path(self.translate_path(self.path))
        if not path.is_file() or not self.path.split('?')[0].endswith('.pmtiles'):
            return super().send_head()
        stat = path.stat()
        size = stat.st_size
        etag = f'"{stat.st_mtime_ns:x}-{size:x}"'
        if self.headers.get('If-Match') not in (None, '*', etag):
            self.send_error(412)
            return None
        start, end = 0, size-1
        if self.headers.get('Range'):
            match = re.fullmatch(r'bytes=(\d*)-(\d*)',self.headers['Range'])
            if not match or not any(match.groups()):
                self.send_error(416)
                return None
            a,b = match.groups()
            if not a:
                start=max(0,size-int(b))
            else:
                start=int(a)
                end=min(size-1,int(b)) if b else size-1
            if start> end or start>=size:
                self.send_response(416)
                self.send_header('Content-Range',f'bytes */{size}')
                self.send_header('Content-Length','0')
                self.end_headers()
                return None
        self.send_response(206 if self.headers.get('Range') else 200)
        self.send_header('Content-Type','application/octet-stream')
        self.send_header('Accept-Ranges','bytes')
        self.send_header('ETag',etag)
        self.send_header('Content-Length',str(end-start+1))
        if self.headers.get('Range'):
            self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
        self.end_headers()
        stream=path.open('rb')
        stream.seek(start)
        self.remaining=end-start+1
        return stream

    def copyfile(self, source, outputfile):
        if self.remaining is None:
            return super().copyfile(source,outputfile)
        while self.remaining:
            chunk=source.read(min(65536,self.remaining))
            if not chunk:
                break
            outputfile.write(chunk)
            self.remaining-=len(chunk)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--port',type=int,default=8820)
    args=parser.parse_args()
    ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(WEB))).serve_forever()

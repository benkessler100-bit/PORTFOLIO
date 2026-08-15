#!/usr/bin/env python3
"""Static server that answers HTTP Range requests.

python -m http.server ignores Range and replies 200 with the whole file, so a
browser can only ever play a video from the start — the scrub bar looks alive
but seeking does nothing. GitHub Pages does support Range, so this only affects
local preview; it still has to work locally or you cannot test playback.
"""
import os, re, sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

class RangeHandler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        rng = self.headers.get("Range")
        if not rng:
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)\s*$", rng)
        if not m:
            return super().send_head()
        try:
            f = open(path, "rb")
        except OSError:
            self.send_error(404, "File not found")
            return None
        size = os.fstat(f.fileno()).st_size
        start, end = m.group(1), m.group(2)
        if start == "":                        # suffix range: last N bytes
            length = int(end)
            start = max(0, size - length)
            end = size - 1
        else:
            start = int(start)
            end = int(end) if end else size - 1
        end = min(end, size - 1)
        if start > end or start >= size:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            f.close()
            return None
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        f.seek(start)
        self._range_left = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        left = getattr(self, "_range_left", None)
        if left is None:
            return super().copyfile(source, outputfile)
        self._range_left = None
        while left > 0:
            chunk = source.read(min(64 * 1024, left))
            if not chunk:
                break
            try:
                outputfile.write(chunk)
            except (BrokenPipeError, ConnectionResetError):
                break                          # the browser seeked away
            left -= len(chunk)

    def end_headers(self):
        if "Accept-Ranges" not in self._headers_buffer_str():
            self.send_header("Accept-Ranges", "bytes")
        super().end_headers()

    def _headers_buffer_str(self):
        return b"".join(getattr(self, "_headers_buffer", [])).decode("latin-1", "replace")

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8013
    root = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    os.chdir(root)
    print("serving %s on http://localhost:%d (Range enabled, threaded)" % (root, port))
    # Threaded on purpose: a single-threaded server handles one request at a
    # time, so a video streaming its range response blocks every image queued
    # behind it and half the page appears not to load.
    srv = ThreadingHTTPServer(("127.0.0.1", port), RangeHandler)
    srv.daemon_threads = True
    srv.serve_forever()

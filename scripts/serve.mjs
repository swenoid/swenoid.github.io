// Local preview server with byte-range support for seeking through videos.
import http from 'node:http';
import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../', import.meta.url));
const port = Number(process.env.SWENOID_PORT || 4173);
const mime = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.json': 'application/json; charset=utf-8', '.webp': 'image/webp', '.png': 'image/png', '.svg': 'image/svg+xml', '.mp4': 'video/mp4', '.glb': 'model/gltf-binary', '.md': 'text/plain; charset=utf-8' };
const server = http.createServer(async (req, res) => {
  try {
    if (!['GET', 'HEAD'].includes(req.method)) {
      res.writeHead(405, { Allow: 'GET, HEAD' }).end();
      return;
    }
    const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
    if (pathname.split('/').some(part => part.startsWith('.'))) throw new Error('Not found');
    const filename = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
    if (!filename.startsWith(root)) throw new Error('Not found');
    const info = await stat(filename);
    if (!info.isFile()) throw new Error('Not found');
    const headers = { 'Content-Type': mime[path.extname(filename)] || 'application/octet-stream', 'Accept-Ranges': 'bytes', 'Cache-Control': 'no-cache' };
    let start = 0, end = info.size - 1, code = 200;
    if (req.headers.range) {
      const range = /^bytes=(\d*)-(\d*)$/.exec(req.headers.range);
      if (!range || (!range[1] && !range[2])) {
        res.writeHead(416, { 'Content-Range': `bytes */${info.size}` }).end();
        return;
      }
      if (range[1]) {
        start = Number(range[1]);
        end = range[2] ? Math.min(Number(range[2]), info.size - 1) : info.size - 1;
      } else start = Math.max(0, info.size - Number(range[2]));
      if (start > end || start >= info.size || !Number.isSafeInteger(start) || !Number.isSafeInteger(end)) {
        res.writeHead(416, { 'Content-Range': `bytes */${info.size}` }).end();
        return;
      }
      code = 206;
      headers['Content-Range'] = `bytes ${start}-${end}/${info.size}`;
    }
    headers['Content-Length'] = info.size ? end - start + 1 : 0;
    res.writeHead(code, headers);
    if (req.method === 'HEAD' || !info.size) res.end();
    else {
      const stream = createReadStream(filename, { start, end });
      stream.on('error', () => res.destroy());
      res.on('close', () => stream.destroy());
      stream.pipe(res);
    }
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Not found');
  }
});
server.listen(port, '127.0.0.1', () => console.log(`Swenoid local preview: http://localhost:${port}`));
server.on('error', error => { console.error(error.message); process.exitCode = 1; });

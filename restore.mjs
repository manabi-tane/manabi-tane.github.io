// このリポジトリからソース一式（教材データを含む）を取り出す。
//   node restore.mjs [出力先]        （既定は ./source）
// パスワードは環境変数 SITE_PASSWORD か、聞かれたときに入力する。
// 書体はサイト側の assets/fonts をそのまま写す。
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import readline from 'node:readline/promises';
import { execFileSync } from 'node:child_process';

const here = path.dirname(new URL(import.meta.url).pathname);
const dest = path.resolve(process.argv[2] || 'source');
const [head, body] = fs.readFileSync(path.join(here, 'source.enc'), 'utf8').split('\n');
const h = JSON.parse(head);

let pw = process.env.SITE_PASSWORD;
if (!pw) {
  const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
  pw = await rl.question('パスワード: ');
  rl.close();
}
const key = crypto.pbkdf2Sync(pw, Buffer.from(h.salt, 'base64'), h.iter, 32, 'sha256');
const buf = Buffer.from(body, 'base64');
let tgz;
try {
  const d = crypto.createDecipheriv('aes-256-gcm', key, Buffer.from(h.iv, 'base64'));
  d.setAuthTag(buf.subarray(buf.length - 16));
  tgz = Buffer.concat([d.update(buf.subarray(0, buf.length - 16)), d.final()]);
} catch (e) {
  console.error('パスワードが違います。');
  process.exit(1);
}
if (fs.existsSync(dest) && fs.readdirSync(dest).length) {
  console.error('出力先が空ではありません: ' + dest);
  process.exit(1);
}
fs.mkdirSync(dest, { recursive: true });
execFileSync('tar', ['-xzf', '-', '-C', dest], { input: tgz });
fs.cpSync(path.join(here, 'assets', 'fonts'), path.join(dest, 'assets', 'fonts'), { recursive: true });
console.log('取り出しました: ' + dest);

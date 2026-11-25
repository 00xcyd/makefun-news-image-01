// The World, 25 November 2026.
//
// This program ships one ready-made newspaper poster beside itself and copies it,
// byte for byte, to the grader's output directory. Before copying, it checks that
// the file is a whole PNG or JPEG: correct magic, valid dimensions, a complete
// chunk/segment stream with its end marker, and at most 1 MiB and 1024x1024.
// A broken build fails with a clear message and a non-zero exit.
//
// Locally:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { join } from 'node:path';

const LIMIT = 1024 * 1024;
const MAX_SIDE = 1024;
const source = new URL('./entry.png', import.meta.url);

type Kind = 'png' | 'jpeg';
type Size = { width: number; height: number };

function fail(message: string): never {
  console.error(`entry refused: ${message}`);
  process.exit(1);
}

function readSource(): Buffer {
  try {
    return readFileSync(source);
  } catch (error) {
    fail(`cannot read entry.png: ${(error as Error).message}`);
  }
}

function kindOf(bytes: Buffer): Kind | null {
  if (
    bytes.length >= 8 &&
    bytes[0] === 0x89 &&
    bytes[1] === 0x50 &&
    bytes[2] === 0x4e &&
    bytes[3] === 0x47 &&
    bytes[4] === 0x0d &&
    bytes[5] === 0x0a &&
    bytes[6] === 0x1a &&
    bytes[7] === 0x0a
  ) {
    return 'png';
  }
  if (bytes.length >= 2 && bytes[0] === 0xff && bytes[1] === 0xd8) {
    return 'jpeg';
  }
  return null;
}

// PNG's CRC-32, computed here so the check needs nothing but the standard library.
const CRC_TABLE = (() => {
  const table = new Uint32Array(256);
  for (let n = 0; n < 256; n += 1) {
    let c = n;
    for (let k = 0; k < 8; k += 1) {
      c = (c & 1) === 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    }
    table[n] = c >>> 0;
  }
  return table;
})();

function crc32(bytes: Buffer, start: number, end: number): number {
  let c = 0xffffffff;
  for (let i = start; i < end; i += 1) {
    c = CRC_TABLE[(c ^ bytes[i]) & 0xff] ^ (c >>> 8);
  }
  return (c ^ 0xffffffff) >>> 0;
}

function pngSize(bytes: Buffer): Size {
  let offset = 8;
  let size: Size | null = null;
  let sawData = false;

  while (offset + 12 <= bytes.length) {
    const length = bytes.readUInt32BE(offset);
    if (length > 0x7fffffff) fail('PNG chunk length is out of range');
    const type = bytes.toString('ascii', offset + 4, offset + 8);
    const dataStart = offset + 8;
    const dataEnd = dataStart + length;
    const end = dataEnd + 4;
    if (end > bytes.length) fail(`PNG chunk ${type} is truncated`);

    const stored = bytes.readUInt32BE(dataEnd);
    const actual = crc32(bytes, offset + 4, dataEnd);
    if (stored !== actual) fail(`PNG chunk ${type} fails its checksum`);

    if (!size) {
      if (type !== 'IHDR' || length !== 13) fail('PNG does not begin with a 13-byte IHDR chunk');
      size = {
        width: bytes.readUInt32BE(dataStart),
        height: bytes.readUInt32BE(dataStart + 4),
      };
    } else if (type === 'IDAT') {
      sawData = true;
    } else if (type === 'IEND') {
      if (length !== 0) fail('PNG IEND chunk is not empty');
      if (end !== bytes.length) fail('PNG has bytes after its IEND chunk');
      if (!sawData) fail('PNG has no image data chunk');
      return size;
    }

    offset = end;
  }

  fail('PNG is missing its IEND chunk');
}

function jpegSize(bytes: Buffer): Size {
  if (bytes.length < 4 || bytes[bytes.length - 2] !== 0xff || bytes[bytes.length - 1] !== 0xd9) {
    fail('JPEG does not end with its EOI marker');
  }

  const sof = new Set([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]);
  let offset = 2;
  let size: Size | null = null;

  while (offset < bytes.length) {
    if (bytes[offset] !== 0xff) fail('JPEG has a malformed marker');
    while (offset < bytes.length && bytes[offset] === 0xff) offset += 1;
    if (offset >= bytes.length) fail('JPEG ends inside a marker');
    const marker = bytes[offset];
    offset += 1;

    if (marker === 0xd9) {
      if (offset !== bytes.length) fail('JPEG has bytes after its EOI marker');
      break;
    }
    if (marker === 0xd8 || marker === 0x01 || (marker >= 0xd0 && marker <= 0xd7)) {
      continue;
    }
    if (offset + 2 > bytes.length) fail('JPEG segment is truncated');
    const length = bytes.readUInt16BE(offset);
    if (length < 2 || offset + length > bytes.length) fail('JPEG segment length is invalid');
    if (sof.has(marker)) {
      if (length < 7) fail('JPEG frame header is too short');
      size = {
        height: bytes.readUInt16BE(offset + 3),
        width: bytes.readUInt16BE(offset + 5),
      };
    }
    if (marker === 0xda) {
      // The scan data is entropy-coded; the EOI check above is the whole-file test.
      break;
    }
    offset += length;
  }

  if (!size) fail('JPEG has no frame header with its dimensions');
  return size;
}

const bytes = readSource();
const kind = kindOf(bytes);
if (!kind) fail('bytes are neither PNG nor JPEG');
if (bytes.length > LIMIT) fail(`${bytes.length} bytes exceeds the 1 MiB limit`);

const size = kind === 'png' ? pngSize(bytes) : jpegSize(bytes);
if (size.width < 1 || size.height < 1) fail('image dimensions are zero');
if (size.width > MAX_SIDE || size.height > MAX_SIDE) {
  fail(`${size.width}x${size.height} exceeds ${MAX_SIDE}x${MAX_SIDE}`);
}

const outputDir = process.env.MAKEFUN_OUTPUT_DIR || '/output';
mkdirSync(outputDir, { recursive: true });
const target = join(outputDir, 'entry.png');
copyFileSync(source, target);
const copied = statSync(target);
if (copied.size !== bytes.length) {
  fail(`copy is ${copied.size} bytes, expected ${bytes.length}`);
}

const digest = createHash('sha256').update(bytes).digest('hex');
console.log(
  `entry.png: ${copied.size} bytes, ${size.width}x${size.height}, ` +
    `${kind.toUpperCase()}, sha256 ${digest}`,
);

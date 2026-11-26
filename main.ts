// SPDX-License-Identifier: MIT
// THE WORLD — 25 November 2026. Entry shipper for make.fun's one-image
// news bounty.
//
// The deliverable is a single picture: the poster kept in entry.png beside
// this file. The grader runs this program in a sandbox that holds the
// repository read-only and hands it one writable output directory, so the
// entry's whole job is to prove the picture is exactly what the rules
// demand and then copy it, byte for byte:
//
//   * a PNG or a JPEG, told apart by its first bytes;
//   * a whole image: a PNG whose stream closes with its IEND chunk, or a
//     JPEG whose stream closes with its EOI marker;
//   * no larger than 1024 pixels on a side;
//   * no heavier than 1,048,576 bytes.
//
// Anything else is refused with a clear message and a non-zero exit. Run it
// the same way the grader does:
//
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import * as fs from "node:fs";
import * as nodePath from "node:path";
import { createHash } from "node:crypto";

const HEAVIEST = 1048576;
const LONGEST_EDGE = 1024;
const SOURCE = new URL("./entry.png", import.meta.url);
const TARGET_DIR = process.env["MAKEFUN_OUTPUT_DIR"] ?? "/output";

const PNG_SIGNATURE = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
const PNG_CLOSER = Buffer.from([0x49, 0x45, 0x4e, 0x44, 0xae, 0x42, 0x60, 0x82]);
const JPEG_FRAME_MARKERS = new Set([0xc0, 0xc1, 0xc2, 0xc3, 0xc5, 0xc6, 0xc7, 0xc9, 0xca, 0xcb, 0xcd, 0xce, 0xcf]);

type Picture = { format: "png" | "jpeg"; width: number; height: number };

function refuse(detail: string): never {
  process.stderr.write(`entry.png does not meet the bounty's rules: ${detail}\n`);
  process.exit(1);
}

function readPngSize(buf: Buffer): Picture {
  // The first chunk of a PNG is always IHDR: width and height, four bytes each.
  if (buf.subarray(12, 16).toString("latin1") !== "IHDR" || buf.readUInt32BE(8) !== 13) {
    refuse("the PNG's first chunk is not a well-formed IHDR");
  }
  return { format: "png", width: buf.readUInt32BE(16), height: buf.readUInt32BE(20) };
}

function readJpegSize(buf: Buffer): Picture {
  // Walk the JPEG's segments until a frame header names the image's size.
  let at = 2;
  while (at + 10 < buf.length) {
    if (buf[at] !== 0xff) {
      at += 1;
      continue;
    }
    const marker = buf[at + 1];
    if (JPEG_FRAME_MARKERS.has(marker)) {
      return { format: "jpeg", width: buf.readUInt16BE(at + 7), height: buf.readUInt16BE(at + 5) };
    }
    at += 2 + buf.readUInt16BE(at + 2);
  }
  refuse("the JPEG stream carries no frame header naming its size");
}

function inspect(buf: Buffer): Picture {
  if (buf.length >= 24 && buf.subarray(0, 8).equals(PNG_SIGNATURE)) {
    if (!buf.subarray(buf.length - 8).equals(PNG_CLOSER)) {
      refuse("the PNG stream does not close with its IEND chunk");
    }
    return readPngSize(buf);
  }
  if (buf.length >= 4 && buf[0] === 0xff && buf[1] === 0xd8) {
    if (!(buf[buf.length - 2] === 0xff && buf[buf.length - 1] === 0xd9)) {
      refuse("the JPEG stream does not close with its EOI marker");
    }
    return readJpegSize(buf);
  }
  refuse("the file is neither a PNG nor a JPEG");
}

function main(): void {
  const bytes = fs.readFileSync(SOURCE);
  if (bytes.length === 0) {
    refuse("the file is empty");
  }
  if (bytes.length > HEAVIEST) {
    refuse(`the file weighs ${bytes.length} bytes, over the ${HEAVIEST}-byte limit`);
  }
  const picture = inspect(bytes);
  if (picture.width > LONGEST_EDGE || picture.height > LONGEST_EDGE) {
    refuse(`the image measures ${picture.width}x${picture.height}, past the ${LONGEST_EDGE}-pixel limit`);
  }
  fs.mkdirSync(TARGET_DIR, { recursive: true });
  const target = nodePath.join(TARGET_DIR, "entry.png");
  fs.writeFileSync(target, bytes);
  const sha256 = createHash("sha256").update(bytes).digest("hex");
  process.stdout.write(
    `entry.png: ${picture.format} ${picture.width}x${picture.height}, ${bytes.length} bytes, sha256 ${sha256}, written to ${target}\n`,
  );
}

main();

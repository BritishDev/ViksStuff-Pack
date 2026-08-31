import { createHash } from "node:crypto";
import { readFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const sharp = require("sharp");

const repositoryRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const sourceRoot = resolve(repositoryRoot, "source-art", "rps");
const outputRoot = resolve(
  repositoryRoot,
  "overlay",
  "assets",
  "viksstuff",
  "textures",
  "item",
);

const icons = [
  ["rock", "rps-rock-imagegen-original.png"],
  ["paper", "rps-paper-imagegen-original.png"],
  ["scissors", "rps-scissors-imagegen-original.png"],
];

const outputSize = 64;
const transparentPadding = 4;
const contentSize = outputSize - transparentPadding * 2;
const transparent = { r: 0, g: 0, b: 0, alpha: 0 };

for (const [name, sourceName] of icons) {
  const sourcePath = resolve(sourceRoot, sourceName);
  const outputPath = resolve(outputRoot, `rps_${name}.png`);
  const sourceBytes = await readFile(sourcePath);
  const metadata = await sharp(sourceBytes).metadata();

  if (metadata.format !== "png" || metadata.channels !== 4 || !metadata.hasAlpha) {
    throw new Error(`${sourceName} must be an RGBA PNG with an alpha channel`);
  }

  const { data: sourcePixels, info: sourceInfo } = await sharp(sourceBytes)
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });
  let sourceTransparentPixels = 0;
  let sourceVisiblePixels = 0;
  for (let offset = 3; offset < sourcePixels.length; offset += sourceInfo.channels) {
    if (sourcePixels[offset] === 0) {
      sourceTransparentPixels += 1;
    } else {
      sourceVisiblePixels += 1;
    }
  }
  if (sourceTransparentPixels === 0 || sourceVisiblePixels === 0) {
    throw new Error(`${sourceName} must contain both transparent and visible pixels`);
  }

  const trimmed = await sharp(sourceBytes)
    .ensureAlpha()
    .trim({ background: transparent, threshold: 0 })
    .toBuffer();

  await sharp(trimmed)
    .resize(contentSize, contentSize, {
      fit: "contain",
      kernel: sharp.kernel.nearest,
      background: transparent,
    })
    .extend({
      top: transparentPadding,
      bottom: transparentPadding,
      left: transparentPadding,
      right: transparentPadding,
      background: transparent,
    })
    .png({
      compressionLevel: 9,
      adaptiveFiltering: false,
      palette: false,
    })
    .toFile(outputPath);

  const outputBytes = await readFile(outputPath);
  const outputMetadata = await sharp(outputBytes).metadata();
  const { data, info } = await sharp(outputBytes)
    .ensureAlpha()
    .raw()
    .toBuffer({ resolveWithObject: true });
  let transparentPixels = 0;
  let visiblePixels = 0;

  for (let offset = 3; offset < data.length; offset += info.channels) {
    if (data[offset] === 0) {
      transparentPixels += 1;
    } else {
      visiblePixels += 1;
    }
  }

  if (
    outputMetadata.width !== outputSize ||
    outputMetadata.height !== outputSize ||
    !outputMetadata.hasAlpha ||
    transparentPixels === 0 ||
    visiblePixels === 0
  ) {
    throw new Error(`Generated rps_${name}.png failed output validation`);
  }

  console.log(
    JSON.stringify({
      icon: name,
      sourceSha256: createHash("sha256").update(sourceBytes).digest("hex"),
      sourceTransparentPixels,
      sourceVisiblePixels,
      outputSha256: createHash("sha256").update(outputBytes).digest("hex"),
      width: outputMetadata.width,
      height: outputMetadata.height,
      transparentPixels,
      visiblePixels,
    }),
  );
}

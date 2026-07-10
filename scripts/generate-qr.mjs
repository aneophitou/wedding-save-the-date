import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import QRCode from "qrcode";

const __dirname = dirname(fileURLToPath(import.meta.url));
const rootDir = join(__dirname, "..");
const outputDir = join(rootDir, "site", "assets");
const url = "https://wedding.neophitou.com";

const options = {
  errorCorrectionLevel: "M",
  margin: 2,
  width: 1024,
  color: {
    dark: "#5c543f",
    light: "#fbfbf3",
  },
};

const svg = await QRCode.toString(url, { ...options, type: "svg" });
const pngBuffer = await QRCode.toBuffer(url, { ...options, type: "png" });

writeFileSync(join(outputDir, "qr-code.svg"), svg, "utf8");
writeFileSync(join(outputDir, "qr-code.png"), pngBuffer);

console.log(`QR code generated for ${url}`);
console.log("  site/assets/qr-code.svg");
console.log("  site/assets/qr-code.png");

import { access, readFile, readdir, stat } from "node:fs/promises";
import { constants } from "node:fs";
import path from "node:path";

const dist = path.resolve("dist");
const indexPath = path.join(dist, "index.html");

await access(indexPath, constants.R_OK);
const html = await readFile(indexPath, "utf8");

if (!html.includes('<div id="root"></div>')) {
  throw new Error("Production index.html is missing the React root element");
}

const assetsDir = path.join(dist, "assets");
const assets = await readdir(assetsDir);
const javascript = assets.filter((file) => file.endsWith(".js"));
const stylesheets = assets.filter((file) => file.endsWith(".css"));

if (javascript.length === 0) {
  throw new Error("Production bundle contains no JavaScript asset");
}

for (const file of [...javascript, ...stylesheets]) {
  const fileStat = await stat(path.join(assetsDir, file));
  if (fileStat.size === 0) {
    throw new Error(`Production asset is empty: ${file}`);
  }
}

console.log(
  `Production bundle verified: ${javascript.length} JavaScript and ${stylesheets.length} CSS assets`,
);

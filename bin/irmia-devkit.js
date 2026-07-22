#!/usr/bin/env node
"use strict";

const path = require("path");
const { spawn, spawnSync } = require("child_process");

const launcher = path.join(__dirname, "irmia-devkit.py");
const probe = "import sys;raise SystemExit(0 if sys.version_info >= (3,10) else 1)";
const candidates = process.platform === "win32"
  ? [["py", ["-3"]], ["python", []], ["python3", []]]
  : [["python3", []], ["python", []]];

let selected = null;
for (const [command, prefix] of candidates) {
  const result = spawnSync(command, [...prefix, "-c", probe], { stdio: "ignore" });
  if (result.status === 0) {
    selected = [command, prefix];
    break;
  }
}

if (!selected) {
  console.error("[irmia-devkit] Error: Python >= 3.10 not found. Install: https://python.org");
  process.exit(1);
}

const [command, prefix] = selected;
const child = spawn(command, [...prefix, launcher, ...process.argv.slice(2)], { stdio: "inherit" });
child.on("error", (error) => {
  console.error(`[irmia-devkit] Error: ${error.message}`);
  process.exit(1);
});
child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
  } else {
    process.exit(code === null ? 1 : code);
  }
});

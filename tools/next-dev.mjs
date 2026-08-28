import { spawn } from "node:child_process";

const forwardedArgs = [];

for (const argument of process.argv.slice(2)) {
  if (argument === "--host") {
    forwardedArgs.push("--hostname");
    continue;
  }

  if (argument === "--strictPort") {
    continue;
  }

  forwardedArgs.push(argument);
}

const nextDev = spawn(
  process.execPath,
  ["node_modules/next/dist/bin/next", "dev", ...forwardedArgs],
  { stdio: "inherit" },
);

for (const signal of ["SIGINT", "SIGTERM"]) {
  process.on(signal, () => nextDev.kill(signal));
}

nextDev.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }

  process.exit(code ?? 1);
});

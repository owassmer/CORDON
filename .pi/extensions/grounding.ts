/**
 * The coordinator holds CORDON's constitution, whole, in its system prompt, as it stands on origin/main.
 *
 * A local checkout is a working copy; origin/main is the source of truth (AGENTS.md). A coordinator grounded in its
 * checkout can stand far behind it (on 2026-10-28 the main checkout was 89 commits behind origin/main), and a merged
 * change to the constitution would not reach it. So at the start of each run this fetches origin/main, with a bounded
 * wait, and puts its AGENTS.md (in place of the checkout's), DESIGN_PRINCIPLES.md, STAGE_BOUNDARIES.md and
 * REVIEW_PRINCIPLES.md into the system prompt. Where the fetch fails, it grounds from origin/main as last fetched and
 * says so, rather than passing over it.
 */
import { execFileSync } from "node:child_process";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const FILES = ["AGENTS.md", "DESIGN_PRINCIPLES.md", "STAGE_BOUNDARIES.md", "REVIEW_PRINCIPLES.md"];
const FETCH_EVERY_MS = 60_000;

export default function grounding(pi: ExtensionAPI) {
  let fetchedAt = 0;
  pi.on("before_agent_start", async (event, ctx) => {
    const git = (...args: string[]) => execFileSync("git", args, { cwd: ctx.cwd, encoding: "utf8", timeout: 15_000, stdio: ["ignore", "pipe", "pipe"] });
    if (Date.now() - fetchedAt > FETCH_EVERY_MS) {
      try {
        git("fetch", "-q", "origin", "main");
        fetchedAt = Date.now();
      } catch (e) {
        let last = "unknown";
        try { last = git("log", "-1", "--format=%h, %cr", "origin/main").trim(); } catch { /* none */ }
        ctx.ui.notify(`origin/main could not be fetched (${e instanceof Error ? e.message.split("\n")[0] : String(e)}); the constitution is read from origin/main as last fetched (${last}).`, "warning");
      }
    }
    const files = event.systemPromptOptions.contextFiles;
    let top = "";
    try { top = git("rev-parse", "--show-toplevel").trim(); } catch { /* not a checkout */ }
    for (const name of FILES) {
      let content: string;
      try {
        content = git("show", `origin/main:${name}`);
      } catch (e) {
        ctx.ui.notify(`${name} on origin/main could not be read into the system prompt: ${e instanceof Error ? e.message.split("\n")[0] : String(e)}`, "warning");
        continue;
      }
      // The checkout's own copy of a file (Pi loads AGENTS.md from the working directory) is replaced, not doubled;
      // context files from parent directories or the agent directory are left as they are.
      const at = files.findIndex((f) => f.path === name || (top !== "" && f.path === `${top}/${name}`));
      const entry = { path: `origin/main:${name}`, content };
      if (at >= 0) files[at] = entry;
      else files.push(entry);
    }
  });
}

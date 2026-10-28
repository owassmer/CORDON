/**
 * Before the coordinator delegates, a fresh reader says back what it would understand from the text.
 *
 * The first time this session runs scripts/work on a task, or scripts/steer with a message, the call is blocked. The
 * task (and, for a steer, the message as it arrives during that task) goes, with nothing else but AGENTS.md, to the
 * builder's own model, which says back in plain words what it would do, why it believes the work is wanted, and what
 * done looks like. The block shows that restatement beside the text. Where they differ, the text failed to carry its
 * reason, and the coordinator rewrites it; where they agree, the identical command goes through. A changed task or
 * message is new text and is read afresh. scripts/steer --stop and scripts/review pass untouched: a reviewer is handed
 * REVIEW_PRINCIPLES.md's brief, not the coordinator's words. One delegation goes per command, and a task is named as
 * its file.
 *
 * The gate sees a command before it runs, so it cannot see everything: a loop's task paths, or an edit made in the same
 * round of tool calls (Pi checks every call of a round before running any). So the reader leaves word of each text it
 * read (.runs/read/<sha256>), and scripts/work and scripts/steer refuse a text it has not read.
 *
 * Why: a coordinator hands builders rules where it means reasons, and a builder handed a rule without its reason
 * follows it after its basis has gone, or writes the failure case it was warned about into the work. Asking the
 * coordinator to re-read its own text as the one receiving it does not hold, so the reading is done by the same kind of
 * agent that will receive it, knowing nothing of why the work exists.
 */
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import { isAbsolute, join } from "node:path";
import type { ExtensionAPI, ExtensionContext } from "@earendil-works/pi-coding-agent";

const READER = `You have been handed the text below as a builder in a repository you have not seen yet. What the repository
gives everyone who works in it, its AGENTS.md, is in <guidance>: read the text as one who shares that purpose. Before you start, say back in a few plain sentences, without planning file changes:
1. What you would do.
2. Why you believe it is wanted: the reason behind it, as you understand it from the text.
3. What "done" looks like, and how you would know.
4. Whether the text, followed faithfully, serves that purpose: where it would lead you somewhere the purpose would not
want, say where and why, as you understand the purpose.
If the text leaves any of these unclear to you, say so plainly rather than guessing. Where the only reason the text gives
for something is that someone decided, approved or asked for it, name that part. Where the text keeps, adjusts, works
around or defers to something that already exists (a rule, a number, a mechanism, a test, a record's shape, a review, a
decision), say what that thing is for and whether its purpose holds here; name any the text keeps or tunes without saying
what it is for.`;

/** The purpose the text is meant to serve, as the repository states it on origin/main: AGENTS.md. */
function guidance(dir: string): string {
  let agents = "";
  try { agents = execFileSync("git", ["-C", dir, "show", "origin/main:AGENTS.md"], { encoding: "utf8" }); } catch { /* none */ }
  if (!agents && existsSync(join(dir, "AGENTS.md"))) agents = readFileSync(join(dir, "AGENTS.md"), "utf8");
  return agents ? `\n\n<guidance>\n${agents}\n</guidance>` : "";
}

const RECENT = `
4. This text is a message arriving while the builder is already at work. Its latest steps, from its log, follow the
handed text in <recent> (they are not part of what it is handed, and the builder knows its own steps). Say whether the
message still tells the builder something it has not already found, decided or done; if it has reached it on its own,
say so plainly.`;

/** The command with heredoc bodies and quoted strings set aside, so a script is recognized only where the shell would
 * run it, not where a command merely mentions it. */
function invoked(command: string): string {
  const s = command.replace(/<<-?\s*(['"]?)(\w+)\1[^\n]*\n[\s\S]*?\n\s*\2\s*(?=\n|$)/g, "<<heredoc");
  // Quotes as the shell reads them: an apostrophe inside double quotes is a letter, not the start of a quoted string.
  let out = "", i = 0;
  while (i < s.length) {
    const c = s[i]!;
    if (c === "\\") { out += s.slice(i, i + 2); i += 2; continue; }
    if (c === "'") { const end = s.indexOf("'", i + 1); out += "''"; i = end < 0 ? s.length : end + 1; continue; }
    if (c === '"') {
      let j = i + 1;
      while (j < s.length && s[j] !== '"') j += s[j] === "\\" ? 2 : 1;
      out += '""'; i = j + 1; continue;
    }
    out += c; i++;
  }
  return out;
}

/** Where the fresh reader leaves word that it read a text: scripts/work and scripts/steer refuse a text without it, so
 * nothing is delegated unread however the command is put together (a loop, a chain, an edit made in the same round of
 * tool calls as the dispatch, which the gate sees before the edit is applied). */
function markRead(dir: string, text: string): void {
  let root = dir;
  try { root = execFileSync("git", ["-C", dir, "rev-parse", "--show-toplevel"], { encoding: "utf8" }).trim(); } catch { /* not a checkout */ }
  const marks = join(root, ".runs", "read");
  mkdirSync(marks, { recursive: true });
  writeFileSync(join(marks, createHash("sha256").update(text.trim()).digest("hex")), new Date().toISOString());
}

/** Runs of eight or more words a task shares with this pull request's reviewer reports. A task is written in the
 * coordinator's own words, so the builder gets what is wrong in the world, not a reviewer's framing of it; copying is a
 * matter of form, so form is what this compares. It informs; it does not block. */
function copied(text: string, task: string, dir: string): string {
  const pr = /(?:^|\/)(\d+)-[\w.-]+\.md$/.exec(task)?.[1];
  const runs = join(dir, ".runs");
  if (!pr || !existsSync(runs)) return "";
  const reports = readdirSync(runs).filter((f) => f.startsWith(`review-pr${pr}-`) && f.endsWith(".md") && !f.endsWith(".prompt.md") && !f.endsWith(".comment.md"));
  if (!reports.length) return "";
  const words = (t: string) => t.toLowerCase().replace(/[^a-z0-9$.' ]+/g, " ").split(/\s+/).filter(Boolean);
  const eights = (w: string[]) => new Set(w.slice(0, Math.max(0, w.length - 7)).map((_, i) => w.slice(i, i + 8).join(" ")));
  const theirs = eights(words(reports.map((f) => readFileSync(join(runs, f), "utf8")).join("\n")));
  const shared = [...eights(words(text))].filter((r) => theirs.has(r));
  return shared.length ? `\nIt shares ${shared.length} eight-word run(s) with this pull request's reviewer reports, e.g. "${shared.slice(0, 3).join('", "')}": the task should be in your own words.` : "";
}

const escape = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** A task file's text as it will be when the command runs: written by this command (a heredoc), or as it stands. */
function taskText(command: string, task: string, dir: string): string | undefined {
  const written = new RegExp(`>\\s*${escape(task)}\\s*<<-?\\s*(['"]?)(\\w+)\\1[^\\n]*\\n([\\s\\S]*?)\\n\\s*\\2\\s*(?=\\n|$)`).exec(command);
  if (written) return written[3];
  const path = isAbsolute(task) ? task : join(dir, task);
  return existsSync(path) ? readFileSync(path, "utf8") : undefined;
}

/** For a steer: the message, the task of the run it goes to, and what the builder has done most recently. */
function steerText(command: string, dir: string): { task?: string; taskText?: string; message: string; recent?: string; review?: boolean } | undefined {
  // The message as the shell hands it over: a single-quoted string as written, a double-quoted one with its escapes undone.
  const m = /scripts\/steer\s+(\S+)\s+(?:'([^']*)'|"((?:[^"\\]|\\.)*)")/.exec(command);
  if (!m) return undefined;
  const run = m[1];
  const message = m[2] ?? m[3]!.replace(/\\(["\\$`])/g, "$1");
  const runs = join(dir, ".runs");
  const log = existsSync(runs) ? readdirSync(runs).filter((f) => f.startsWith(run!) && f.endsWith(".log")).sort().pop() : undefined;
  const body = log ? readFileSync(join(runs, log), "utf8") : "";
  const task = /^=== builder on (\S+)/m.exec(body)?.[1];
  // The builder's latest steps (what it said and what it ran), so the reader can say whether the message is still news.
  const steps = body.split("\n").filter((l) => / says: | \u2192 |^=== steered/.test(l)).slice(-25).map((l) => l.slice(0, 300));
  const review = /^=== reviewer on /m.test(body);
  const taskFile = task ? join(".runs", "tasks", task) : undefined;
  return { task: taskFile, taskText: taskFile ? taskText("", taskFile, dir) : undefined, message: message!, recent: steps.length ? steps.join("\n") : undefined, review };
}

/** The builder's model, named in scripts/work and nowhere else. */
function builderModel(dir: string): { provider: string; id: string } | undefined {
  const script = join(dir, "scripts/work");
  const m = existsSync(script) ? /^BUILDER="([^/"]+)\/([^":]+)/m.exec(readFileSync(script, "utf8")) : null;
  return m ? { provider: m[1]!, id: m[2]! } : undefined;
}

/** Where the builder works, so the reader can say where a task points outside its reach. */
const SEES = "You will work in the unit's worktree: a full checkout of the repository on the unit's branch, with git history, the shared content-addressed store of source bytes, and the network. You can read the unit's plan from its pull request (gh pr view <n>). You commit on the branch; you cannot push or write to GitHub. If the text points you at anything outside that, say it is out of your reach.";

async function freshReading(ctx: ExtensionContext, dir: string, handed: string, recent?: string): Promise<string> {
  const named = builderModel(dir);
  const sees = SEES;
  const model = named ? ctx.modelRegistry.find(named.provider, named.id) : undefined;
  if (!model) return "(The fresh reader could not be reached: the builder's model is not available here. Read it yourself, as one who knows nothing of why it exists.)";
  try {
    const r = await ctx.modelRegistry.complete(model, { messages: [{ role: "user" as const, content: [{ type: "text" as const, text: `${READER}${sees ? `\n${sees}` : ""}${recent ? RECENT : ""}${guidance(dir)}\n\n<handed>\n${handed}\n</handed>${recent ? `\n\n<recent>\n${recent}\n</recent>` : ""}` }], timestamp: Date.now() }] }, { maxTokens: 1600, cacheRetention: "none" });
    const said = r.content.filter((c): c is { type: "text"; text: string } => c.type === "text").map((c) => c.text).join("").trim();
    return said || "(The fresh reader returned nothing.)";
  } catch (e) {
    return `(The fresh reader could not be reached: ${e instanceof Error ? e.message : String(e)}. Read it yourself, as one who knows nothing of why it exists.)`;
  }
}

export default function delegation(pi: ExtensionAPI) {
  const checked = new Set<string>();
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return;
    const command = String((event.input as { command?: string }).command ?? "");
    const shell = invoked(command);
    const at = /(?:^|[;&|(\n]\s*|\s)(?:\S*\/)?scripts\//;
    const works = [...shell.matchAll(new RegExp(at.source + "work\\s+(\\S+\\.md)", "g"))];
    const work = works[0];
    const steer = new RegExp(at.source + "steer\\s").test(shell) && !/--stop\b/.test(shell);
    if (!work && !steer) return;
    // One delegation per command, so the reader reads each one before it goes.
    if (works.length + (steer ? 1 : 0) > 1) return { block: true, reason: "Delegate one task (or one steer) per command, so the fresh reader reads each before it goes." };
    // A dispatch is its own command (after an optional cd; its output may be piped). A refusal here stops the whole
    // command before the shell runs, so an edit or commit sharing it would be dropped without running.
    const rest = shell.replace(/^\s*cd\s+\S+\s*(?:&&|;)\s*/, "");
    if (!/^\s*(?:\S*\/)?scripts\/(?:work|steer)\b/.test(rest) || /;|&&|\|\||\n\s*\S/.test(rest.trimEnd()))
      return { block: true, reason: "Run the dispatch as a command on its own (cd <checkout> && scripts/work .runs/tasks/<pr>-<n>.md <worktree>, or scripts/steer <run> \"...\"). Nothing in this command ran: run its other parts first, by themselves." };
    // Tool calls of one turn run together: a dispatch beside another call (an edit of the task it sends) can go out on the
    // text as it was before the edit, not the text its reader read. A dispatch is the only call of its turn.
    const turn = [...(ctx.sessionManager.getBranch() as Array<Record<string, any>>)].reverse().find((e) => e.message?.role === "assistant");
    const calls = ((turn?.message?.content ?? []) as Array<{ type?: string }>).filter((c) => c.type === "toolCall").length;
    if (calls > 1) return { block: true, reason: "Dispatch in a turn of its own: other calls in this turn run alongside it, so it could go out on a text other than the one its reader read. Nothing in this call ran; run the other calls first, then this one by itself." };
    const dir = command.match(/^\s*cd\s+(\S+)/)?.[1] ?? ctx.cwd;

    // What the receiver will be handed, as it will read it.
    let handed: string;
    let task = "";
    if (work) {
      task = work[1]!;
      const text = /^[\w./-]+\.md$/.test(task) ? taskText(command, task, dir) : undefined;
      if (text === undefined) return { block: true, reason: `The fresh reader could not find the task "${task}" to read. Name the task file itself (scripts/work .runs/tasks/<pr>-<n>.md <worktree>), written before this command.` };
      handed = text;
    } else {
      const s = steerText(command, dir);
      if (!s) return;
      if (s.review) return { block: true, reason: "That run is a review: a reviewer gets no message after its brief (REVIEW_PRINCIPLES.md, \"Briefs\"), and scripts/steer refuses it. Only --stop reaches a reviewer." };
      task = s.task ?? "";
      handed = `${s.taskText ? `${s.taskText}\n\n` : ""}While you are working on that, this message arrives from the one who handed it to you:\n${s.message}`;
    }
    const key = createHash("sha256").update(handed).digest("hex");
    if (checked.has(key)) return;
    checked.add(key);
    // For a steer the reader also sees the builder's latest steps, since a steer can tell a builder what it has already
    // found for itself, and a reader rejects a steer that refers to work it cannot see. That part is for the reader only;
    // the builder is handed the message alone.
    const recent = work ? undefined : steerText(command, dir)?.recent;
    const reading = await freshReading(ctx, dir, handed, recent);
    // What scripts/work or scripts/steer will check: the task's text, or the steer's message.
    if (work) markRead(dir, handed);
    else {
      markRead(dir, steerText(command, dir)?.message ?? "");
    }
    return {
      block: true,
      reason:
        `A fresh reader, the builder's own model knowing nothing else, was handed this and says:\n\n${reading}\n\n` +
        (recent ? `The builder's latest steps, which the reader also saw:\n${recent}\n\nIf the builder has already reached what the message says, send nothing.\n\n` : "") +
        `Compare that with what you mean. Where the reason, the work or "done" came across differently, the text did not carry it: rewrite it. ` +
        `Where it came across as you mean it, run the identical command again.${copied(handed, task, dir)}\n\nWhat was handed over:\n\n${handed}`,
    };
  });
}

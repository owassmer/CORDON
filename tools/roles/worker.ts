/**
 * The builder's way back to the coordinator, and the limits of its reach. scripts/work loads it into the builder's Pi.
 *
 * Report: what a builder understood rarely comes back from a short final message, so where it departed from the plan
 * is found only by reading its code. So it ends with the report tool, whose fields are what the coordinator needs to
 * judge the work: what changed and why, where it departed from the task and why, what of its done is not yet true, and
 * what it saw beyond its task. The run does not settle until it has reported. What keeps a task's done from being true
 * is the task's work; the report says only what could not be made true and why. scripts/work puts the report in the
 * run's log, and the coordinator's finish notice carries it.
 *
 * Reach: the builder works in the unit's own worktree, unsandboxed, since it reads the shared store and acquires from
 * the network. What it may not do is publish: the coordinator reads every diff before it is pushed, and a PR's body,
 * comments and state are the coordinator's. So a bash command that pushes, or a gh command that writes, is refused.
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { Type } from "typebox";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

/** A command that publishes: git push, or a gh subcommand that changes GitHub. Reading with gh stays open. */
export function publishes(command: string): string | null {
  const c = command.replace(/\s+/g, " ");
  if (/(^|[;&|(`$ ])git( -C \S+)? push\b/.test(c)) return "git push";
  if (/(^|[;&|(`$ ])gh (pr|issue) (create|edit|merge|close|reopen|ready|comment|review|lock|unlock|delete)\b/.test(c)) return "a gh command that writes";
  if (/(^|[;&|(`$ ])gh (repo|release|label|secret|variable|workflow|run) (create|edit|delete|set|enable|disable|rerun|cancel|upload)\b/.test(c)) return "a gh command that writes";
  if (/(^|[;&|(`$ ])gh api\b/.test(c) && /(-X|--method) ?(POST|PUT|PATCH|DELETE)\b|(^| )(-f|-F|--field|--raw-field|--input)\b/.test(c)) return "a gh api call that writes";
  return null;
}

export default function worker(pi: ExtensionAPI) {
  let reported = false;
  let reminded = 0;

  pi.on("tool_call", async (event) => {
    if (event.toolName !== "bash") return undefined;
    const what = publishes(String((event.input as { command?: unknown })?.command ?? ""));
    if (!what) return undefined;
    return { block: true, reason: `${what} is the coordinator's: commit on the branch and report; the coordinator reads your diff and pushes it.` };
  });

  pi.registerTool({
    name: "report",
    label: "Report",
    description:
      "End your run with this, after committing. The coordinator judges your work from it and decides what comes next, " +
      "and it cannot see your reasoning, so say what it needs in full sentences.",
    parameters: Type.Object({
      changed: Type.String({ description: "What you changed and why: the understanding behind it, not a list of files." }),
      departures: Type.String({ description: "Where you departed from the task or the plan in the pull request, or chose something neither asked for, and why. Say 'none' only if there were none." }),
      notTrue: Type.String({ description: "What of your task's done is not true at the consumer surface as you leave it, and what stands in the way. Whatever keeps it from being true is your task's work, so this holds only what you could not make true: a decision that is not yours to make, or something you cannot reach from here. 'none' where all of it is true." }),
      beyond: Type.String({ description: "What you saw that bears on none of your task's done but on another owner, input or unit, one line each, as you saw it. 'none' where nothing." }),
    }),
    async execute(_id, params) {
      const dir = join(process.env.ROLE_RUN_DIR ?? process.cwd(), ".tmp");
      mkdirSync(dir, { recursive: true });
      writeFileSync(join(dir, "report.json"), JSON.stringify(params));
      reported = true;
      return { content: [{ type: "text", text: "Reported. You can finish." }], details: {} };
    },
  });

  // The run settles only after a report: until then each settle is held with a request for it (a few times at most,
  // so a model that cannot comply does not loop; scripts/work then ends the run as unreported, exit 8).
  pi.on("agent_before_settle", () => {
    if (reported || reminded >= 3) return undefined;
    reminded++;
    return {
      entries: [{ type: "custom_message", customType: "report-due", display: true, content: "Before you finish: commit, then call report with what you changed and why, where you departed from the task and why, what of your task's done is not yet true and why, and what you saw beyond it." }],
      continue: true,
    };
  });
}

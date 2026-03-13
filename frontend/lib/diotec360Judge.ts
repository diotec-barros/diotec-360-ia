"use client";

export type LocalJudgeStatus = "cold" | "loading" | "ready" | "error";

export type LocalJudgeVerdict = {
  status: "PROVED" | "FAILED";
  reason?: string;
  details?: {
    sat?: "sat" | "unsat" | "unknown";
    constraints?: string[];
  };
};

function extractBlock(code: string, blockName: string) {
  const re = new RegExp(`${blockName}\\s*\\{([\\s\\S]*?)\\}`, "m");
  const m = code.match(re);
  return m ? m[1] : "";
}

function extractConstraints(block: string) {
  // Keep it strict/simple for v1:
  // - each constraint is expected to end with ';' OR be on its own line
  // - ignore empty lines
  return block
    .split(/;|\n/)
    .map((s) => s.trim())
    .filter(Boolean);
}

type ParsedConstraint = { left: string; op: ">=" | "<=" | "==" | "!=" | ">" | "<"; right: string };

function parseSimpleExpr(expr: string): ParsedConstraint | null {
  // Supported forms (v1.1):
  // - <arith> (>=|<=|==|!=|>|<) <arith>
  // where <arith> is built from identifiers / integer literals and + - * /.
  const m = expr.match(/^(.*?)\s*(>=|<=|==|!=|>|<)\s*(.*?)$/);
  if (!m) return null;
  const left = m[1].trim();
  const op = m[2] as ParsedConstraint["op"];
  const right = m[3].trim();
  if (!left || !right) return null;
  return { left, op, right };
}

type Token =
  | { kind: "int"; value: number }
  | { kind: "id"; value: string }
  | { kind: "op"; value: "+" | "-" | "*" | "/" }
  | { kind: "paren"; value: "(" | ")" };

function tokenizeArith(input: string): Token[] | null {
  const s = input.trim();
  const out: Token[] = [];
  let i = 0;
  while (i < s.length) {
    const ch = s[i];
    if (ch === " " || ch === "\t" || ch === "\n" || ch === "\r") {
      i += 1;
      continue;
    }
    if (ch === "(" || ch === ")") {
      out.push({ kind: "paren", value: ch });
      i += 1;
      continue;
    }
    if (ch === "+" || ch === "-" || ch === "*" || ch === "/") {
      out.push({ kind: "op", value: ch });
      i += 1;
      continue;
    }
    if (/[0-9]/.test(ch) || (ch === "-" && i + 1 < s.length && /[0-9]/.test(s[i + 1]))) {
      let j = i + (ch === "-" ? 1 : 0);
      while (j < s.length && /[0-9]/.test(s[j])) j += 1;
      const raw = s.slice(i, j);
      const n = Number(raw);
      if (!Number.isFinite(n) || !Number.isInteger(n)) return null;
      out.push({ kind: "int", value: n });
      i = j;
      continue;
    }
    if (/[A-Za-z_]/.test(ch)) {
      let j = i + 1;
      while (j < s.length && /[A-Za-z0-9_]/.test(s[j])) j += 1;
      out.push({ kind: "id", value: s.slice(i, j) });
      i = j;
      continue;
    }
    return null;
  }
  return out;
}

type ArithAST =
  | { type: "int"; value: number }
  | { type: "id"; name: string }
  | { type: "bin"; op: "+" | "-" | "*" | "/"; left: ArithAST; right: ArithAST };

function parseArith(tokens: Token[]): ArithAST | null {
  let pos = 0;

  const peek = () => tokens[pos];
  const consume = () => tokens[pos++];

  const parseFactor = (): ArithAST | null => {
    const t = peek();
    if (!t) return null;
    if (t.kind === "int") {
      consume();
      return { type: "int", value: t.value };
    }
    if (t.kind === "id") {
      consume();
      return { type: "id", name: t.value };
    }
    if (t.kind === "paren" && t.value === "(") {
      consume();
      const inner = parseExpr();
      const close = peek();
      if (!inner || !close || close.kind !== "paren" || close.value !== ")") return null;
      consume();
      return inner;
    }
    return null;
  };

  const parseTerm = (): ArithAST | null => {
    let node = parseFactor();
    if (!node) return null;
    while (true) {
      const t = peek();
      if (!t || t.kind !== "op" || (t.value !== "*" && t.value !== "/")) break;
      consume();
      const rhs = parseFactor();
      if (!rhs) return null;
      node = { type: "bin", op: t.value, left: node, right: rhs };
    }
    return node;
  };

  const parseExpr = (): ArithAST | null => {
    let node = parseTerm();
    if (!node) return null;
    while (true) {
      const t = peek();
      if (!t || t.kind !== "op" || (t.value !== "+" && t.value !== "-")) break;
      consume();
      const rhs = parseTerm();
      if (!rhs) return null;
      node = { type: "bin", op: t.value, left: node, right: rhs };
    }
    return node;
  };

  const ast = parseExpr();
  if (!ast) return null;
  if (pos !== tokens.length) return null;
  return ast;
}

function arithToZ3(ast: ArithAST, ctx: any, getVar: (name: string) => any): any {
  switch (ast.type) {
    case "int":
      return ctx.Int.val(ast.value);
    case "id":
      return getVar(ast.name);
    case "bin": {
      const L = arithToZ3(ast.left, ctx, getVar);
      const R = arithToZ3(ast.right, ctx, getVar);
      switch (ast.op) {
        case "+":
          return L.add(R);
        case "-":
          return L.sub(R);
        case "*":
          return L.mul(R);
        case "/":
          return L.div(R);
      }
    }
  }
}

export class Diotec360JudgeWasm {
  private status: LocalJudgeStatus = "cold";
  private z3: any = null;

  getStatus() {
    return this.status;
  }

  async init() {
    if (this.status === "ready") return "READY" as const;
    if (this.status === "loading") return "LOADING" as const;

    this.status = "loading";
    try {
      // z3-solver exposes an async init() returning { Context, ... }
      const mod: any = await import("z3-solver");
      const initZ3 = mod?.init || mod?.default?.init;
      if (typeof initZ3 !== "function") {
        throw new Error("z3-solver: init() not found");
      }

      this.z3 = await initZ3();
      this.status = "ready";
      return "READY" as const;
    } catch (e) {
      this.status = "error";
      throw e;
    }
  }

  async verifyLocally(code: string): Promise<LocalJudgeVerdict> {
    await this.init();

    const guardBlock = extractBlock(code, "guard");
    const verifyBlock = extractBlock(code, "verify");

    const constraints = [...extractConstraints(guardBlock), ...extractConstraints(verifyBlock)];
    if (constraints.length === 0) {
      return { status: "FAILED", reason: "No constraints found in guard/verify blocks" };
    }

    try {
      const { Context } = this.z3;
      const ctx = new Context("main");
      const solver = new ctx.Solver();

      /** @type {Map<string, any>} */
      const vars = new Map();

      const getVar = (name: string) => {
        const existing = vars.get(name);
        if (existing) return existing;
        const v = ctx.Int.const(name);
        vars.set(name, v);
        return v;
      };

      for (const c of constraints) {
        const parsed = parseSimpleExpr(c);
        if (!parsed) {
          return { status: "FAILED", reason: `Unsupported constraint syntax: ${c}`, details: { constraints } };
        }

        const leftTokens = tokenizeArith(parsed.left);
        const rightTokens = tokenizeArith(parsed.right);
        if (!leftTokens || !rightTokens) {
          return { status: "FAILED", reason: `Unsupported arithmetic syntax: ${c}`, details: { constraints } };
        }

        const leftAst = parseArith(leftTokens);
        const rightAst = parseArith(rightTokens);
        if (!leftAst || !rightAst) {
          return { status: "FAILED", reason: `Unsupported arithmetic syntax: ${c}`, details: { constraints } };
        }

        const L = arithToZ3(leftAst, ctx, getVar);
        const R = arithToZ3(rightAst, ctx, getVar);

        switch (parsed.op) {
          case ">=":
            solver.add(L.ge(R));
            break;
          case ">":
            solver.add(L.gt(R));
            break;
          case "<=":
            solver.add(L.le(R));
            break;
          case "<":
            solver.add(L.lt(R));
            break;
          case "==":
            solver.add(L.eq(R));
            break;
          case "!=":
            solver.add(L.neq(R));
            break;
          default:
            return { status: "FAILED", reason: `Unsupported operator: ${parsed.op}`, details: { constraints } };
        }
      }

      const sat = await solver.check();
      const satStr = String(sat);

      if (satStr === "sat") {
        return { status: "PROVED", details: { sat: "sat", constraints } };
      }

      if (satStr === "unsat") {
        return { status: "FAILED", reason: "UNSAT: constraints are inconsistent", details: { sat: "unsat", constraints } };
      }

      return { status: "FAILED", reason: `Z3 returned: ${satStr}`, details: { sat: "unknown", constraints } };
    } catch (e: any) {
      return { status: "FAILED", reason: e?.message ? String(e.message) : String(e), details: { constraints } };
    }
  }
}

let _singleton: Diotec360JudgeWasm | null = null;

export function getDiotec360JudgeWasm() {
  if (!_singleton) _singleton = new Diotec360JudgeWasm();
  return _singleton;
}

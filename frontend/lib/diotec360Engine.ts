"use client";

export type Diotec360EngineInitOptions = {
  modelId?: string;
  device?: "webgpu" | "wasm";
};

export type GenerateOptions = {
  maxNewTokens?: number;
  temperature?: number;
  topP?: number;
};

type TextGenerationPipeline = (input: string, options?: Record<string, unknown>) => Promise<any>;

export class Diotec360Engine {
  private generator: TextGenerationPipeline | null = null;
  private status: "cold" | "loading" | "ready" | "error" = "cold";

  getStatus() {
    return this.status;
  }

  async init(opts: Diotec360EngineInitOptions = {}) {
    if (this.status === "ready") return "READY" as const;
    if (this.status === "loading") return "LOADING" as const;

    this.status = "loading";

    const modelId = opts.modelId || "Xenova/distilgpt2";
    const device = opts.device || "webgpu";

    try {
      const { pipeline, env } = await import("@xenova/transformers");

      // Keep models cached in browser storage when possible.
      // Avoid forcing remote mode; Xenova will choose the best available.
      env.allowLocalModels = false;

      // The runtime supports `device`, but some released TS typings don't expose it.
      // Keep runtime behavior (WebGPU) while appeasing strict TS.
      this.generator = (await (pipeline as any)("text-generation", modelId, {
        device,
      } as any)) as unknown as TextGenerationPipeline;

      this.status = "ready";
      return "READY" as const;
    } catch (e) {
      this.status = "error";
      throw e;
    }
  }

  async generateText(prompt: string, opts: GenerateOptions = {}) {
    if (!this.generator) {
      throw new Error("Diotec360Engine: init() required before generateText()");
    }

    const out = await this.generator(prompt, {
      max_new_tokens: opts.maxNewTokens ?? 128,
      temperature: opts.temperature ?? 0.2,
      top_p: opts.topP ?? 0.9,
    });

    // Typical xenova pipeline output: [{ generated_text: "..." }]
    const generatedText = Array.isArray(out) ? out?.[0]?.generated_text : out?.generated_text;
    if (typeof generatedText === "string") return generatedText;

    return JSON.stringify(out);
  }
}

let _singleton: Diotec360Engine | null = null;

export function getDiotec360Engine() {
  if (!_singleton) _singleton = new Diotec360Engine();
  return _singleton;
}

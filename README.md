# AI Security Workshop

Hands-on work, labs and materials from the AI Security Workshop — a ground-up introduction to how
AI systems work and where they break.

Everything here is **built to run offline**. Each deck is a single self-contained HTML file with no
CDN, web fonts, external images or build step. Copy the folder to a USB stick, double-click a file,
and it works with no internet and nothing to install.

## Repository structure

| Path | Contents |
|------|----------|
| [`slides/ai-fundamentals.html`](slides/ai-fundamentals.html) | **Deck B** — the main primer: machine learning through to AI supply-chain security, ending in a hands-on audit lab (20 slides) |
| [`slides/ai-security-workshop.html`](slides/ai-security-workshop.html) | **Deck A** — the prompt-security workshop: prompt injection, jailbreaking and a 5-layer defence (20 slides) |

## Deck B — AI Fundamentals

The main deck. It starts with no assumed knowledge and runs from "what is machine learning" all the
way to auditing a third-party model you did not build.

| # | Section | Slide |
|---|---------|-------|
| 1–4 | AI Foundations | Machine learning and the four learning types · neural networks and deep learning · large language models · how LLMs learn |
| 5–8 | LLM Fundamentals | Tokens and token IDs · nondeterminism and the next-token spread · temperature and top-p · max tokens and the context window. Slides 7 and 8 carry runnable "try it yourself" examples with the parameter names for each provider |
| 9 | Prompt Engineering | **The Anatomy of a Prompt** — the four pillars (instruction, context, output format, constraints), the four assembled into one prompt, and specificity vs verbosity |
| 10–11 | Advanced Prompting | **The Shot Spectrum** — zero-, one- and few-shot with worked examples · **Chains and Templates** — chain-of-thought, zero-shot CoT and reusable prompt templates. Each technique carries its own "use when" |
| 12 | Instruction Hierarchy | **System vs User Prompts** — what each is, the comparison grid, and why the boundary between them is probabilistic rather than architectural |
| 13 | AI Security Threats | Vulnerabilities across the model lifecycle, and MITRE ATT&CK vs ATLAS |
| 14 | AI in Cyber Security | Attack · Defend · Secure — the three ways AI meets security |
| 15 | Training Data | Where the data comes from: provenance, ML-BOM, personal data |
| 16 | Building the Model | Epochs and overfitting, validation, pruning and quantisation, federated learning |
| 17 | The Inheritance Problem | Fine-tuning inherits everything beneath it |
| 18 | The Black Box Problem | Why a model cannot be inspected, and what a model card is for |
| 19 | Model Supply Chain | **Practical: Audit a Model** — the interactive lab (below) |
| 20 | Model Supply Chain | **Audit Answer Key** — every finding and its severity |

## The lab — Audit a Model (slide 19)

Anyone can publish a model. That makes public model hubs an enormous resource and a real
supply-chain risk, and reading a model repository critically is a skill worth practising before it
matters. Slide 19 is a **simulated model-hub repository** — a plausible-looking listing for
`nimbus-labs/redact-guard-v3`, a PII-redaction model that a company wants to put in front of its
data-loss-prevention gate — and the participant is the reviewer of record.

**How it works**

1. Read the model card, the file listing, the community tab and the sidebar metadata.
2. Hover over the page to reveal **hotspots**; click one to flag it and rate it **Low**, **Medium**
   or **High**.
3. Submit the review. Every finding is then scored, explained and — if it was missed — revealed in
   place on the page.

There are **12 concerns** hidden in the repository, spread across all three severities. They are not
all serious: rating a minor one as critical costs exactly as much as missing a real one, which is
the point. Scoring **70% at the correct severity** unlocks a completion code; below that the code
stays locked and the participant is invited to review again. The debrief closes with twelve
questions to ask of any third-party model, and slide 20 is the full answer key for whoever is
running the session.

The lab is plain HTML, CSS and JavaScript inside the deck — no iframe, no server, no network calls.
It works from `file://` like the rest of the deck.

## Deck A — Prompt Security Workshop

A 20-slide workshop on **prompt injection** and **jailbreaking**, and how to defend against them in
five layers: harden the prompt → guardrails → architecture and least privilege → output handling →
monitor. It is framed around an "attack, then defend" playground running a local open-source model
with Ollama, so participants break a chatbot before they fix it.

## Running the decks

Open either HTML file in any modern browser — double-click it, or drag it onto a browser window.

| Control | Action |
|---------|--------|
| `←` `→` `Space` | Previous / next slide |
| Click | Next slide |
| `F` | Fullscreen |
| `#<n>` | Deep-link to a slide, e.g. `ai-fundamentals.html#19` |

Slides are laid out for **16:9** and letterbox themselves to any window, so they present cleanly on a
projector or a laptop screen. Inside the lab, clicking and the arrow keys are handed to the lab
itself rather than the deck, so reviewing the repository never skips a slide.

## Topics covered

- AI fundamentals — machine learning, neural networks, LLMs and how they are trained
- LLM fundamentals — tokens, nondeterminism, temperature and top-p, max tokens, context windows
- Prompt engineering — the four pillars of a prompt, specificity vs verbosity
- Advanced prompting — zero/one/few-shot, chain-of-thought, prompt templates
- The instruction hierarchy — system vs user prompts, and why the separation is soft
- Prompt security — prompt injection, jailbreaks and mitigations
- Data poisoning attacks and defences
- AI supply chain security — provenance, model cards and third-party model review
- Building secure AI systems

## Author

**Sowat Hossain Rafi** — [@SowatRafi](https://github.com/SowatRafi)

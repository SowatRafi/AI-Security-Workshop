# AI Security Workshop

Hands-on work, labs and materials from the AI Security Workshop — a ground-up introduction to how
AI systems work and where they break.

Everything here is **built to run offline**. Each deck is a single self-contained HTML file with no
CDN, web fonts, external images or build step. Copy the folder to a USB stick, double-click a file,
and it works with no internet and nothing to install.

## Repository structure

| Path | Contents |
|------|----------|
| [`slides/ai-fundamentals.html`](slides/ai-fundamentals.html) | **Deck B** — the main primer: machine learning through to AI supply-chain security, ending in a hands-on audit lab (26 slides) |
| [`slides/ai-security-workshop.html`](slides/ai-security-workshop.html) | **Deck A** — the prompt-security workshop: prompt injection, jailbreaking and a 5-layer defence (20 slides) |
| [`labs/prompt-injection-in-action/`](labs/prompt-injection-in-action/) | Facilitator runbook and Ollama `Modelfile`s for the live prompt-injection practical (Deck B, slides 16–18) |
| [`START-HERE.cmd`](START-HERE.cmd) · [`.command`](START-HERE.command) · [`.sh`](START-HERE.sh) | **Start here** — Windows, macOS, Linux. Run once per machine: it sets up the model and makes the live chat work however you open the slides afterwards |
| [`labs/serve-deck.py`](labs/serve-deck.py) | The launcher itself: builds the practice model, serves the workshop, proxies the deck through to Ollama (`serve-deck.ps1` is the Windows fallback when Python is absent) |

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
| 13–14 | How LLMs Follow Instructions | **Five Sources, One Context Window** — system and developer prompts, user input, retrieved context and tool output, and who controls each · **Labelled in Theory, One Stream in Practice** — ChatML, Harmony and the provider-side reinforcements, then why the labelling does not hold. Each separation method carries its own "use when" |
| 15 | Prompt Injection | **What is Prompt Injection?** — the OWASP LLM #1 vulnerability: a worked attack on a translation tool, the root cause, the SQL-injection parallel, and a risk ladder showing when it matters |
| 16–18 | Prompt Injection | **Prompt Injection in Action** — the live practical against a local model (below) · **Your Turn** — the student exercise with click-to-reveal hints · **Debrief** — what actually happened, and why nothing broke |
| 19 | AI Security Threats | Vulnerabilities across the model lifecycle, and MITRE ATT&CK vs ATLAS |
| 20 | AI in Cyber Security | Attack · Defend · Secure — the three ways AI meets security |
| 21 | Training Data | Where the data comes from: provenance, ML-BOM, personal data |
| 22 | Building the Model | Epochs and overfitting, validation, pruning and quantisation, federated learning |
| 23 | The Inheritance Problem | Fine-tuning inherits everything beneath it |
| 24 | The Black Box Problem | Why a model cannot be inspected, and what a model card is for |
| 25 | Model Supply Chain | **Practical: Audit a Model** — the interactive lab (below) |
| 26 | Model Supply Chain | **Audit Answer Key** — every finding and its severity |

## The lab — Audit a Model (slide 25)

Anyone can publish a model. That makes public model hubs an enormous resource and a real
supply-chain risk, and reading a model repository critically is a skill worth practising before it
matters. Slide 25 is a **simulated model-hub repository** — a plausible-looking listing for
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
questions to ask of any third-party model, and slide 26 is the full answer key for whoever is
running the session.

The lab is plain HTML, CSS and JavaScript inside the deck — no iframe, no server, no network calls.
It works from `file://` like the rest of the deck.

## The practical — Prompt Injection in Action (slides 16–18)

A 20–25 minute hands-on block where participants perform prompt injection themselves against a
**local open-source model**. No cloud service, no API key, no account: the target is an Ollama model
running on the participant's own machine, built from the `Modelfile` in
[`labs/prompt-injection-in-action/`](labs/prompt-injection-in-action/).

The target is **AtlasBot**, an internal assistant for a fictional freight company. It will happily
discuss office hours, meeting rooms and holiday policy, and it has been instructed to protect one
fictional canary value. Participants never see its system prompt.

The exercise is deliberately built around the attacker's *process* rather than a magic prompt —
use it normally, observe, probe its instructions, attempt injection, observe again — and slide 17
carries three progressive hints that open on click, so the room can be nudged without being told.

**Slides 16 and 17 have a chat window built in.** A *"💬 Open the live chat"* button opens a panel
that talks to Ollama on the participant's own machine, so they can run the whole attack without
leaving the deck. It keeps conversation history, has a **Reset** button for starting an attempt
fresh, and switches between the standard and hardened builds for the defence-in-depth
demonstration. It is the only network call in the deck and it never leaves `localhost`; if Ollama
is not reachable the panel says exactly what to do rather than failing silently. Everything it needs
is handled by the launcher — the terminal remains a fine alternative either way.

It closes on the point the whole section exists to make: run `/show system` and the entire hidden
instruction prints, canary included, with no attack at all. **A system prompt is an instruction to
the model, not an access-control mechanism.**

The [facilitator runbook](labs/prompt-injection-in-action/README.md) carries the setup, speaker
notes, the demonstration script, the student brief, the debrief answers and the instructor notes.
Every technique in it was run against `llama3.2` and the observed result recorded, including two
findings that are now taught rather than tidied away: fictional framing tends to make the model
**invent** a plausible code name rather than leak the real one, and a carefully hardened system
prompt leaked *more* readily than the plain one — which is the workshop's own argument for
defence-in-depth, demonstrated live.

## Deck A — Prompt Security Workshop

A 20-slide workshop on **prompt injection** and **jailbreaking**, and how to defend against them in
five layers: harden the prompt → guardrails → architecture and least privilege → output handling →
monitor. It is framed around an "attack, then defend" playground running a local open-source model
with Ollama, so participants break a chatbot before they fix it.

## Running the decks

Open either HTML file in any modern browser — double-click it, or drag it onto a browser window.

The one exception is the **live chat on Deck B slides 16–17**, which needs to reach a model. For
that, double-click the launcher for your system instead:

| System | Double-click |
|---|---|
| **Windows** | `START-HERE.cmd` |
| **macOS** | `START-HERE.command` |
| **Linux** | `START-HERE.sh` |

It checks what the machine already has and **asks before downloading anything** — if Ollama is
missing it explains what Ollama is and offers to fetch it; if the model is missing it names it and
its size and asks first. Decline either and every slide still works; only the live chat needs them.

Requirements: [Ollama](https://ollama.com/download), plus Python 3 on macOS and Linux (both normally
have it; Windows falls back to PowerShell). No accounts, no API keys, no admin rights, no Ollama
configuration.

Browsers deliberately stop a page opened off disk from reaching a local server, so the launcher
serves the workshop at `http://localhost:8000` and passes the deck's requests through to Ollama on
that same origin. Everything else in both decks works offline from a plain double-click.

| Control | Action |
|---------|--------|
| `←` `→` `Space` | Previous / next slide |
| Click | Next slide |
| `F` | Fullscreen |
| `#<n>` | Deep-link to a slide, e.g. `ai-fundamentals.html#25` |

Slides are laid out for **16:9** and letterbox themselves to any window, so they present cleanly on a
projector or a laptop screen. Inside the lab, clicking and the arrow keys are handed to the lab
itself rather than the deck, so reviewing the repository never skips a slide.

## Topics covered

- AI fundamentals — machine learning, neural networks, LLMs and how they are trained
- LLM fundamentals — tokens, nondeterminism, temperature and top-p, max tokens, context windows
- Prompt engineering — the four pillars of a prompt, specificity vs verbosity
- Advanced prompting — zero/one/few-shot, chain-of-thought, prompt templates
- The instruction hierarchy — system vs user prompts, and why the separation is soft
- How LLMs follow instructions — the five sources in a context window, ChatML and Harmony, and the one-stream reality
- Prompt injection — how it works, why formatting cannot stop it, and how the risk scales with an application's reach
- Hands-on prompt injection against a local open-source model, with a facilitator runbook
- Prompt security — jailbreaks and mitigations
- Data poisoning attacks and defences
- AI supply chain security — provenance, model cards and third-party model review
- Building secure AI systems

## Author

**Sowat Hossain Rafi** — [@SowatRafi](https://github.com/SowatRafi)

# Helix Architecture

Helix is built from scratch. It is not a fork of Professor Synapse or any other agent persona. The architecture is a governed maze — structured decision flow with explicit reasoning at each node.

---

## Design Principles

**Governed maze, not open conversation.** Helix does not improvise a teaching style. It traverses a defined decision tree: assess student state → select modality → execute → check. Every branch in the tree is knowable and auditable.

**Open-Brain reasoning.** Helix shows its work. When it chooses a recall card over an explanation, it says why. When it detects a misconception, it names the misconception before correcting it. The student can always see the reasoning chain.

**Derived from course identity.** Helix's voice comes from `helix-voice.md`. Its content knowledge comes from the lesson files. It has no inherited personality, no borrowed teaching philosophy, no blackbox prior training on how to be a tutor.

---

## System Prompt Architecture

Helix's system prompt has four layers, written in order, each governing a distinct concern:

```
[LAYER 1: IDENTITY]
Who Helix is. Derived from helix-voice.md.
Defines: name, role, what Helix will and won't do.

[LAYER 2: REASONING CHAIN]
How Helix thinks before responding.
Defines: the 4-step assess→select→execute→check loop.
Every response begins with a silent (or visible) pass through this loop.

[LAYER 3: MODALITY RULES]
What Helix can do: explain, quiz, hint, flag, schedule.
Each modality has a trigger condition. Helix cannot mix modalities in one response.

[LAYER 4: CONSTRAINTS]
What Helix never does. Hard stops.
No unsolicited opinions. No responses outside the lesson curriculum. No override of FSRS scheduling without explicit student request.
```

---

## Decision Tree (Governed Maze)

```
Student input received
        │
        ▼
[ASSESS] What is the student's current state?
  ├─ Asking a concept question → [EXPLAIN]
  ├─ Completing an exercise → [FLAG CHECK]
  ├─ Requesting recall review → [QUIZ]
  ├─ Stuck / frustrated → [HINT]
  └─ Off-topic → [REDIRECT]
        │
        ▼
[SELECT] Which modality applies?
  (Modality rules from Layer 3 — one per response)
        │
        ▼
[EXECUTE] Respond in selected modality
  (Voice rules from Layer 1; content from lesson files)
        │
        ▼
[CHECK] Did the response resolve the student's state?
  ├─ Yes → end turn
  └─ No → surface the gap explicitly, do not loop silently
```

---

## FSRS Integration Layer

Separate from the conversation layer. FSRS scheduling runs as a background process:
- Student completes a recall card → submits Again/Hard/Good/Easy rating
- FSRS-5 calculates next review interval
- Helix receives the next due card on the student's next review session

Helix does not see the FSRS algorithm. It receives: `next_card: {{CARD_JSON}}`. The scheduling is invisible to Helix's conversation layer by design.

---

## Faculty Persona System

Defined in `00-d-helix-design/output/faculty-persona-spec.md`.

Trigger: student is in a phase where the content is primarily GTM (Phases 05, 11, 14) → GTM faculty voice.
Default: AI engineering faculty voice.

The persona is a voice register shift, not a personality change. The governed maze does not change. The vocabulary and examples shift to match the domain.

---

## What Was Cut (and Why)

**Professor Synapse fork:** discarded. Synapse is a blackbox persona built for general tutoring. Helix has a specific curriculum, a specific student, and a specific platform (Claude Code Desktop terminal). Inheriting Synapse's teaching philosophy would introduce hidden constraints that conflict with the governed-maze design. Building from scratch takes longer but gives us an auditable, fully owned system prompt.

**Open-ended conversation mode:** discarded. Helix does not have a free-form chat mode. All interactions flow through the decision tree. Students who want an open conversation use Claude Code directly.

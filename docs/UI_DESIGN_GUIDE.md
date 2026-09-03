# Dashboard Design System

The Streamlit interface uses a restrained life-sciences SaaS visual system designed for high-trust review work.

## Design principles

- **Clinical clarity over decoration:** critical decisions, evidence, status, and reviewer actions are visually prioritized.
- **Evidence before implementation detail:** human-readable citations appear first; raw JSON and traces remain available inside expanders.
- **Calm, high-trust palette:** navy conveys governance and stability, cobalt indicates action/navigation, teal indicates evidence/healthy system state, and amber is reserved for caution.
- **Progressive disclosure:** complex machine-readable payloads are hidden by default but remain available for auditability.
- **Consistent density:** 14–16 px corner radii, subtle borders, restrained shadows, and generous whitespace make dense PV workflows readable.

## Palette

- Ink / navigation: `#0B1220`
- Primary action: `#2563EB`
- Evidence / positive system state: `#0F9F8F`
- Safety notice: `#B7791F` on `#FFFAEB`
- Canvas: `#F5F7FB`
- Surface: `#FFFFFF`
- Border: `#E4E7EC`
- Primary text: `#111827`
- Secondary text: `#667085`

## Typography

The dashboard uses a local, dependency-free modern system stack:

`Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica, Arial, sans-serif`

Inter is used automatically when installed on the machine; otherwise the closest native UI font is selected. No font file is bundled.

## RAG presentation

RAG answers are intentionally separated into:

1. Grounded answer
2. Confidence and evidence count
3. Human-readable source cards with retrieval match
4. Advanced retrieval trace (collapsed by default)

Retrieval match is explicitly labeled as query similarity, not clinical certainty.

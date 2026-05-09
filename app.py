"""
Sunbird AI GenAI Application
Entry point for the Gradio web interface.

UI design follows the ElevenLabs-inspired design system:
- Off-white canvas, warm near-black ink
- Editorial serif display at weight 300
- Inter body with subtle tracking
- Atmospheric pastel gradient orbs
- Pill-shaped CTAs, soft card geometry
"""
import os
import tempfile

import gradio as gr
import requests
from dotenv import load_dotenv

from backend.pipeline import run_pipeline, SUPPORTED_LANGUAGES

load_dotenv()

# ---------------------------------------------------------------------------
# Design System — CSS
# ---------------------------------------------------------------------------
CUSTOM_CSS = r"""
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* =====================================================
   TOKENS
   ===================================================== */
:root {
  --canvas: #f5f5f5;
  --canvas-soft: #fafafa;
  --ink: #0c0a09;
  --primary: #292524;
  --primary-active: #0c0a09;
  --body: #4e4e4e;
  --body-strong: #292524;
  --muted: #777169;
  --muted-soft: #a8a29e;
  --hairline: #e7e5e4;
  --hairline-soft: #f0efed;
  --hairline-strong: #d6d3d1;
  --surface-card: #ffffff;
  --surface-strong: #f0efed;
  --on-primary: #ffffff;
  --gradient-mint: #a7e5d3;
  --gradient-peach: #f4c5a8;
  --gradient-lavender: #c8b8e0;
  --gradient-sky: #a8c8e8;
  --gradient-rose: #e8b8c4;
  --error: #dc2626;
  --success: #16a34a;
}

/* =====================================================
   BASE
   ===================================================== */
body, .gradio-container {
  background-color: var(--canvas) !important;
  color: var(--ink) !important;
  font-family: 'Inter', sans-serif !important;
  font-weight: 400 !important;
  letter-spacing: 0.16px !important;
  line-height: 1.5 !important;
}

.gradio-container {
  max-width: 1100px !important;
  margin: 0 auto !important;
  padding: 0 24px 96px !important;
}

/* =====================================================
   DISPLAY TYPOGRAPHY  (Waldenburg substitute)
   ===================================================== */
.editorial-display {
  font-family: 'Times New Roman', 'Georgia', serif !important;
  font-weight: 300 !important;
  color: var(--ink) !important;
  letter-spacing: -1.92px !important;
  line-height: 1.05 !important;
  font-size: 52px !important;
}

@media (min-width: 1024px) {
  .editorial-display {
    font-size: 64px !important;
  }
}

.editorial-subhead {
  font-family: 'Inter', sans-serif !important;
  font-weight: 400 !important;
  color: var(--body) !important;
  font-size: 16px !important;
  line-height: 1.5 !important;
  letter-spacing: 0.16px !important;
  max-width: 560px;
}

.section-head {
  font-family: 'Times New Roman', 'Georgia', serif !important;
  font-weight: 300 !important;
  color: var(--ink) !important;
  font-size: 32px !important;
  letter-spacing: -0.32px !important;
  line-height: 1.13 !important;
  margin-bottom: 24px !important;
}

/* =====================================================
   ATMOSPHERIC GRADIENT ORBS
   ===================================================== */
.orb-container {
  position: relative;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.55;
  pointer-events: none;
  z-index: 0;
}

.orb-mint {
  width: 320px;
  height: 320px;
  background: radial-gradient(circle, var(--gradient-mint), transparent 70%);
  top: -80px;
  left: -60px;
}

.orb-peach {
  width: 280px;
  height: 280px;
  background: radial-gradient(circle, var(--gradient-peach), transparent 70%);
  top: 40px;
  right: -40px;
}

.orb-lavender {
  width: 260px;
  height: 260px;
  background: radial-gradient(circle, var(--gradient-lavender), transparent 70%);
  bottom: -60px;
  left: 20%;
}

.orb-sky {
  width: 240px;
  height: 240px;
  background: radial-gradient(circle, var(--gradient-sky), transparent 70%);
  bottom: 20px;
  right: 10%;
}

/* =====================================================
   HERO BAND
   ===================================================== */
.hero-band {
  position: relative;
  padding: 96px 0 64px;
  text-align: center;
  margin-bottom: 48px;
}

.hero-band .editorial-display {
  position: relative;
  z-index: 1;
}

.hero-band .editorial-subhead {
  margin: 16px auto 0;
  position: relative;
  z-index: 1;
}

/* =====================================================
   CARDS  (surface-card, 1px hairline, rounded-xl)
   ===================================================== */
.sunbird-card {
  background-color: var(--surface-card) !important;
  border: 1px solid var(--hairline) !important;
  border-radius: 16px !important;
  padding: 24px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}

.sunbird-card-strong {
  background-color: var(--surface-card) !important;
  border: 1px solid var(--hairline-strong) !important;
  border-radius: 16px !important;
  padding: 32px !important;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04) !important;
}

/* =====================================================
   FORMS & INPUTS
   ===================================================== */
input, textarea, select,
.gr-form input, .gr-form textarea, .gr-form select,
.gr-text-input textarea, .gr-text-input input {
  background-color: var(--surface-card) !important;
  color: var(--ink) !important;
  border: 1px solid var(--hairline-strong) !important;
  border-radius: 8px !important;
  padding: 12px 16px !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 15px !important;
  font-weight: 400 !important;
  line-height: 1.47 !important;
  letter-spacing: 0.15px !important;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
}

input:focus, textarea:focus, select:focus,
.gr-form input:focus, .gr-form textarea:focus, .gr-form select:focus {
  border: 2px solid var(--ink) !important;
  outline: none !important;
  box-shadow: none !important;
}

/* Labels in caption-uppercase style */
label, .gr-input-label, .gr-radio-label, .gr-checkbox-label {
  font-family: 'Inter', sans-serif !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.96px !important;
  line-height: 1.4 !important;
  color: var(--muted) !important;
  margin-bottom: 8px !important;
}

/* =====================================================
   BUTTONS  (pill geometry)
   ===================================================== */
button, .gr-button {
  font-family: 'Inter', sans-serif !important;
  font-size: 15px !important;
  font-weight: 500 !important;
  line-height: 1.0 !important;
  letter-spacing: 0 !important;
  border-radius: 9999px !important;
  padding: 10px 24px !important;
  height: 40px !important;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

/* Primary ink pill */
button.primary, .gr-button-primary, .gr-button-variant-primary {
  background-color: var(--primary) !important;
  color: var(--on-primary) !important;
  border: none !important;
}
button.primary:hover, .gr-button-primary:hover {
  background-color: var(--primary-active) !important;
}

/* Secondary outline pill */
button.secondary, .gr-button-secondary, .gr-button-variant-secondary {
  background-color: transparent !important;
  color: var(--ink) !important;
  border: 1px solid var(--hairline-strong) !important;
}

/* =====================================================
   AUDIO PLAYER
   ===================================================== */
.gr-audio {
  border-radius: 16px !important;
  overflow: hidden !important;
  border: 1px solid var(--hairline) !important;
}

/* =====================================================
   RADIO & DROPDOWN
   ===================================================== */
.gr-radio, .gr-dropdown {
  background-color: var(--surface-card) !important;
  border: 1px solid var(--hairline) !important;
  border-radius: 8px !important;
}

.gr-radio-item {
  font-family: 'Inter', sans-serif !important;
  font-size: 15px !important;
  color: var(--ink) !important;
}

/* =====================================================
   OUTPUT TEXTBOXES
   ===================================================== */
.gr-textbox:disabled, .gr-textbox[data-disabled="true"] {
  background-color: var(--canvas-soft) !important;
  color: var(--body) !important;
}

/* =====================================================
   SECTION DIVIDERS
   ===================================================== */
.hairline-divider {
  border: none;
  border-top: 1px solid var(--hairline);
  margin: 48px 0;
}

/* =====================================================
   FOOTER
   ===================================================== */
.footer-text {
  color: var(--body) !important;
  font-size: 15px !important;
  line-height: 1.47 !important;
  letter-spacing: 0.15px !important;
  text-align: center;
  padding-top: 64px;
}

/* =====================================================
   SCROLLBAR (subtle)
   ===================================================== */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: var(--canvas-soft);
}
::-webkit-scrollbar-thumb {
  background: var(--hairline-strong);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--muted-soft);
}
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _download_audio(url: str) -> str:
    """Download remote audio to a temporary local file and return its path."""
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp.write(response.content)
    tmp.close()
    return tmp.name


def process(
    input_mode: str,
    text_input: str,
    audio_input: str,
    target_language: str,
    progress=gr.Progress(),
):
    """
    Gradio handler that runs the pipeline and surfaces intermediate updates
    with a progress bar.
    """
    if not os.environ.get("SUNBIRD_API_TOKEN"):
        raise gr.Error(
            "SUNBIRD_API_TOKEN is not set. Please add it to your .env file or environment."
        )

    progress(0.1, desc="Validating input…")

    try:
        original, transcript, summary, translation, audio_url = run_pipeline(
            input_mode=input_mode,
            text_input=text_input,
            audio_input=audio_input,
            target_language=target_language,
        )
    except ValueError as exc:
        raise gr.Error(str(exc))
    except requests.HTTPError as exc:
        raise gr.Error(f"Sunbird API error: {exc}")
    except Exception as exc:
        raise gr.Error(f"Unexpected error: {exc}")

    progress(0.85, desc="Fetching synthesised audio…")

    local_audio_path = None
    if audio_url:
        try:
            local_audio_path = _download_audio(audio_url)
        except Exception as exc:
            gr.Warning(f"Could not retrieve audio: {exc}")

    progress(1.0, desc="Done")

    return original, transcript, summary, translation, local_audio_path


def toggle_inputs(mode: str):
    """Return visibility updates based on the selected input mode."""
    if mode == "audio":
        return (
            gr.update(visible=False),   # text_input
            gr.update(visible=True),    # audio_input
            gr.update(visible=True),    # transcript_box
        )
    return (
        gr.update(visible=True),    # text_input
        gr.update(visible=False),   # audio_input
        gr.update(visible=False),   # transcript_box
    )


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="Sunbird AI GenApp") as demo:

    # ---------- HERO BAND ----------
    gr.HTML(
        """
        <div class="orb-container hero-band">
            <div class="orb orb-mint"></div>
            <div class="orb orb-peach"></div>
            <div class="orb orb-lavender"></div>
            <div class="orb orb-sky"></div>
            <h1 class="editorial-display">Sunbird AI GenApp</h1>
            <p class="editorial-subhead">
                Summarise and translate text or audio into Ugandan local languages.
                Powered by Sunbird AI.
            </p>
        </div>
        """
    )

    # ---------- MAIN WORKSPACE ----------
    with gr.Row():
        # --- INPUT COLUMN ---
        with gr.Column(scale=1, min_width=320):
            gr.HTML('<h2 class="section-head">Input</h2>')

            with gr.Column(elem_classes="sunbird-card"):
                input_mode = gr.Radio(
                    choices=["text", "audio"],
                    value="text",
                    label="Input type",
                )

                text_input = gr.Textbox(
                    label="Enter text",
                    placeholder="Paste or type the text you want to summarise and translate…",
                    lines=8,
                    visible=True,
                    show_label=True,
                )

                audio_input = gr.Audio(
                    label="Upload audio",
                    type="filepath",
                    visible=False,
                )

            with gr.Column(elem_classes="sunbird-card"):
                target_language = gr.Dropdown(
                    choices=SUPPORTED_LANGUAGES,
                    value="Luganda",
                    label="Target language",
                )

                run_btn = gr.Button("Process", variant="primary")

        # --- OUTPUT COLUMN ---
        with gr.Column(scale=1, min_width=320):
            gr.HTML('<h2 class="section-head">Results</h2>')

            with gr.Column(elem_classes="sunbird-card-strong"):
                original_text = gr.Textbox(
                    label="Original text / Transcript",
                    lines=5,
                    interactive=False,
                )

                transcript_box = gr.Textbox(
                    label="Transcript (audio only)",
                    lines=3,
                    interactive=False,
                    visible=False,
                )

                summary_box = gr.Textbox(
                    label="Summary",
                    lines=4,
                    interactive=False,
                )

                translation_box = gr.Textbox(
                    label="Translated summary",
                    lines=4,
                    interactive=False,
                )

            with gr.Column(elem_classes="sunbird-card"):
                audio_output = gr.Audio(
                    label="Synthesised speech",
                    interactive=False,
                    autoplay=False,
                )

    # ---------- FOOTER ----------
    gr.HTML(
        """
        <hr class="hairline-divider">
        <p class="footer-text">
            Built for the Sunbird AI Internship Assessment.<br>
            All AI capabilities are powered by the Sunbird AI API.
        </p>
        """
    )

    # ---------- EVENT WIRING ----------
    input_mode.change(
        fn=toggle_inputs,
        inputs=input_mode,
        outputs=[text_input, audio_input, transcript_box],
    )

    run_btn.click(
        fn=process,
        inputs=[input_mode, text_input, audio_input, target_language],
        outputs=[original_text, transcript_box, summary_box, translation_box, audio_output],
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
        css=CUSTOM_CSS,
    )

# Deploying ORBIT on Streamlit Community Cloud

This guide is for running the same ORBIT that works on the laptop as a public web app.
Deploying publishes the app under your own Streamlit account, so it's a step you take yourself.

## 1. What's the same, and what's different online

| | On the laptop | On Streamlit Community Cloud |
|---|---|---|
| Emotion model | Downloaded once into the Hugging Face cache | Downloaded when the server starts (~125 MB) |
| Safety rules, crisis reply | Identical | Identical |
| Where data is saved | `data/orbit.db` on this computer, kept | A **temporary database for each browser session**, deleted within 24 hours |
| Companion replies | Templates, or Ollama if installed | Templates, or Claude if a key is added (Ollama isn't available) |
| Offline demo mode | Available | Available |

ORBIT detects that it's on Streamlit Cloud by its install folder (`/mount/src/`), and then
switches storage to session mode automatically. To test session mode on the laptop, set the
environment variable `ORBIT_STORAGE=session` before running the app.

## 2. Storage and the privacy trade-off

Streamlit Community Cloud doesn't keep files: the server can restart at any time, and the
disk is shared by everyone using the app. A single `orbit.db` would therefore (a) lose data
and (b) mix different visitors' journals together. That isn't acceptable for a wellbeing app.

So online, every browser session gets **its own** small database file, named with a random
session id. Nobody else can see it, and it's deleted when it's more than 24 hours old. A browser session is one open tab: **refreshing the page or opening a new tab starts a fresh, empty session.** The trade-off:

- **Privacy:** better. Nothing is kept long-term, and nothing is linked to a name or account.
- **Convenience:** worse. Closing the tab ends the journal. To keep it, go to
  **Settings (top right) → Download my data**. This saves a `.json` file to your own device;
  **Import** brings it back next time.
- **The downloaded file contains journal text.** Keep it private. ORBIT never uploads it anywhere.
- Crisis messages are never stored, online or offline.
- While a session is active, its data does exist on Streamlit's server (that's how any web app
  works). If that isn't acceptable, run ORBIT locally, where nothing leaves the computer.

## 3. Optional cloud AI replies (Claude)

Without a key, ORBIT's replies come from its own templates, which work everywhere. With a key,
it can write warmer replies using Anthropic's Claude.

- Add the key in **App settings → Secrets** (format in `.streamlit/secrets.toml.example`).
  Never put a key in the code or in GitHub.
- **Users must opt in** (in Settings, top right). Without consent, nothing is sent.
- When it's on, the user's message (and the last few chat messages) **is sent to Anthropic**
  to write the reply. That's a real privacy trade-off, and the app says so.
- Default model: `claude-opus-5-5`. Set `ORBIT_CLOUD_MODEL = "claude-haiku-5-5"` for a cheaper,
  faster model. The request asks for low effort and short replies, and turns on server-side
  fallbacks, so another model can answer if the chosen one is temporarily overloaded.

Safeguards (in `llm.py` and `companion.py`):
1. **Crisis messages never reach any AI.** The deterministic safety check runs first, and a crisis
   always gets the fixed reply with Tele-MANAS 14416 / 1-800-891-4416 and 112.
2. **Prompt-injection guard.** Messages that try to change ORBIT's instructions ("ignore previous
   instructions", "system prompt", "you are now…") skip the AI and get a template reply. User
   text is wrapped in `<user_message>` tags with angle brackets escaped, so it can't close the tag.
3. **Output check.** A reply is rejected (and a template is used instead) if it claims to be a human
   or a therapist, mentions a diagnosis, is too long, or trips the safety rules.
4. Any error or timeout also falls back to templates, so the app never breaks.

## 4. Memory

The emotion model is loaded lazily (only when the first message is analysed) and cached once per
server with `@st.cache_resource`, so all visitors share one copy.

Measured on the development laptop (Windows, Python 3.12) after the model was loaded and one
check-in was analysed: the Streamlit process used **about 277 MB** (peak 293 MB).
Streamlit's documentation lists Community Cloud limits of **690 MB minimum and 2.7 GB maximum**
memory ("as of February 2024, subject to change"). ORBIT fits within the minimum with room to
spare. Linux memory use will be somewhat different from Windows; check **Manage app → logs**
after deploying.

If the model can't be downloaded (no internet, or Hugging Face is down), ORBIT switches to
**offline demo mode** automatically and shows a banner. It doesn't crash.

## 5. Steps

1. Push the code to GitHub. `data/orbit.db`, `secrets.toml` and the personal model are git-ignored.
2. Go to share.streamlit.io, choose **Create app**, pick the repository, branch `main` and file `app.py`.
3. Under **Advanced settings**, choose **Python 3.12**.
4. (Optional) Paste the secrets from `.streamlit/secrets.toml.example` with a real key.
5. Deploy, then test: the landing page, a check-in, a crisis phrase (it should show the
   helplines only), Download my data, and offline demo mode.

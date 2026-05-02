# Onward — Design Decisions

A living document capturing key design decisions for the Onward desktop app. Updated as decisions are made.

> **Working title:** The app is currently called "Onward" and uses the `.onward` file extension. The final name will be revisited before any App Store release.

---

## System Requirements

| Platform | Minimum Version | Architecture |
|----------|----------------|--------------|
| macOS | 13.0 (Ventura) | Apple Silicon (ARM) only |
| Windows | Windows 10 | x64 |

The macOS 13 minimum is a hard requirement imposed by Qt (the framework underlying PySide6) and cannot be worked around. Onward will not launch on macOS 12 Monterey or earlier. Intel Mac support has been set aside for now — the app is built for Apple Silicon only. Intel support can be revisited in the future if there is demand.

---

## Project File Format

### `.onward` as a folder bundle
Onward projects are stored as folder bundles with the `.onward` extension, modeled after Scrivener's `.scriv` format.

- On Mac, folder bundles currently appear as regular folders in Finder. They will appear as opaque single objects once the `.onward` file type is registered with macOS (see File type association below).
- On Windows, users can navigate inside them in File Explorer, but this is a cosmetic difference rather than a functional one
- Double-clicking a `.onward` file/folder opens the project in Onward on both platforms

**File type association:**
- **Mac:** Declared in `Info.plist` inside the `.app` bundle via `CFBundleDocumentTypes`. Can be added directly to `onward.spec` in the existing `info_plist` section. macOS registers the association on first app launch.
- **Windows:** Stored in the system registry. Requires either a proper installer (e.g. NSIS or Inno Setup) or the app writing registry entries on first launch. Not handled automatically by PyInstaller. More complex than Mac — tackle Mac first.

**Project location:** `~/Documents/Onward/[projectname].onward/`

**Top-level Onward directory:**
```
~/Documents/Onward/
    my-novel.onward/
    another-project.onward/
```

**Inside a project bundle:**
```
my-novel.onward/
    my-novel.csv        ← submitted entries
    autosave.tmp        ← crash recovery, only present mid-session
```

---

## Settings

User preferences are saved globally to `~/Documents/Onward/settings.json` and applied on every launch. Settings are accessible via the Settings button in the sidebar and include:

- **Font** — Sans Serif (IBM Plex Sans), Serif (IBM Plex Serif), Monospace (IBM Plex Mono). Each option is previewed in its own typeface.
- **Size** — Small (12pt), Medium (16pt), Large (20pt). All UI elements scale uniformly with the selected size, including the editor, sidebar, and dialogs. Large Print support was added in response to a user with vision problems.
- **Mode** — Light or Dark.

All settings support live preview — changes are applied immediately and reverted if the user cancels.

`settings.json` uses a merge-on-write strategy — saving any subset of settings preserves all other keys. This ensures that settings added by different parts of the app (e.g. `recent_projects` added by the launch screen) are never accidentally overwritten.

---

## Plain Text

Onward is a plain text app. Rich text formatting (bold, italic, underline) is not supported. Paste events strip formatting — only plain text is accepted in both the main editor and the summary input. Export TXT produces a clean plain text file.

This decision may be revisited in the future if users request it. If rich text is added, markdown is the preferred approach — it stores cleanly as plain text in the CSV and exports naturally as `.txt` without requiring a format change.

---

## File Roles

| File | Purpose |
|------|---------|
| `[projectname].csv` | The canonical data store — submitted entries, timestamps, word counts, summaries |
| `autosave.tmp` | Crash recovery only — a plain text file containing the raw contents of the editor at the time of the last autosave. Written periodically during a session, deleted on clean Submit or clean exit. |

---

## Save & Submit Flow

- Writing lives in the editor until the user clicks **Submit & Clear**
- On Submit, the editor becomes read-only and a modal summary dialog appears — the editor remains visible behind it
- The summary dialog contains a text input for notes, a character count, and Cancel and Submit buttons
- On Submit, the entry is written to `[projectname].csv` and the editor is cleared
- The summary dialog can be dismissed via Cancel or Submit (there is no X button — it is a modal dialog)
- `autosave.tmp` is written to disk periodically during a session (e.g. every few minutes) for crash recovery only
- On clean Submit or clean exit, `autosave.tmp` is deleted
- On next launch, if `autosave.tmp` exists, the app offers to recover the unsaved entry

---

## First Launch & Project Management

- On first launch and all subsequent launches, the app shows a screen with three options: **New Project**, **Open Project**, and **Import**
- **New Project** — opens a dialog prompting the user to enter a project name, then creates a new `.onward` bundle and opens the main writing window.
- **Open Project** uses a platform-specific file picker — on Mac, the native picker is used with an `*.onward` filter (enabled by file type registration); on Windows, a directory picker is used since `.onward` bundles are folders. In both cases the user navigates to and selects a `.onward` bundle.
- **Import** — see Import section below.

### Recent Projects

The launch screen shows up to 5 recently opened projects alongside the three primary buttons. On first launch (no recent projects), the buttons are centered as usual. On subsequent launches, the buttons shift left, a vertical divider appears, and the recent projects list appears on the right as a secondary column.

- Recent projects are stored in `settings.json` under a `recent_projects` key — a list of up to 5 dicts, each with `name` and `path`
- Every time a project is opened, created, or imported, it is prepended to the list and the list is trimmed to 5
- On load, each path is validated against disk — stale entries (moved or deleted projects) are silently dropped
- Project names in the list are truncated with `...` using font-aware metrics, so the truncation point respects the user's chosen font and size
- The full name is available as a tooltip on hover

---

## Project Naming

- Users choose a project name when creating a new project or importing files
- The project name determines the folder name: `[projectname].onward/`
- Duplicate names are not allowed — if a folder with that name already exists, the app shows an error: "A project with that name already exists."
- The user is responsible for differentiating (e.g. adding a number or subtitle)

---

## Import

Import lives on the launch screen alongside New Project and Open Project. The flow is: select file → validate → enter project name → open main window.

- **Import CSV** — accepts a CSV file previously exported by Onward (validated by fieldnames). Creates a new `.onward` bundle from the imported data. Also supports migrating projects from the original Streamlit version of the app. The editor opens blank — the user continues writing as normal.
- **Import TXT** — accepts any plain text file. Creates a new `.onward` bundle and loads the TXT contents into the editor. The user still needs to click Submit & Clear to save the content and add a summary.

Import is not available from within the main writing window — it is a launch-time action only.

---

## Sidebar

The sidebar is a right-side panel that pushes the writing area when open — the writing area shrinks to avoid overlap. A pill-shaped chevron button (`❯❯` / `❮❮`) floats in the top-right corner of the writing area. It uses the same background, hover, and text colors as the sidebar buttons. Clicking it slides the sidebar in from the right; clicking anywhere outside the sidebar, or clicking the pill again, slides it back out. The animation uses `QPropertyAnimation` with an `OutCubic` easing curve, animating both the sidebar and the writing area simultaneously. The project name is shown in the window title bar rather than in the toggle itself.

The sidebar contains:
- Word count
- Submit & Clear
- View Summary (visible only after first submission)
- Export Work (visible only after first submission)
- Settings
- Send Feedback (bottom-aligned, visually separated from action buttons)
- Home (bottom-aligned, below Send Feedback and Settings)

**Send Feedback** opens a mailto link to the app's feedback address. No third-party form service is used — the user's own mail client handles the interaction.

**Home** returns the user to the launch screen (New Project / Open Project / Import). If the user has an unsaved entry, a confirmation dialog appears first. The current project is not affected — it remains in `~/Documents/Onward/` as its own `.onward` bundle.

---

## Export

Two distinct export actions, both producing standalone files the user saves wherever they choose:

| Export | Output | Purpose |
|--------|--------|---------|
| Export TXT | `[projectname].txt` | Compiled plain text of all entries — for sharing, editing elsewhere, or submitting to a publisher |
| Export CSV | `[projectname]-[timestamp].csv` | Full raw data export including entries, timestamps, word counts, and summaries — for backup or migration |

Export CSV is distinct from the internal `.onward` format. It is a portable, human-readable snapshot of all project data.

---

## Stylesheets

All styling flows through two functions:

- **`base_stylesheet(font_family, font_size)`** — the single source of truth for all shared styles: the main window, editor, sidebar buttons, dialogs, inputs, scrollbars, and the `muted` label style.
- **`launch_stylesheet(font_family, font_size)`** — calls `base_stylesheet` and appends the four launch-specific rules: `launchWidget` background, `launchTitle`, `launch-btn`, and `recent-btn`.

This consolidation means any shared style change (e.g. dialog button padding) has exactly one place to be made.

---

## Easter Eggs

### Frankenstein (Cmd+Shift+F)
Pastes the next paragraph of Mary Shelley's *Frankenstein* (Chapter 5, public domain) into the editor. Cycles through paragraphs on repeated presses. Primarily a QA tool for testing Submit & Export with realistic content.

---

## File Mental Model (for users)

| Format | What it is |
|--------|-----------|
| `.onward` | Onward's working format — how your project is stored while you use the app |
| `.txt` | How you share your writing with the world |
| `.csv` | How you back up or migrate your full project data |

---

## Known Limitations & Testing Notes

- **Open Project on Mac (built app)** — the native file picker with `.onward` file type registration has not been tested in the built `.app` yet. When running `onward.py` directly on Mac, file type registration is not active, so this can only be verified in a GitHub Actions build. Testing is pending access to a Mac running macOS 13+ where the built app can be launched.
- **Full flow on Mac ARM (built app)** — the complete app flow (New Project, Open Project, Import, Submit, Export, autosave recovery) has been tested running `onward.py` directly on ARM Mac but not as a built `.app` from GitHub Actions. Should be verified once a built `.app` can be tested on an ARM Mac running macOS 13+.
- **Autosave recovery on Mac** — autosave and crash recovery have been tested on Windows only. Should be verified on Mac.

---

## Future Considerations

**Project renaming** — Renaming a project from within the app would require renaming the `.onward` bundle on disk, updating any open file handles, and updating the window title and toggle row. Doable but non-trivial.

**AI-generated summaries** — Users could optionally have summaries generated automatically by AI rather than writing them manually. Tabled for the long term.

**Keyboard shortcuts** — A writing app should be fully keyboard-accessible. Submit, toggle sidebar, and Home at minimum. Qt's `QShortcut` makes this straightforward.

**Submit without summary (keyboard shortcut)** — A shortcut to submit with no summary, bypassing the dialog entirely, would reduce friction for power users writing daily. The "or not — that's okay, too!" copy in the dialog already acknowledges this friction.

**Accent colour** — Everything is intentionally neutral grey, which suits the writing-first aesthetic. A single accent colour used very sparingly — perhaps just the Submit button — could add life and visually prioritise the most important action without compromising the minimalist feel. Worth revisiting.

**Live word count** — A session word count visible in the editor as you type has been considered and deliberately set aside. The concern is that it encourages writers to think about their work quantitatively rather than qualitatively. Fifty hard-won words that unlock a story are worth more than five hundred easy ones, and a visible counter might make a productive session feel like a failure. If this is ever added, it should be a toggleable option in Settings, off by default.

**About screen** — An About button in the sidebar would give the app a sense of completeness. It could show the app name, version number, a one-line description, and the philosophy behind Onward. Professional apps have About screens, and it's a natural place to surface the "write forward, don't look back" idea for curious users.

**GitHub README** — A repo-level README explaining what Onward is, why it exists, how to download and run it, and a screenshot. Worth doing before any public release or sharing. The About screen copy would provide a good head start.

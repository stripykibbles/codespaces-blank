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

## File Roles

| File | Purpose |
|------|---------|
| `[projectname].csv` | The canonical data store — submitted entries, timestamps, word counts, summaries |
| `autosave.tmp` | Crash recovery only — a plain text file containing the raw contents of the editor at the time of the last autosave. Written periodically during a session, deleted on clean Submit or clean exit. |

---

## Save & Submit Flow

- Writing lives in the editor until the user clicks **Submit & Clear**
- On Submit, the entry is written to `[projectname].csv` and the editor is cleared
- `autosave.tmp` is written to disk periodically during a session (e.g. every few minutes) for crash recovery only
- On clean Submit or clean exit, `autosave.tmp` is deleted
- On next launch, if `autosave.tmp` exists, the app offers to recover the unsaved entry

---

## First Launch & Project Management

- On first launch and all subsequent launches, the app shows a screen with three options: **New Project**, **Open Project**, and **Import**
- **New Project** — opens a dialog prompting the user to enter a project name, then creates a new `.onward` bundle and opens the main writing window.
- **Open Project** uses a platform-specific file picker — on Mac, the native picker is used with an `*.onward` filter (enabled by file type registration); on Windows, a directory picker is used since `.onward` bundles are folders. In both cases the user navigates to and selects a `.onward` bundle.
- **Import** — see Import section below.

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

The sidebar is hidden by default, giving the writing area the full window width — similar to writing in Notepad. It is triggered by a small button or icon in the corner of the writing area.

- **Trigger:** A small button/icon in the top-left corner of the writing area
- **Appearance:** Slides in and overlays the writing area (does not push or resize it)
- **Dismissal:** Clicking the trigger button again, or clicking anywhere outside the sidebar
- **Animation:** Smooth slide-in/slide-out using `QPropertyAnimation`

The sidebar contains: project name display, word count, Submit & Clear, View Summary, Export Work, and Settings.

---

## Export

Two distinct export actions, both producing standalone files the user saves wherever they choose:

| Export | Output | Purpose |
|--------|--------|---------|
| Export TXT | `[projectname].txt` | Compiled plain text of all entries — for sharing, editing elsewhere, or submitting to a publisher |
| Export CSV | `[projectname]-[timestamp].csv` | Full raw data export including entries, timestamps, word counts, and summaries — for backup or migration |

Export CSV is distinct from the internal `.onward` format. It is a portable, human-readable snapshot of all project data.

---

## File Mental Model (for users)

| Format | What it is |
|--------|-----------|
| `.onward` | Onward's working format — how your project is stored while you use the app |
| `.txt` | How you share your writing with the world |
| `.csv` | How you back up or migrate your full project data |

---

## Implementation Order & Dependencies

The planned changes have a clear dependency chain — each step unlocks the next:

1. ✅ **Project naming UI** — the user needs a way to enter a project name. Everything else depends on this.
2. ✅ **First launch / New Project / Open Project / Import screen** — this is where project naming happens.
3. ✅ **`.onward` folder structure + file paths** — once the project name is known, create `~/Documents/Onward/[projectname].onward/` and route the CSV there. Replaces the current hardcoded `novel.csv` path.
4. ✅ **Autosave** — periodic writes to `autosave.tmp` and crash recovery flow on launch.
5. ✅ **Export/Import updates** — Export TXT and Export CSV use the new paths and naming conventions. Import moved to launch screen.
6. ✅ **Sidebar refactor** — persistent sidebar replaced with an animated overlay panel triggered by a << button in the top-left corner of the writing area. Slides in/out with a smooth animation, dismissed by clicking >> or anywhere outside the sidebar.

---

## Known Limitations & Testing Notes

- **Open Project on Mac (built app)** — the native file picker with `.onward` file type registration has not been tested in the built `.app` yet. When running `onward.py` directly on Mac, file type registration is not active, so this can only be verified in a GitHub Actions build. Testing is pending access to a Mac running macOS 13+ where the built app can be launched.
- **Full flow on Mac ARM (built app)** — the complete app flow (New Project, writing, submitting, Open Project, autosave recovery) has been tested by running `onward.py` directly on ARM Mac, but not in the built `.app` from GitHub Actions. Worth downloading and testing the full flow in the built app.
- **Autosave recovery on Mac** — crash recovery has been verified on Windows but not yet tested on Mac.
- **Full flow testing on Mac ARM (built app)** — the complete app flow (New Project, Open Project, Import, Submit, Export, autosave recovery) has been tested running `onward.py` directly on ARM Mac but not as a built `.app` from GitHub Actions. Should be verified once a built `.app` can be tested on an ARM Mac running macOS 13+.
- **Autosave recovery on Mac** — autosave and crash recovery have been tested on Windows only. Should be verified on Mac.

---

## Decisions Still Pending

- Where exactly is the project name displayed in the UI?
- Font options and dark mode — where do these live in the UI?
- Should users have the option to have summaries generated automatically by AI, rather than writing them manually?
- Should the editor support rich text formatting (bold, italic, underline)? This would affect how entries are stored, displayed, and exported, and would determine whether RTF should be supported as an import/export format.
- Should users be able to start a new project from within the main writing window (without having to quit and relaunch)? If so, where does this option live in the UI?

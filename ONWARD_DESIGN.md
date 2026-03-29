# Onward — Design Decisions

A living document capturing key design decisions for the Onward desktop app. Updated as decisions are made.

> **Working title:** The app is currently called "Onward" and uses the `.onward` file extension. The final name will be revisited before any App Store release.

---

## System Requirements

| Platform | Minimum Version |
|----------|----------------|
| macOS | 13.0 (Ventura) |
| Windows | Windows 10 |

The macOS 13 minimum is a hard requirement imposed by Qt (the framework underlying PySide6) and cannot be worked around. Onward will not launch on macOS 12 Monterey or earlier.

---

## Project File Format

### `.onward` as a folder bundle
Onward projects are stored as folder bundles with the `.onward` extension, modeled after Scrivener's `.scriv` format.

- On Mac, folder bundles appear as opaque single objects in Finder
- On Windows, users can navigate inside them in File Explorer, but this is a cosmetic difference rather than a functional one
- Double-clicking a `.onward` file/folder opens the project in Onward on both platforms

**File type association:**
- **Mac:** Declared in `Info.plist` inside the `.app` bundle via `CFBundleDocumentTypes`. Can be added directly to `onward.spec` in the existing `info_plist` section. macOS registers the association on first app launch.
- **Windows:** Stored in the system registry. Requires either a proper installer (e.g. NSIS or Inno Setup) or the app writing registry entries on first launch. Not handled automatically by PyInstaller. More complex than Mac (tackling Mac first).

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

## Export

Two distinct export actions, both producing standalone files the user saves wherever they choose:

| Export | Output | Purpose |
|--------|--------|---------|
| Export TXT | `[projectname].txt` | Compiled plain text of all entries — for sharing, editing elsewhere, or submitting to a publisher |
| Export CSV | `[projectname]-[timestamp].csv` | Full raw data export including entries, timestamps, word counts, and summaries — for backup or migration |

Export CSV is distinct from the internal `.onward` format. It is a portable, human-readable snapshot of all project data.

---

## Import

- **Import CSV** — accepts a CSV file previously exported by Onward (validated by fieldnames). Creates a new `.onward` bundle from the imported data. Also supports migrating projects from the original Streamlit version of the app.
- **Import TXT** — adds the contents of a TXT file to the current editor. The user still needs to Submit to save it.

---

## Project Naming

- Users choose a project name on first launch or when creating a new project
- The project name determines the folder name: `[projectname].onward/`
- Duplicate names are not allowed — if a folder with that name already exists, the app shows an error: "A project with that name already exists."
- The user is responsible for differentiating (e.g. adding a number or subtitle)

---

## First Launch & Project Management

- On first launch and all subsequent launches, the app shows a **New Project / Open Project** screen
- **Open Project** uses a standard OS file picker — the user navigates to and selects a `.onward` bundle
- Double-clicking a `.onward` file from Finder or File Explorer also opens it directly in Onward
- **Start New Project** — if the user already has an active project, a simple confirmation dialog fires ("Are you sure you want to start a new project?") to prevent accidental clicks. The existing project is not affected — it remains in `~/Documents/Onward/` as its own `.onward` bundle.

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

1. **Project naming UI** — the user needs a way to enter a project name. Everything else depends on this.
2. **First launch / New Project / Open Project screen** — this is where project naming happens. Comes immediately after or alongside #1.
3. **`.onward` folder structure + file paths** — once the project name is known, create `~/Documents/Onward/[projectname].onward/` and route the CSV there. Replaces the current hardcoded `novel.csv` path.
4. **Autosave** — once the file structure is in place, add periodic writes to `autosave.tmp` and the crash recovery flow on launch.
5. **Export/Import updates** — once the file structure is settled, update Export TXT and Export CSV to use the new paths and naming conventions.
6. **Sidebar refactor** — tackle last, once all the above is in place and it's clear exactly what options need to live in it (project name display, new project, open project, submit, view summary, export, import, settings).

---

## Decisions Still Pending

- Where exactly is the project name displayed in the UI?
- What does the sidebar/menu look like after the persistent sidebar is refactored?
- Font options and dark mode — where do these live in the UI?
- Should users have the option to have summaries generated automatically by AI, rather than writing them manually?

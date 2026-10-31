---
name: chatgpt-image-assets
description: Use for ANY request to create, generate, draw, design, render, edit or redo an image or visual asset, in any wording or language (e.g. "tạo ảnh", "vẽ", "make a picture", "generate an icon", "design a logo", "background", "illustration", "sprite", "UI mockup", "concept art", "banner", "thumbnail", "remove the background"). Claude cannot generate raster images itself, so this skill drives ChatGPT image generation in the built-in browser, one prompt per asset, then reviews, downloads and files the results (into a Unity project's Assets when there is one).
---

# ChatGPT image assets

Claude cannot produce raster images itself. For any image request, drive chatgpt.com in the built-in browser to turn a brief into images, one prompt ("tag") per image or asset, then bring the results into the user's project.

Proven on the Jelly Buddies UI pass in ForkNBacon: 13 tags, prompts in `Assets/_Game/_Docs/ArtPrompts/chatgpt-ui-prompts.md`, output in `Assets/_Game/_Base/Textures/UI/chatgpt_generated/`. The Unity paths below are that project's conventions. In another project, use its own asset folders. With no project, save to a folder the user names.

**Quick requests** (one image, e.g. "vẽ cho tôi một con mèo"): skip the prompt file. Write one prompt, show it, get a yes, send it, review it and offer to download. Use the full workflow for sets of assets.

Claude cannot call ChatGPT directly: everything goes through the user's own signed-in ChatGPT tab.

## Ground rules (ask before acting)

1. **Sending prompts posts on the user's account.** Show or link the prompt file and get an explicit yes before the first send. One yes covers the listed tags; a new or rewritten prompt that the user did not ask for needs another yes.
2. **The user signs in themself.** Never type credentials. Decline non-essential cookies on the consent banner.
3. **Downloading is a separate approval.** Ask before saving any image to disk, naming the files and target folder.
4. ChatGPT cannot see project files (no upload tool in the built-in browser), so describe reference art in words. Expect drift from the existing art.

## Workflow

### 1. Write the prompt file

Create `Assets/_Game/_Docs/ArtPrompts/<topic>-prompts.md` from `templates/prompt-template.md`:

- **Tag 00 = style block + UI kit.** States the style once for the whole chat: resolution and orientation, outline color and thickness, highlight/shadow rules, hex palette, character description, and "NO text, letters or numbers anywhere". Later tags start with "Same style."
- **One tag per screen/popup**, written as layout instructions: background, top/center/bottom, what each element looks like. Leave buttons and ribbons blank; text is rendered by TextMeshPro.
- **Sprite sheets must be strict**: say "Draw ONLY these N items, nothing else", list them row by row, and name things to exclude. A loose list makes ChatGPT add stars, trophies, boosters, chests and other filler.
- Ask for "fully transparent background (PNG alpha), no frame, no floor shadow, wide transparent gaps" whenever the output will be cut into sprites. Full-screen mockups keep their background.
- Settle open art-direction questions (which character design, which skins are in scope) with the user before writing.

### 2. Open ChatGPT

Load the `anthropic-skills:built-in-browser` skill, then `preview_start` with `url: https://chatgpt.com`. If a cookie banner shows, click "decline non-essential" (Vietnamese UI: "Từ chối cookie không thiết yếu"). If not signed in, call `tabs_context`; if the pane is hidden ask the user to press Ctrl+Shift+B (Cmd+Shift+B on Mac), then ask them to sign in and confirm.

### 3. Send tags one at a time, in one conversation

Keep every tag in the same chat so the style carries over. Run `python ~/.claude/skills/chatgpt-image-assets/scripts/flatten_prompts.py <prompts.md> <out.json>` first: **a newline in `type` presses Enter and sends early**, so each prompt must be one line. Prefix each message with `Tag NN - ScreenName.` so images can be mapped back later.

Per tag, one `browser_batch`:

1. `computer left_click` on the composer (`find "Hỏi ChatGPT"` / "Ask anything", or the coordinate from the last screenshot)
2. `computer type` the flattened prompt
3. `computer key Return`
4. `computer wait 5`
5. Two `javascript_tool` calls running the wait snippet from `references/browser-snippets.md`. **Each JS call times out at 45 s**, so poll ≤38 s per call and chain calls; image generation takes 15–60 s.

Several tags can go in one batch. A turn is finished when its reply shows the image "Edit" button ("Chỉnh sửa"). The page virtualizes old turns, so counting `<img>` elements is unreliable; read the tail of `main.innerText` instead.

### 4. Review before downloading

- Scroll the newest image into view and take a screenshot. The image's "Edit" overlay can hide the bottom-left corner, so use the row-segmentation snippet to count items per row against the prompt.
- Check transparency with the alpha snippet (`transparentPct` well above 0 means real alpha, not a painted checkerboard).
- Report what matches, what is missing or extra, and size/orientation. Re-prompt only with the user's go-ahead, using a stricter tag such as `Tag 00c`.

Observed output sizes: portrait mockups 1024×1536 or 853×1844, landscape sheets 1536×1024. They are never the requested 1080×2340, so plan to rescale.

### 5. Download (after approval)

Use the download snippet. It scrolls the chat container top to bottom, maps each image to its tag by walking back to the nearest `Tag NN -` text (the first prompt maps to `00`), fetches the blob and clicks an `<a download>`, recording `{tag: byteSize}` in `window.__got`. One call may not reach the bottom in 36 s; call again with the remaining tags.

Files land in `~/Downloads`, first as `<guid>.tmp` and later renamed to the chosen name. Then run:

```bash
python ~/.claude/skills/chatgpt-image-assets/scripts/collect_downloads.py '<json of window.__got>' '<names json>' Assets/_Game/_Base/Textures/UI/<folder>
```

It matches files by exact byte size (either name form), checks the PNG signature, moves them as `<tag>_<Name>.png` and prints dimensions and whether each has alpha.

### 6. Put into Unity

- Target folder: `Assets/_Game/_Base/Textures/UI/<snake_case_folder>/` next to `complete_popup`, `failed_popup` and the others.
- When moving files that Unity already imported, move each `.meta` with its asset (and `<folder>.meta` with the folder) so GUIDs stay the same.
- Sheets meant for slicing: Texture Type Sprite, Sprite Mode Multiple, then slice in the Sprite Editor. Mockups are reference only.
- Do not commit unless asked.

## Gotchas

- ChatGPT's Vietnamese UI labels: stop button `aria-label="Ngừng"`, composer "Hỏi ChatGPT", edit button "Chỉnh sửa". For English use "Stop", "Ask anything", "Edit".
- "Same as the previous popup" works for small variants and saves tokens.
- Asking to "remove the background" makes ChatGPT redraw the image, not edit it, so recheck the content as well as the alpha.

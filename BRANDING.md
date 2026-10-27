# Wusel branding

The owner selected the first hedgehog concept: petrol body, cream face and ochre ear/feet. The unchanged generated PNG is retained at `wusel/static/wusel-logo.png`. Exports trim transparent margins and resize for their destination; they do not redraw or regenerate the animal. The source was produced with the built-in image-generation tool and then explicitly selected for use as the Wusel logo.

Original source SHA-256: `92aa48d30b0813c364bbb955082071f7b64af596df7d11291b2528fc64fffed4`.

## Assets

| File | Purpose |
| --- | --- |
| `wusel/static/wusel-logo.png` | Unchanged selected original artwork |
| `wusel/static/wusel-mark.png` | Transparent 256-pixel-wide header mark |
| `wusel/static/favicon.ico` | ICO containing 16, 32, 48, 64, 128 and 256-pixel PNG frames |
| `wusel/static/favicon-16.png`, `favicon-32.png` | Browser-tab icons |
| `wusel/static/favicon-192.png`, `favicon-512.png` | Higher-resolution browser/shortcut icon candidates |
| `wusel/static/apple-touch-icon.png` | 180-pixel Apple touch icon |
| `wusel/icon.png` | 128-pixel Home Assistant icon |
| `wusel/logo.png` | 500-pixel-wide transparent Home Assistant logo |

Favicons and square icons have a light cream background so the petrol shape remains visible on dark surfaces. The original and header mark retain transparency. Brand colors do not follow theme palettes or the child's plain task-icon preference. Task, badge and weather illustrations remain SVG and are separate from this fixed brand artwork.

Browser assets are served from an explicit allowlist; `/favicon.ico` also maps to the bundled ICO. HTML links carry a `hedgehog-1` asset revision to avoid stale favicon caches. Change that suffix if the brand artwork changes. There is no CDN, external icon service or service worker.

Home Assistant reads `icon.png` and `logo.png` from the inner app folder. Its [presentation guide](https://contributors.home-assistant.io/apps/guides/presentation/#icon-and-logo) recommends a 128-pixel square icon and allows other logo sizes. These files must be copied alongside the app manifest when installing/updating local app sources.

## Regenerate exports

Generated files are committed; no image-processing package is needed to run Wusel or its normal checks. For a deliberate re-export, install the development-only Sharp library in an ignored directory:

```sh
npm install --prefix work/branding-tools --no-save sharp@0.35.5
node tools/build-branding.cjs --sharp-module ./work/branding-tools/node_modules/sharp
```

Alternatively supply an existing local Sharp module directory. The tool reads the committed source and writes only the derived files listed above. It never overwrites the original. Review the source and 16/32-pixel previews before publishing a changed logo.

# Tara Graphix security audit and deployment notes

Audited 2026-09-10. This is a static, public portfolio. No backend, authentication,
database, upload endpoint, or private session exists in the current project.
This report does not claim that the site is completely secure.

## A. Critical findings

None identified in the inspected current project. Credential-pattern scans of
project text/configuration files found no private keys, API credentials, tokens,
password assignments, or private filesystem paths. No secret-bearing files were
identified. Artwork is public content; this was not forensic analysis of binary
media or a complete historical Git secret scan.

## B. High findings

No confirmed high-severity exploit path was identified. There is no user-input
source reaching an HTML, script, URL, or CSS execution sink in application code.
A compromised permitted script could control the page, but no evidence of such
a compromise was found; that possibility is not reported as an existing exploit.

## C. Medium findings and fixes

1. **Missing production browser protections.** The project supplied only
   `vercel.json`, which does not configure Netlify. A read-only HEAD request to
   the live Netlify URL returned no CSP, framing restriction, nosniff,
   Referrer-Policy, Permissions-Policy, COOP, or CORP. The new Netlify build
   generates these headers into `dist/_headers`. They are not live yet.
2. **Mutable external executable dependencies.** Tailwind used an unversioned
   CDN URL; the GSAP and ScrollTrigger versions were pinned but lacked SRI.
   All three now use byte-for-byte copies of the existing CDN assets, with
   versioned/content-hashed filenames, SHA-384 integrity attributes, and a
   SHA-256/SHA-384 lock checked by the build. No library was upgraded.

## D. Low findings and defense-in-depth changes

- Replaced 13 inline click attributes with explicit allowlisted event listeners
  so CSP can reject all inline event handlers. The functions remain the same.
- Existing `innerHTML` assignments contained only fixed strings and were not
  confirmed XSS. They now use `textContent` and `replaceChildren` to avoid
  unnecessary HTML interpretation.
- Publish only referenced assets, not the repository root. `.git`, `.env`,
  `.DS_Store`, build/configuration files, this report, the media bookkeeping
  manifest, and the unused legacy `script.js` are not staged. Originals remain
  untouched in the source project; originals referenced by the page are copied.
- Ignore local environment files and generated output in Git. Ignore rules are
  not the security boundary: the publication allowlist is.
- Keep HTML revalidated. The build now generates content-hashed media URLs;
  those and integrity-pinned vendor scripts receive year-long immutable caching.
- The existing safe external link attributes were retained. Instagram and
  WhatsApp URLs are fixed HTTPS links with `noopener noreferrer`. The WhatsApp
  phone path and prefilled text remain unchanged.

## E. Checked and not applicable, or no issue found

- No forms, user inputs, uploads, iframe/embed/object elements, service workers,
  web manifests, Netlify functions, authentication, cookies, or database access.
- No application use of query/hash/path data, dynamic redirects, `window.open`,
  `eval`, `new Function`, `document.write`, unsafe HTML insertion from external
  data, custom object merging, or prototype-key assignment.
- Application dataset values and generated selectors/styles come from fixed
  project markup, numeric slide indexes, and pointer coordinates. No untrusted
  network/URL input enters these paths.
- No unsafe `javascript:` links, insecure resource downloads, protocol-relative
  assets, or mixed HTTP resources. `http://www.w3.org/2000/svg` is an XML namespace,
  not a downloaded resource.
- No source maps, debug backups, logs, `.env`, robots.txt, sitemap.xml, or web app
  manifest were found in source publication inputs. `media/manifest.json` holds
  relative artwork paths, dimensions, hashes, and encoding metadata, not secrets;
  it is excluded because the page does not need it.
- Public media and developer source are not confidential solely because users
  can download them. No original media or legacy source was deleted.

## F. Files changed / added

- `index.html`: local integrity-pinned script references, event bindings, safe
  constant-text DOM updates. All inline CSS and image/video attributes unchanged.
- `.gitignore`: excludes build output, Python bytecode, and local environment files.
- `netlify.toml`: builds using Python and publishes `dist`.
- `tools/build_site.py`: validates vendor integrity and public asset paths,
  stages referenced assets with content-hashed media URLs, generates current inline-script CSP hashes/headers.
- `tools/vendor-lock.json`: upstream URLs, versions, hashes, and integrity values.
- `assets/vendor/tailwind-3.4.17-176e894661aa.js`
- `assets/vendor/gsap.min-3.12.2-efc85c7eb141.js`
- `assets/vendor/ScrollTrigger.min-3.12.2-65f6c13748b0.js`
- `SECURITY.md`: this report and maintenance instructions.
- `dist/`: generated, ignored deployment artifact including `_headers`.

`vercel.json`, legacy `script.js`, original artwork, optimized artwork/video,
posters, and `media/manifest.json` were not changed by this security pass.

## G. Headers

The build emits this policy with the real SHA-256 of the inline application script:

```text
default-src 'self'; base-uri 'none'; object-src 'none';
frame-ancestors 'none'; frame-src 'none'; form-action 'none';
script-src 'self' 'sha256-<generated>'; script-src-attr 'none';
style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
font-src 'self' https://fonts.gstatic.com; img-src 'self';
media-src 'self'; connect-src 'none'; worker-src 'none';
manifest-src 'none'; upgrade-insecure-requests
```

Inline **styles** remain permitted for existing Tailwind-generated styles,
markup styles, and GSAP. Inline **scripts** are hash-restricted; arbitrary
inline scripts, inline handlers, and dynamic string evaluation are not allowed.
Replacing the Tailwind runtime with compiled CSS is a separate optional future
task, not part of this security-only implementation.

Other headers:

- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), bluetooth=(), accelerometer=(), gyroscope=(), magnetometer=(), autoplay=(self), fullscreen=(self)`
- `Cross-Origin-Opener-Policy: same-origin`
- `Cross-Origin-Resource-Policy: same-origin`
- `Strict-Transport-Security: max-age=31536000`
- HTML: `Cache-Control: public, max-age=0, must-revalidate`
- Content-hashed media and vendor files: `Cache-Control: public, max-age=31536000, immutable`

No preload or includeSubDomains directive was added. The live Netlify response
already advertises provider-managed HSTS with includeSubDomains/preload; final
effective HSTS depends on Netlify. No COEP is imposed, avoiding unnecessary
third-party embedding requirements. CSP frame-ancestors provides framing
protection; no redundant X-Frame-Options header was added.

## H. Remaining third parties and limitations

- Tailwind Play runtime 3.4.17, GSAP 3.12.2, ScrollTrigger 3.12.2 remain required
  for the current implementation, now served locally. Embedded upstream license
  notices remain intact. Updates must be reviewed and hashes regenerated.
- Google Fonts remains external: CSS from fonts.googleapis.com and font files
  from fonts.gstatic.com. Families, weights, display behavior, and fallbacks are
  unchanged. Font CDN failures can still affect typography, but not trap users
  on the splash. No third-party JavaScript request is required at runtime.
- Tailwind's development-runtime warning remains upstream behavior. Self-hosting
  removes the mutable CDN delivery risk but does not make it compiled production
  CSS or eliminate its runtime compiler cost.
- OSV queries for npm `gsap` 3.12.2 and `tailwindcss` 3.4.17 returned no advisories
  on the audit date. This is not a full transitive dependency/SBOM assurance or
  proof of absence of vulnerabilities in the bundled libraries.

## I. Netlify deployment and maintenance

Run `python3 tools/build_site.py`. Netlify runs this via `netlify.toml` and publishes
**dist**, not the repository root. For a future manual upload, upload **dist**.
The build refreshes CSP hashes automatically after application JS edits. Do not
edit generated `dist/index.html` without rebuilding its matching headers.

On a future approved deployment, verify actual response headers on HTML, media,
and hashed JS; HTTPS redirects and certificate/custom-domain behavior; Netlify
cache overrides and MIME/range responses; blocked framing; absence of private
paths; font loading; and EN/AR interaction behavior. Dashboard settings, edge
functions/proxies, account access controls, and any deployment outside this build
were not inspected. Do not interpret a local header simulation as live protection.

## J. Verification performed and remaining manual checks

- Build succeeds; integrity failures and inline-handler additions are rejected.
- Local Chrome with the generated headers: injected inline scripts, event
  attributes, base-URL changes, external fetches, and framing were blocked.
- Excluded environment/repository/configuration/legacy paths returned 404 in
  staged output. All media attributes and inline CSS match the pre-security file.
- EN/LTR and AR/RTL at 320, 360, 375, 390, 430, 768, 820, 1024, 1280, 1366,
  1440, 1920 and 844x390: all 37 gallery artworks retain their dimensions;
  no page overflow, navbar overlap, or dots/arrows collisions. All page images decode.
- Native mouse/touch input exercised gallery arrows and swipe in both languages;
  menu/Escape, language actions, cursor disabling on emulated touch devices,
  deferred media, and splash fallbacks work under CSP. No unexpected script
  exceptions or failed asset requests during the responsive run.
- Splash dismissal begins around 1.82 seconds; existing fade and CSS fallback
  remain. JavaScript-disabled and font/CDN-blocked cases release the splash.
- First visible reel reached readyState 4 without an error; offscreen reels
  stayed deferred. Physical-device autoplay/audio policies remain a manual check.
- Reduced-motion emulation was checked for page access/overflow only; existing
  decorative motion preferences were not refactored in a security pass.
- Still manually verify physical iOS Safari/Android, trackpad/touch hybrids,
  slow mobile data, outbound contact app handoff, and the final HTTPS deployment.

No commit or deployment was performed.

References: [Netlify custom headers](https://docs.netlify.com/manage/routing/headers/),
[CSP guidance](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/CSP),
[Tailwind Play CDN limitations](https://tailwindcss.com/docs/installation/play-cdn),
[COOP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Opener-Policy),
[CORP](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cross-Origin-Resource-Policy).

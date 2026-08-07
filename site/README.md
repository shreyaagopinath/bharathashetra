# Public Website — bharathashetra.org

Single-page site. Everything lives in `index.html`; images go in `images/`.

---

## Deploying (Render Static Site — free)

1. Render Dashboard → **New +** → **Static Site**
2. Connect the same `bharathashetra` repo
3. Settings:
   - **Build Command:** *leave empty*
   - **Publish Directory:** `site`
4. Create, then **Settings → Custom Domains → Add** `bharathashetra.org`
5. In Porkbun DNS, change the existing **ALIAS** record for the root:
   - Host: *(blank)*
   - Answer: the `xxx.onrender.com` hostname Render gives this static site
   - (It currently points at `pixie.porkbun.com`, Porkbun's parking page)
6. Optionally add `www` as a **CNAME** to the same target

The parent portal at `portal.bharathashetra.org` is untouched by any of this.

---

## Adding your images

Drop files into `site/images/` with these exact names. Anything missing shows a
labeled placeholder instead of a broken image, so you can add them gradually.

| File | Used for | Suggested size |
|---|---|---|
| `logo.png` | Nav logo | 200×200, square |
| `instructor.jpg` | About section portrait | 800×1000, portrait |
| `gallery-1.jpg` … `gallery-6.jpg` | Performance gallery | 1200×900, landscape |
| `event-1.jpg` … `event-3.jpg` | Event posters | 900×1200, portrait |

**Before publishing photos of students:** these are other families' children on a
public page. Get permission from the parents of anyone recognizable, or favor
wide stage shots where individuals aren't identifiable. The photos in the parent
portal were shared under a login — that isn't the same as consenting to a public
website.

Compress images before uploading (squoosh.app is free). Aim for under 300 KB each.

---

## Editing the text

Search `index.html` for `EDIT ME` — every spot you'll want to personalize is
marked. The main ones:

- **Hero tagline** — the italic line under the school name
- **About** — replace the placeholder story with the school's real history
- **Meet Your Teacher** — instructor name, training lineage, credentials
- **Quote band** — currently a traditional verse; swap for your own philosophy
- **Video** — paste a YouTube embed where the placeholder is
- **Arangetram** — adjust if your path through the repertoire differs
- **Testimonials** — replace the three placeholder quotes with real ones
- **FAQ** — every answer needs checking against how you actually run classes
- **Events** — one `<article class="event">` block per event; copy/paste to add more
- **Contact** — email address and studio locations
- **`<meta name="description">`** in `<head>` — the text Google shows in results

### Two places to keep in sync

The FAQ appears **twice**: once as visible text, and once in the `FAQPage`
structured data at the top of the file. If you change an answer materially,
update both — Google may show the structured version directly in search results,
and it shouldn't contradict the page.

The same applies to your studio locations, which appear in the `DanceSchool`
structured data, the contact section, the footer, and the form dropdown.

### Testimonials

Ask parents before quoting them. First name and studio ("Parent · Keller") is
enough attribution and avoids publishing full names alongside children's photos.

---

## The contact form

Posts to `https://portal.bharathashetra.org/api/contact/public-inquiry`.
Submissions land in the **Messages** tab of the admin portal. The subject line
carries the studio they picked — "Website inquiry — Keller" — so you can triage
at a glance, and the phone number and studio preference are prepended to the
message body.

Spam protection is a hidden honeypot field — bots fill it, people never see it,
and anything with it filled is silently discarded. If you ever start getting
real spam, the next step would be adding Cloudflare Turnstile.

---

## Analytics

`index.html` has a commented-out analytics snippet near the top. To enable:

1. Sign up at [plausible.io](https://plausible.io) (~$9/mo) or
   [usefathom.com](https://usefathom.com)
2. Add `bharathashetra.org` as a site
3. Uncomment the matching `<script>` line in `index.html`

Both are cookie-free, so no cookie banner is required — unlike Google Analytics.

---

## Getting found on Google

The site includes SEO metadata and structured data marking it as a DanceSchool.
Two things matter more than anything on the page:

1. **Create a free Google Business Profile for EACH studio** —
   `business.google.com`. One for Flower Mound, one for Keller. Local search is
   location-specific: a parent in Keller searching "Bharatanatyam classes near
   me" will not reliably see a Flower Mound listing. Two profiles means two
   Maps pins and two sets of reviews. Bigger impact than any on-page work.
2. **Submit the site to Google Search Console** — `search.google.com/search-console`.
   Verify the domain and submit `https://bharathashetra.org` so it gets indexed
   in days rather than weeks.

Keep the address, phone, and school name identical between the site and the
Business Profile — inconsistencies weaken local ranking.

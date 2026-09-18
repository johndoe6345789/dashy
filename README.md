# dashy

The [Dashy](https://dashy.to) homepage served at https://wardcrew.com.

| File | What it is |
| --- | --- |
| `conf.yml` | Main page: WardCrew apps, admin links, everyday links |
| `apps.yml` | "App Guide" page: deep links into individual apps (loaded via `pages:` in `conf.yml`) |
| `Dockerfile` | `lissy93/dashy` (pinned) with both configs baked in |
| `captain-definition` | Tells CapRover to build the `Dockerfile` |
| `scripts/lint.py` | Schema validation plus link lint, run by CI |
| `docker-compose.yml` | Local preview on http://localhost:4000 |

## Deploying

The CapRover app `dashy` (custom domain `wardcrew.com`) builds this repo's
`Dockerfile`. Push to `master` and CapRover rebuilds via its GitHub webhook
(app → Deployment → "Deploy from Github/Bitbucket/Gitlab").

The config is baked into the image and `preventWriteToDisk` is on, so edits
made in Dashy's UI only last in that browser. Change the YAML here instead.

## Rules for links

Everything in these files is public: Dashy serves them at `/conf.yml` and
`/apps.yml`, and the repo is public. `scripts/lint.py` enforces:

- **No private hosts** (`*.ts.net`, private IPs). Put infra consoles behind
  Cloudflare Access or keep them off the public dashboard.
- **`https://` for `wardcrew.com` links, and no ports that Cloudflare doesn't
  proxy** (e.g. `:8889`, `:9443` can never load through the tunnel).
- **No duplicate URLs** in a file, no duplicate titles within a section,
  every item has an icon, no leftover `temp_*` ids from Dashy's editor.
- Don't deep-link into apps without URL routing (Workforce, StrategyOS):
  every such link just opens the homepage.

Run it locally:

```bash
docker run --rm --entrypoint cat "$(awk '/^FROM /{print $2; exit}' Dockerfile)" \
  /app/src/utils/config/ConfigSchema.json > /tmp/schema.json
python3 scripts/lint.py /tmp/schema.json conf.yml
```

Status dots are enabled per item on our own services only; big external
sites often answer bot checks with 403s, which would show as false outages.

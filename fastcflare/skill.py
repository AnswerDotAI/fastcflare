# NB: this file is designed for an LLM reader, not a human. Add it to your LLM's context and ask it to explain.
"""Cloudflare API access via `CloudflareApi`: zones, DNS records, caching, and every other Cloudflare v4 feature from Python. Use this for day-to-day Cloudflare work instead of hand-built httpx calls against api.cloudflare.com.

notation: /why

- ~2,600 ops, generated per instance from a bundled OpenAPI snapshot (`fastcflare.cf_spec`): the class shows only `verify`, `create_token`; op names can shift when the snapshot updates, URLs don't
- every call async, `verify` and `create_token` too

## Names: from verb and URL path, not operation IDs

- group: path's non-parameter segments, nested: `/zones/{zone_id}/dns_records` → `cf.zones.dns_records`
- method: the verb, lowercase; group with both collection and single-item GET: `.list`, `.get` (`GET /zones` → `cf.zones.list`, `GET /zones/{zone_id}` → `cf.zones.get`); one GET: `.get`
- rare collisions: siblings differing only by an interior param gain `_by_<param>`; action segment that would shadow an op: `<segment>_<verb>` on the parent
- e.g. `GET /user/tokens/verify` → `cf.user.tokens.verify.get()`; route params (`zone_id`, ...) by position or keyword; query, body params by keyword

## Finding operations

- start: endpoint URL from Cloudflare's docs (organised by URL), or guessed path segments, through the naming rules
- drill down; bare display = `doc()`: `cf` → `doc(cf.zones)` → `doc(cf.zones.dns_records.post)`
- deep groups: `pyskills.xdir(cf.zones, 'cache')`, then display a match
- failing those: `rgstr(pattern, full_docs(cf.groups))`; each hit has the dotted call path; never display the ~430,000-character reference

## Results

- Cloudflare's envelope: `.success`, `.result` (list for collection ops), `.errors`, `.messages`
- list endpoints: `page`, `per_page`; totals in `.result_info`; no auto-paging helper
- HTTP failure: raises `fasttransport.errors.APIError` (`.status_code`; message: Cloudflare's error JSON, `code`, `message` chain)

```python
zid = (await cf.zones.list(name='example.com')).result[0].id
(await cf.zones.dns_records.list(zone_id=zid)).result
rec = await cf.zones.dns_records.post(zid, type='A', name='test.example.com', content='192.0.2.1', ttl=1)
await cf.zones.dns_records.delete(zid, rec.result.id)
```

## Tokens

- permission-group names: check first: `[p.name for p in (await cf.user.tokens.permission_groups.get()).result if 'DNS' in p.name]`    /`create_token` skips unmatched names
- `tok = await cf.create_token(['example.com'], ('Zone Read', 'DNS Write'), 'dns mgt')`; save `tok.result.value` now    /shown only in this response
- account-owned token (service principal: valid after its creator leaves): `cf.accounts.tokens.post`; policy must nest zones under the account resource: `{f'com.cloudflare.api.account.{acct_id}': {'com.cloudflare.api.account.zone.*': '*'}}`; bare zone resource fails: "Must specify a zone for account owned tokens"
"""

__all__ = ['CloudflareApi', 'full_docs']

from .core import CloudflareApi
from fastcore.apisurface import full_docs

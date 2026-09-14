"""Cloudflare API access via `CloudflareApi`: zones, DNS records, caching, and every other Cloudflare v4 feature from Python. Use this for day-to-day Cloudflare work instead of hand-built httpx calls against api.cloudflare.com.

`fastcflare` wraps the entire Cloudflare v4 API (~2,500 operations), generated from Cloudflare's own OpenAPI spec when a client is constructed. All calls are async: `await` every API call (notebooks and modern REPLs support top-level `await`; scripts use `asyncio.run`).

# Auth

Three credential shapes, matching Cloudflare's own:

    cf = CloudflareApi(token=usr_tok)                       # user API token
    cf = CloudflareApi(token=acc_tok, account_id=acct_id)   # account-owned token
    cf = CloudflareApi(email=eml, api_key=global_key)       # global API key + email

With no `token` or `api_key`, the token falls back to the `CF_API_TOKEN` environment variable. When `api_key` is given, `email` falls back to `CF_API_EMAIL`.

`await cf.verify()` checks the credentials. It selects the user or account verification endpoint based on `account_id`. Check that `.result.status` is `'active'`.

# Names are computed from the URL

`fastcflare` does not use Cloudflare's operation IDs as method names. It names each operation from its HTTP verb and URL path:

- The group is the path's non-parameter segments, nested: `/zones/{zone_id}/dns_records` ops live at `cf.zones.dns_records`.
- The method is the HTTP verb: `.post`, `.put`, `.patch`, `.delete` -- except that when a group has both a collection GET and a single-item GET, they are `.list` and `.get` (`GET /zones` is `cf.zones.list`, `GET /zones/{zone_id}` is `cf.zones.get`). A group with only one GET keeps plain `.get`, whichever kind it is.
- Rare collisions get a suffix or fold: sibling paths differing only by an interior parameter gain `_by_<param>`, and an action segment that would shadow an op becomes `<segment>_<verb>` on the parent.

So anyone who knows the endpoint URL -- and Cloudflare's API docs organize by URL -- knows the call: `GET /user/tokens/verify` is `cf.user.tokens.verify.get()`. Route params (`zone_id`, ...) pass positionally or by keyword; query and body params by keyword.

# Discovering the API

Discovery is a drill-down, and `doc()` works at every level of a live instance:

    cf                              # bare display: the ~15 top-level groups
    doc(cf.zones)                   # a group: its ops, one line each with signature and title, then subgroups marked `name/`
    pyskills.xdir(cf.zones, 'cache')  # search a big group's names; the query is a case-insensitive regex
    doc(cf.zones.dns_records.post)  # one op: full parameter docs -- required/optional, defaults, per-param descriptions

Displaying any object bare shows the same as `doc()` on it.

Groups contain nested subgroups: `zones` has 60 subgroups and `radar` has 24. Use `xdir` to search large groups instead of reading their full listings. It returns operation and subgroup names together. Display a matching subgroup, such as `purge_cache`, to inspect its contents.

Use a constructed `CloudflareApi` instance for discovery. Groups are generated when you construct it. Inspecting the class shows only `verify` and `create_token`.

Find the endpoint in Cloudflare's API docs, or guess its path segments. Use the URL naming rule above to identify the call.

If that does not find the operation, search `full_docs(cf.groups)`. It contains every group and operation in a Markdown reference of about 430,000 characters. Search it rather than displaying it, using `rgapi`'s `rgstr`:

```python
rgstr(pattern, full_docs(cf.groups))
```

Each matching line includes the dotted call path.

# Results and errors

Every call returns Cloudflare's response envelope as attribute-accessible objects: `.success`, `.result` (a list for collection ops), `.errors`, `.messages`. List endpoints paginate with `page`/`per_page` params and report totals in `.result_info`; there is no auto-paging helper. HTTP-level failures raise `fastspec.errors.APIError`, which carries `.status_code` and Cloudflare's error JSON (with its `code`/`message` chain) in the message.

# Zones and DNS records

    zid = (await cf.zones.list(name='example.com')).result[0].id
    (await cf.zones.dns_records.list(zone_id=zid)).result
    rec = await cf.zones.dns_records.post(zid, type='A', name='test.example.com', content='192.0.2.1', ttl=1)
    await cf.zones.dns_records.delete(zid, rec.result.id)

# Scoped tokens

`create_token` builds a least-privilege user token for a set of domains, resolving permission-group names and zone ids for you:

    tok = await cf.create_token(['example.com'], ('Zone Read', 'DNS Write'), 'dns mgt')
    dns_tok = tok.result.value   # save it: the value is only shown at creation

Browse permission-group names first if unsure:

    pgs = (await cf.user.tokens.permission_groups.get()).result
    [p.name for p in pgs if 'DNS' in p.name]

Account-owned tokens act as service principals. They remain valid after the creating user leaves. Create them with `cf.accounts.tokens.post`.

Their policies must nest zones under the account resource:

```python
{f'com.cloudflare.api.account.{acct_id}': {'com.cloudflare.api.account.zone.*': '*'}}
```

A bare zone resource fails with "Must specify a zone for account owned tokens".

# Gotchas

- Everything is async, including `verify` and `create_token`: a forgotten `await` gives a coroutine, not an envelope.
- The generated surface reflects the bundled `cf_spec` module, so op names can shift when the spec is updated: URLs are the stable vocabulary, and the naming rule maps them to calls.
- Cloudflare token *values* are never retrievable after creation; `user.tokens.get(token_id)` returns metadata only.
"""

__all__ = ['CloudflareApi', 'full_docs']

from .core import CloudflareApi
from fastcore.apisurface import full_docs

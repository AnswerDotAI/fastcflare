"""Cloudflare API access via `CloudflareApi`: zones, DNS records, caching, and every other Cloudflare v4 feature from Python. Use this for day-to-day Cloudflare work instead of hand-built httpx calls against api.cloudflare.com.

Wraps the whole Cloudflare v4 API (~2,600 operations), generated on construction from a bundled snapshot of Cloudflare's OpenAPI spec (`fastcflare.cf_spec`). Everything is async, including `verify` and `create_token`: a missing `await` gives a coroutine, not an envelope.

# Credentials

    cf = CloudflareApi(token=usr_tok)                       # user API token
    cf = CloudflareApi(token=acc_tok, account_id=acct_id)   # account-owned token
    cf = CloudflareApi(email=eml, api_key=global_key)       # global API key + email

`doc(CloudflareApi)` covers env-var fallbacks; `await cf.verify()` checks the credentials.

# Names come from the URL

Operations are named from HTTP verb + URL path, not Cloudflare's operation IDs:

- Group = the path's non-parameter segments, nested: `/zones/{zone_id}/dns_records` → `cf.zones.dns_records`.
- Method = the verb (`.get`/`.post`/`.put`/`.patch`/`.delete`), except a group with both a collection GET and a single-item GET gets `.list` and `.get` (`GET /zones` = `cf.zones.list`, `GET /zones/{zone_id}` = `cf.zones.get`); a group with one GET keeps `.get`.
- Rare collisions: sibling paths differing only by an interior param gain `_by_<param>`; an action segment that would shadow an op becomes `<segment>_<verb>` on the parent.

So the endpoint URL (how Cloudflare's docs are organised) gives the call: `GET /user/tokens/verify` = `cf.user.tokens.verify.get()`. Route params (`zone_id`, ...) go by position or keyword; query/body params by keyword. Op names can shift when the snapshot updates; URLs are the stable vocabulary.

# Finding operations

Groups exist only on an instance (the class shows just `verify` and `create_token`). `doc()` works at every level; a bare display shows the same:

    cf                                # the 15 top-level groups
    doc(cf.zones)                     # a group's ops, one line each, then subgroups marked `name/`
    pyskills.xdir(cf.zones, 'cache')  # names in a big group matching a case-insensitive regex
    doc(cf.zones.dns_records.post)    # one op's full parameter docs

Groups nest deeply (`zones` has 60 subgroups): search with `xdir` (returns op and subgroup names), then display a match such as `purge_cache`. Start from the endpoint in Cloudflare's docs, or guess its path segments, and apply the naming rule. Failing that, search (don't display) the full ~430,000-character reference; each matching line includes the dotted call path:

    rgstr(pattern, full_docs(cf.groups))

# Results and errors

Every call returns Cloudflare's envelope as attribute-accessible objects: `.success`, `.result` (a list for collection ops), `.errors`, `.messages`. List endpoints page with `page`/`per_page` and report totals in `.result_info`; no auto-paging helper. HTTP failures raise `fasttransport.errors.APIError` with `.status_code`, and Cloudflare's error JSON (`code`/`message` chain) in the message.

# Zones and DNS records

    zid = (await cf.zones.list(name='example.com')).result[0].id
    (await cf.zones.dns_records.list(zone_id=zid)).result
    rec = await cf.zones.dns_records.post(zid, type='A', name='test.example.com', content='192.0.2.1', ttl=1)
    await cf.zones.dns_records.delete(zid, rec.result.id)

# Scoped tokens

`create_token` makes a least-privilege user token for a set of domains, resolving permission groups and zone IDs:

    tok = await cf.create_token(['example.com'], ('Zone Read', 'DNS Write'), 'dns mgt')
    dns_tok = tok.result.value   # save it: token values can't be read back; cf.user.tokens.get(token_id) returns metadata only
    pgs = (await cf.user.tokens.permission_groups.get()).result   # check permission-group names first
    [p.name for p in pgs if 'DNS' in p.name]

Account-owned tokens are service principals, valid after their creator leaves; create them with `cf.accounts.tokens.post`. Their policies must nest zones under the account resource, `{f'com.cloudflare.api.account.{acct_id}': {'com.cloudflare.api.account.zone.*': '*'}}`; a bare zone resource fails with "Must specify a zone for account owned tokens".
"""

__all__ = ['CloudflareApi', 'full_docs']

from .core import CloudflareApi
from fastcore.apisurface import full_docs

"""Complete access to the Cloudflare SDK

Modules:

- `fastcflare.skill`: Cloudflare API access via `CloudflareApi`: zones, DNS records, caching, and every other Cloudflare v4 feature from Python. Use this for day-to-day Cloudflare work instead of hand-built httpx calls against api.cloudflare.com."""

__version__ = "0.1.1"
from .core import *

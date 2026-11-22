"""Complete access to the Cloudflare SDK

Modules:

- `fastcflare.graphql`: Query Cloudflare's GraphQL Analytics API with schema-aware chaining, batched requests and raw GraphQL
- `fastcflare.skill`: Cloudflare REST (`CloudflareApi`) and GraphQL Analytics (`CfGql`) access from Python: zones, DNS records, R2 buckets and S3 tokens, caching, Workers, and analytics. Use this instead of hand-built httpx calls against api.cloudflare.com."""

__version__ = "0.1.2"
from .core import *
from .graphql import *

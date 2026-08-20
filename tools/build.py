#!/usr/bin/env python
"Regenerate fastcflare/cf_spec.py from Cloudflare's published OpenAPI schema."
from pathlib import Path
from fastcflare.core import build_spec

build_spec(nm=Path(__file__).parent.parent/'fastcflare'/'cf_spec.py')

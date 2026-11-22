#!/usr/bin/env python
"Regenerate fastcflare/cf_spec.py and fastcflare/gql_spec.py from Cloudflare's schemas."
from pathlib import Path
from fastcflare.core import build_spec
from fastcflare.graphql import build_gql_spec

pkg = Path(__file__).parent.parent/'fastcflare'
build_spec(nm=pkg/'cf_spec.py')
build_gql_spec(nm=pkg/'gql_spec.py')

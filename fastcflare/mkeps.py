#!/usr/bin/env python
from fastcflare.core import build_cf_eps
from pathlib import Path

(Path(__file__).parent/'eps.py').write_text(repr(build_cf_eps()))

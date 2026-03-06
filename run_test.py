#!/usr/bin/env python
import sys
sys.path.insert(0, '.')

from signature import SignatureVerifier

verifier = SignatureVerifier("DG5g3B4j9X2KOErG")

event_ts = "1725442341"
plain_token = "Arq0D5A61EgUu4OxUvOp"

signature = verifier.generate_response_signature(event_ts, plain_token)

expected = "87befc99c42c651b3aac0278e71ada338433ae26fcb24307bdc5ad38c1adc2d01bcfcadc0842edac85e85205028a1132afe09280305f13aa6909ffc2d652c706"

print("=" * 60)
print("QQ Bot Signature Verification Test")
print("=" * 60)
print(f"Generated: {signature}")
print(f"Expected:  {expected}")
print(f"Match: {signature == expected}")
print("=" * 60)

if signature == expected:
    print("SUCCESS: Signature matches expected value!")
    sys.exit(0)
else:
    print("FAILED: Signature does not match!")
    sys.exit(1)

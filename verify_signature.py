from signature import SignatureVerifier

verifier = SignatureVerifier("DG5g3B4j9X2KOErG")

event_ts = "1725442341"
plain_token = "Arq0D5A61EgUu4OxUvOp"

signature = verifier.generate_response_signature(event_ts, plain_token)

expected = "87befc99c42c651b3aac0278e71ada338433ae26fcb24307bdc5ad38c1adc2d01bcfcadc0842edac85e85205028a1132afe09280305f13aa6909ffc2d652c706"

print(f"Generated signature: {signature}")
print(f"Expected signature:  {expected}")
print(f"Match: {signature == expected}")

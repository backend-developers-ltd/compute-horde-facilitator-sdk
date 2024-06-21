# Signatures

## Client side

If `signer` parameter is provided to `FacilitatorClient`,
the client will sign every request before sending it to the server.

## Verifying signatures on server side

```python
import json

from compute_horde_facilitator_sdk.v1 import (
    signature_from_headers,
    signature_payload,
    verify_signature,
    SignatureNotFound,
)


try:
    signature = signature_from_headers(request.headers)
except SignatureNotFound:
    pass  # can be safely ignored if we don't require signatures
else:
    sign_payload = signature_payload(
        request.method, str(request.url), json=json.loads(request.content) if request.content else None
    )
    verify_signature(sign_payload, signature)
```


Additionally, in case of `bittensor` signature type, you can extract hotkey from the signature.
```python
if signature.signature_type == "bittensor":
    hotkey = signature.signatory
```

You can choose the PASETO purpose used to create a token through the `purpose`
parameter of `create_access_token()`, `create_refresh_token()`, or
`create_token()`.

Please read up on PASETO tokens to find out which is the best purpose for your
use case, but to put it short:

**Local** means the token is encrypted with symmetric cryptography. Someone who
obtains the token cannot read its contents without the shared secret key.
This is a good fit when every party that needs to decrypt the token is under
your control.
That secret is also the root credential for minting valid local tokens, so it
should be generated with a CSPRNG and retrieved from secure storage instead of
hardcoded into application code. See [Key Management](key-management.md).

**Public** means the token is signed with your private key but not encrypted.
The payload remains visible to anyone holding the token, so you should not put
confidential data into public tokens. Public tokens can be verified with the
matching public key, which is safe to share with untrusted parties.
The private key still needs the same level of protection as any other signing
credential, and file-based PEM loading should be treated as a fallback for
constrained environments. See [Key Management](key-management.md).

```python hl_lines="16 35-36"
{!../examples/purpose.py!}
```

# Problox
Roblox library with support for launching game clients.

# Usage
```python
from problox import Problox

# https://chrome.google.com/webstore/detail/get-cookiestxt/bgaddhkoddajcdgocldbbfleckgcbcid
rbx = Problox.from_cookiefile("cookies.txt")

user_info = rbx.request(
    method="GET",
    url="https://users.roblox.com/v1/users/authenticated"
    ).json()
print(f"Authenticated as {user_info['name']}")

client = rbx.join_game(1818, locale="fr_fr")
print(f"Launched client with PID {client.pid}")

client.wait()
print(f"Client was closed")
```

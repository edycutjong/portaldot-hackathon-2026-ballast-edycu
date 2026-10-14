# Test fixtures

Raw runtime metadata (`state_getMetadata`, SCALE bytes), sha256-pinned in `SHA256SUMS` and checked by the tests.

| File | Node | Runtime | `:code` blake2-256 | Captured |
|---|---|---|---|---|
| `standin-upstream-metadata.scale` | polkadot-sdk `substrate-node` polkadot-stable2606-3 (3.0.0-dev-9d0dc6e8fbb), `--dev` | `node` / 268, metadata V14+ | `0x72e84be232be151b059440f89710895de0cb6b71b6529f97e9c02340765f1ec0` | 2026-10-14, `scripts/standin_node.sh start` |
| `standin-1002-metadata.scale` | `portaldot_dev` 2.0.0, `--dev --tmp` | `portaldot` / 1002, metadata V13 | `0x8c0d4d9d638ad05e7d214e1496321cea00274698e4bcf5b2006c3eaf86b7fa80` | 2026-10-14, scratch run |

Both are local stand-in chains, not the Portaldot V3 testnet. Capture: `curl -s -H 'Content-Type: application/json'
-d '{"id":1,"jsonrpc":"2.0","method":"state_getMetadata","params":[]}' http://127.0.0.1:49944` → hex → bytes.

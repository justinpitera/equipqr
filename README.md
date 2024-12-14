# Panel

adb reverse tcp:5173 tcp:5173

<https://10.0.2.2:5173/>

vite shortcuts:
  press h + enter to show help
  press r + enter to restart the server
  press u + enter to show server url
  press o + enter to open in browser
  press c + enter to clear console
  press q + enter to quit

## Buf

Generate protobuf classes:

1. npm install -g protoc-gen-ts

2. buf generate

3. buf.gen.yaml - settings for generating:

```text
version: v1
plugins:
  - name: python
    out: api/src/protos/
  - name: ts
    out: out/ # Adjust
```

### Proto Usage Example

```proto
syntax = "proto3";

enum Role {
    ADMIN = 0;
    MOD = 1;
}

message Author {
    Role role = 2;
    oneof id_or_name {
        string id = 4;
        string name = 5;
    }
}
```

```typescript
const author = Author.fromJson({
    role: Kind.ADMIN,
    name: "mary poppins",
});

// Serialize to binary
const bytes: Uint8Array = author.toBinary();

// Deserialize from binary
const received: Change = Change.fromBinary(bytes);

console.log(received.toJson())
```

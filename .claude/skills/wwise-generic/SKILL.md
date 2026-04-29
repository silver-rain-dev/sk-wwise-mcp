---
name: wwise-generic
description: Fallback WAAPI passthrough — discover available WAAPI functions, get their schemas, and call any WAAPI function directly. Use ONLY when no specialized wwise-* skill has the right tool.
metadata:
  author: silver-rain-dev
  version: "1.0"
---

# Wwise Generic (Fallback Only)

## Tools

1. `list_waapi_functions` — find the relevant WAAPI function
2. `get_waapi_function_schema` — understand its arguments
3. `call_waapi` — execute it

## When to Use

Only when no other wwise-* skill covers the operation. Always check specialized skills first.

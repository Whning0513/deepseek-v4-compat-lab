# Offline Protocol Matrix

These are conformance fixtures, not model scores. A matched row means the pinned checker produced the expected diagnostics.

| Case | Boundary | Expected codes | Result |
| --- | --- | --- | --- |
| `valid-thinking-tool-loop` | Thinking tool loop preserves reasoning_content | none | matched |
| `valid-disabled-thinking-loop` | Explicit non-thinking tool loop | none | matched |
| `missing-reasoning-roundtrip` | Missing reasoning_content in a thinking tool loop | `REASONING_CONTENT_MISSING` | matched |
| `orphan-tool-result` | Tool result must match a pending tool_call_id | `TOOL_RESULT_ORPHAN` | matched |
| `mid-flight-pending-result` | Mid-flight capture keeps pending tool results visible | `TOOL_RESULTS_PENDING` | matched |
| `invalid-strict-schema` | DeepSeek strict function schema requirements | `STRICT_ADDITIONAL_PROPERTIES`, `STRICT_REQUIRED_MISSING` | matched |
| `interleaved-streamed-tools` | Interleaved streamed tool-call indices | `SSE_EMPTY_CHOICES`, `SSE_TOOL_INDICES_INTERLEAVED` | matched |
| `truncated-streamed-arguments` | Token-limited incomplete streamed arguments | `SSE_TOOL_ARGUMENTS_INVALID` | matched |
| `malformed-stream-line` | Malformed SSE JSON data line | `SSE_JSON_INVALID` | matched |

Summary: 9/9 fixtures matched; 0 mismatched.

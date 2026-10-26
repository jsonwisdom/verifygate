# FC-2 real-adapter differential runner — intentionally NOT RUN in CI

This runner is for the **actual compiled/installed Python, JavaScript, Go adapters**—not stand-ins. Required environment variables are `FC2_PYTHON_ADAPTER`, `FC2_JS_ADAPTER`, and `FC2_GO_ADAPTER`, each naming an executable accepting raw bytes from stdin and returning canonical JSON on stdout for accepted input (otherwise nonzero exit, empty stdout). Wrapper scripts may be needed where a runtime requires arguments.

Use fixed `fixtures/fc2_hostile_bytes_v1.json` inputs. `python3 scripts/run_fc2_real_adapters.py` fails closed when adapters are missing, on timeout, unexpected accept/reject, rejection with stdout, or unequal accepted canonical output. A clean run emits `fc2_real_adapters_receipt.json`; **it is not signed, reproducibility pinned, or certified merely because the script runs**.

Do not substitute the Python seed for the actual Python adapter. Existing seed-only GitHub CI remains seed-only. An independent review must confirm the binary hashes, source revisions, fixture expectations, error handling, limits, and repeatability. CI should not fetch untrusted binaries or run wallet code.

**FC2 FULL GATE HOLD; x402 LIVE HOLD; PRODUCTION HOLD.**

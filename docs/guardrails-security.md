# Guardrails and Security

Inputs are sanitized and assessed for prompt injection, jailbreak attempts, and misuse. Retrieved Qdrant content is untrusted and sanitized before entering reasoning prompts. Outputs are schema-validated, policy-checked, and redacted before being returned.

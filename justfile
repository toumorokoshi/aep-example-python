serve:
    uv run aep-server serve

generate-openapi:
    uv run aep-server generate-openapi

lint:
    npx @stoplight/spectral lint --ruleset "https://raw.githubusercontent.com/aep-dev/aep-openapi-linter/main/spectral.yaml" ./openapi.json
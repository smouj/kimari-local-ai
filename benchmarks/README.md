# Kimari Benchmarks

This directory contains benchmark results for Kimari Local AI on various GPU configurations.

## Contributing Benchmarks

To contribute your benchmark results:

1. Run the benchmark with JSON output:
   ```bash
   kimari bench --profile gtx1060 --json --output benchmarks/results/my-gtx1060.json
   ```

2. Or use the template from `benchmarks/templates/` and fill in your results manually.

3. Submit a PR with your result file.

## Benchmark Format

See `benchmarks/templates/` for the expected JSON format.

## Important Notes

- Include your GPU model, driver version, and CUDA version for accurate comparisons.
- The `peak_vram_mb` field can be `null` if you cannot measure it — this is a known limitation.
- Run benchmarks with the server freshly started for consistent results.

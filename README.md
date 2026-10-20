# face-fit

Prepare ID photos with automatic face alignment and cropping.
The tool uses geometric edits and white margins, without skin or color retouching.

## Get started

Install [UV](https://docs.astral.sh/uv/), then run:

```sh
git clone https://github.com/P4suta/face-fit.git
cd face-fit
uv sync --frozen
uv run --frozen face-fit fit photo.jpg id.jpg
```

Local development uses Python 3.14.
The first photo conversion downloads the MediaPipe face model.

See the [usage guide](docs/usage.md) for batch conversion, options, and model caching.
See [Contributing](CONTRIBUTING.md) for checks and the [documentation](https://p4suta.github.io/face-fit/) for the algorithm.

## License

[Apache-2.0](LICENSE) © 2026 face-fit contributors

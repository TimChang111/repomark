# repomark

> Zero-dependency CLI tool to bundle codebases into structured, token-estimated Markdown context for Claude, Claude Code, and other LLMs.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

## Features

- **Zero External Dependencies**: Built entirely with Python's standard library.
- **Smart Filtering**: Automatically omits binary files, cache directories, and virtual environments.
- **Structural Tree Visualization**: Produces a clean ASCII directory hierarchy.
- **Token Estimation**: Built-in heuristic calculator to monitor prompt window consumption.

## Installation

```bash
https://github.com/TimChang111/repomark.git
cd repomark
pip install -e .
```

## Usage

Bundle the current directory into a Markdown file:
```bash
repomark . -o context.md
```

Print context directly to standard output:
```bash
repomark ./src
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

Distributed under the [MIT License](LICENSE).

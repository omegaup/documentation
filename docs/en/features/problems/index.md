---
title: Problems
description: Creating and managing programming problems in omegaUp
icon: bootstrap/puzzle
---

# Problems

omegaUp supports creating programming problems through two methods: the visual Problem Creator (CDP) or manual ZIP file generation.

## Problem Creation Methods

### omegaUp Problem Creator (CDP)

The [Problem Creator](https://omegaup.com/problem/creator) is a visual tool for creating problems:

- ✅ User-friendly interface
- ✅ Intuitive workflow
- ⚠️ Some limitations (e.g., no Karel problems)

!!! tip "Tutorial"
    Watch [this video tutorial](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) to learn how to use the Problem Creator.

### Manual ZIP File Generation

For advanced use cases, you can manually create a `.zip` file:

- ✅ Full control over problem structure
- ✅ Supports all problem types including Karel
- ✅ Custom validators and test cases

See [Problem Format](problem-format.md) for detailed instructions.

## Problem Components

A problem consists of:

- **Statement**: Problem description (Markdown)
- **Test Cases**: Input/output files (`.in`/`.out`)
- **Validator**: How outputs are compared
- **Limits**: Time and memory constraints
- **Languages**: Supported programming languages

## Related Documentation

- **[Creating Problems](creating-problems.md)** - Step-by-step creation guide
- **[Problem Format](problem-format.md)** - ZIP file structure and format
- **[Problems API](../../reference/api.md)** - API endpoints for problems

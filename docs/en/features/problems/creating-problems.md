---
title: Creating Problems
description: Step-by-step guide to creating programming problems
icon: bootstrap/plus-circle
---

# Creating Problems

This guide walks you through creating programming problems in omegaUp.

## Quick Start

The easiest way to create a problem is using the [Problem Creator (CDP)](https://omegaup.com/problem/creator):

1. Visit [omegaup.com/problem/creator](https://omegaup.com/problem/creator)
2. Fill in problem details
3. Add test cases
4. Configure limits and languages
5. Upload and publish

!!! tip "Video Tutorial"
    Watch [this tutorial](https://www.youtube.com/watch?v=cUUP9DqQ1Vg) for a visual walkthrough.

## Problem Components

### Required Elements

- **Title**: Problem name
- **Alias**: Short identifier (used in URLs)
- **Statement**: Problem description (Markdown supported)
- **Test Cases**: Input/output files
- **Validator**: How outputs are compared
- **Limits**: Time and memory constraints

### Optional Elements

- **Source**: Problem origin (e.g., "OMI 2020")
- **Tags**: Categorization tags
- **Validator Code**: Custom validator program
- **Checker**: Custom output checker

## Validator Types

| Type | Description |
|------|-------------|
| `literal` | Exact match |
| `token` | Token-by-token comparison |
| `token-caseless` | Case-insensitive token comparison |
| `token-numeric` | Numeric comparison with tolerance |
| `custom` | User-defined validator |

## Problem Limits

Configure appropriate limits:

- **Time Limit**: Execution time per test case (milliseconds)
- **Memory Limit**: Memory usage limit (KB)
- **Output Limit**: Maximum output size (bytes)

## Supported Languages

omegaUp supports many programming languages:

- C, C++ (various standards)
- Java, Kotlin
- Python 2/3
- Ruby, Perl
- C#, Pascal
- Karel (Karel.js)
- And more...

## Advanced: Manual ZIP Creation

For advanced use cases, see [Problem Format](problem-format.md) for manual ZIP file creation.

## Related Documentation

- **[Problem Format](problem-format.md)** - ZIP file structure
- **[Problems API](../../api/problems.md)** - API endpoints
- **[Problem format (ZIP)](problem-format.md)** — manual ZIP layout, validators, and cases
- **[Long-form manual (GitHub)](https://github.com/omegaup/omegaup/blob/main/frontend/www/docs/Manual-for-Zip-File-Creation-for-Problems.md)** — supplementary detail in the main repo wiki mirror

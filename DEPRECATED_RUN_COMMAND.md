# Deprecated `run` Command

## Overview

The `racoon_clip run` command has been deprecated and replaced with more specific commands:
- `racoon_clip crosslinks` - for crosslink detection without peak calling
- `racoon_clip peaks` - for the full pipeline including peak calling

## Backward Compatibility

For backward compatibility, the `run` command is still available and will:
1. Display a deprecation warning in yellow/bold text
2. Redirect to `racoon_clip crosslinks` 
3. Execute the crosslinks workflow

## Deprecation Warning

When using `racoon_clip run`, users will see:

```
⚠️  DEPRECATION WARNING ⚠️
The 'racoon_clip run' command is deprecated and will be removed in a future version.
Please use:
  - 'racoon_clip crosslinks' for crosslink detection (without peak calling)
  - 'racoon_clip peaks' for the full pipeline (including peak calling)

For now, this command will execute 'racoon_clip crosslinks'...
```

## Usage

Old command (deprecated):
```bash
racoon_clip run --configfile config.yaml --cores <n>
```

New commands (recommended):
```bash
# For crosslinks only
racoon_clip crosslinks --configfile config.yaml --cores <n>

# For full pipeline with peaks
racoon_clip peaks --configfile config.yaml --cores <n>
```

## Implementation Details

- The `run` command uses the exact same implementation as `crosslinks`
- All parameters and options are identical to the `crosslinks` command
- The deprecation warning is displayed before execution begins
- The warning uses colored output (yellow/bold) for visibility

## Migration Guide

Users should update their scripts and workflows:

**Before:**
```bash
racoon_clip run --configfile my_config.yaml --cores <n>
```

**After (for crosslinks):**
```bash
racoon_clip crosslinks --configfile my_config.yaml --cores <n>
```

**After (for full pipeline with peaks):**
```bash
racoon_clip peaks --configfile my_config.yaml --cores <n>
```

## Future Removal

The `run` command will be removed in a future major version release. Users are encouraged to migrate to the new commands as soon as possible.

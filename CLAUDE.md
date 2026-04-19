# varmeta — AI Assistant Context Guide

**Version:** 0.1.3  
**Python:** ≥ 3.11  
**Last Updated:** April 19, 2026

---

## Project Overview

`varmeta` is a lightweight Python library for attaching metadata (name, units, description, component structure) to variable identifiers and using that metadata to drive pandas DataFrame construction, serialization, and data unpacking in scientific and engineering workflows.

**Core Value Proposition:**
- Define variables with rich metadata once (`Var` instances)
- Use shared literal string keys across `VarDict` and data dictionaries
- Automatically unpack multi-component variables (e.g., 3D force → force_x, force_y, force_z)
- Generate pandas DataFrames with MultiIndex headers containing keys, names, and units
- Round-trip serialization to/from JSON-compatible dictionaries

**Runtime Dependencies:**
- `numpy >= 1.11.0`
- `pandas >= 2.3.1`

**Development Dependencies:**
- `pytest >= 8.4.1`
- `ruff >= 0.12.9`

**Build System:** `hatchling`

---

## Repository Structure

```
varmeta/
├── LICENSE
├── pyproject.toml         # Build config, ruff settings, dependencies
├── README.md              # User-facing documentation and tutorial
├── CLAUDE.md              # This file — AI assistant context
├── docs/                  # (empty)
├── scripts/               # (empty)
├── src/
│   └── varmeta/
│       ├── __init__.py    # Public API re-exports
│       ├── vars.py        # Core: Var, VarData, VarDict, unpack, dict_to_df, etc.
│       ├── valdicts.py    # ValData, ValDict, valdict_list_to_df
│       └── vardicts.py    # ⚠️ EMPTY PLACEHOLDER — not yet implemented
└── tests/
    ├── test_vars.py           # Core Var unit tests
    ├── test_vars_numpy.py     # NumPy-specific unpacking tests
    ├── test_vars_pandas.py    # DataFrame integration tests
    ├── test_vars_json.py      # JSON serialization round-trip tests
    └── test_doc_examples.py   # Integration tests mirroring README examples
```

---

## Commands

### Testing
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest tests/test_vars.py # Run specific test file
```

### Linting & Formatting
```bash
ruff check src/           # Lint source code
ruff check .              # Lint all Python files (including tests)
ruff format src/          # Auto-format source code
```

### Build
```bash
python -m build           # Build distribution packages (requires build)
```

---

## Public API

All symbols exported from `src/varmeta/__init__.py`:

### Core Classes & Types
- **`Var`** — Frozen, ordered dataclass representing a variable with metadata (key, name, units, description, components, component_axis, data_type)
- **`VarData`** — `TypedDict` for `Var` serialization (all fields of `Var` as dict keys)
- **`VarDict`** — `dict[str, Var]` subclass for holding Var instances keyed by their `key` field
- **`ValData`** — Extends `VarData` with `value: Any` field (bundles metadata + data)
- **`ValDict`** — `dict[Var, Any]` subclass keyed by `Var` instances (not strings)

### Core Functions
- **`unpack(var_dct, data_dct)`** — Expands component variables in both `VarDict` and data dict; returns `(VarDict, dict)`
- **`dict_to_df(var_dct, data_dct, attrs?)`** — Unpacks and builds MultiIndex pandas DataFrame from var/data dicts
- **`records_to_df(var_dct, data_dict_lst, attrs?)`** — Same as `dict_to_df` but accepts list of data dicts (records)
- **`vars_to_multi_index_data(lst, attrs?)`** — Builds MultiIndex tuple list from list of Vars using specified attrs (default: key, name, units)
- **`vars_to_dict(var_dict)`** — Serialize `VarDict` to `dict[str, VarData]` (JSON-compatible)
- **`vars_from_dict(var_data_dict)`** — Deserialize `dict[str, VarData]` back to `VarDict`

---

## Key Architecture & Patterns

### `Var` Dataclass Design
- **Frozen & Ordered:** `@dataclass(frozen=True, order=True)`
- **Unique Hash/Equality Pattern:**
  - `key` field has `compare=False` — excluded from ordering and equality
  - `__hash__` is based on `key` only (allows use as dict key or pandas index)
  - `__eq__` and ordering based on `name`, `units`, `description`, `components`, `component_axis`, `data_type`
- **String Representation:** `__str__` returns `"Name [units]"` — used as pandas column headers in CSV output
- **Methods:**
  - `.to_dict()` / `.from_dict()` — serialization round-trip
  - `.validate(data)` — checks `type(data).__name__ == self.data_type`
  - `.component_vars()` — generates list of sub-Vars (e.g., `force` → `force_x`, `force_y`, `force_z`)
  - `.unpack(data)` — returns `(list[Var], list|NDArray)` — uses `np.moveaxis` for multi-dimensional arrays
  - `.unpack_tuples(data)` — returns `list[tuple[Var, value]]`

### Shared Literal String Keys
```python
# Pattern used throughout codebase and tests
TEMP = "temperature"
FORCE = "force"

var_dct = VarDict({TEMP: temperature_var, FORCE: force_var})
data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}
```
This pattern ensures type safety and prevents key mismatches between var metadata and data.

### Component Unpacking
- Variables can have `components=("x", "y", "z")` attribute
- `component_axis` (default 0) specifies which axis to unpack along
- Uses `np.moveaxis` internally → handles both Python lists and NumPy ndarrays uniformly
- Unpacked var keys follow pattern: `{original_key}_{component}` (e.g., `force_x`, `force_y`, `force_z`)
- Unpacked var names follow pattern: `{original_name} - {component}` (e.g., `Force - x`, `Force - y`, `Force - z`)

### VarDict vs ValDict
- **`VarDict`**: `dict[str, Var]` — keys are strings (the `Var.key` field)
- **`ValDict`**: `dict[Var, Any]` — keys are `Var` instances themselves
- `ValDict` can `.split()` into `(VarDict, dict[str, Any])`
- `ValDict` can `.unpack()` to expand component vars into a new `ValDict`

### MultiIndex DataFrames
- Default MultiIndex uses `(key, name, units)` tuples for each variable
- Customizable via `attrs` parameter (e.g., `attrs=["name", "units"]`)
- Built by `vars_to_multi_index_data()` helper function
- Component variables automatically unpacked before DataFrame construction

---

## Code Conventions

### Import Pattern
Every source file starts with:
```python
from __future__ import annotations
```

### Type Annotations
- **Required** in `src/` (enforced by ruff `ANN` rule)
- **Disabled** in `tests/` (per `tool.ruff.lint.per-file-ignores`)
- Use `from typing import ...` and `from numpy.typing import NDArray`

### Docstrings
- **Style:** Google-style docstrings (enforced by ruff `D` + `pydocstyle.convention = "google"`)
- **Required** in `src/` (enforced by ruff `D` rule)
- **Disabled** in `tests/` (per `tool.ruff.lint.per-file-ignores`)
- **Format:**
  ```python
  def function(arg: type) -> return_type:
      """One-line summary.

      Longer description if needed.

      Args:
          arg (type): Description.

      Returns:
          return_type: Description.
      """
  ```

### Line Length
- **79 characters** (configured in `tool.ruff.line-length`)

### Ruff Rules
- **Selected:** `E` (pycodestyle errors), `F` (pyflakes), `B` (flake8-bugbear), `C90` (mccabe complexity), `I` (isort), `UP` (pyupgrade), `SIM` (flake8-simplify), `D` (pydocstyle), `ANN` (flake8-annotations)
- **Per-file ignores:**
  - `tests/*`: `ANN`, `D` disabled

---

## Known Gaps / Issues

### 1. `vardicts.py` is Empty
- **File:** `src/varmeta/vardicts.py`
- **Status:** Empty placeholder file with no implementation
- **Impact:** None currently — file exists but is not used

### 2. `ValDict.to_df()` Tested But Not Implemented
- **Issue:** `tests/test_doc_examples.py::TestValDictDocExamples::test_to_df` calls `val_dict_1.to_df()`
- **Problem:** This method **does not exist** on `ValDict` class
- **Status:** Test currently fails
- **Workaround:** The free function `valdict_list_to_df(valdict_lst, attrs?)` exists for list-based conversion
- **Location:** `src/varmeta/valdicts.py` — method needs to be added to `ValDict` class

### 3. No Method to Convert Single ValDict to DataFrame
- Current options:
  1. `ValDict.split()` → `(VarDict, dict)` → use `dict_to_df(var_dct, data_dct)` — works for single record
  2. `valdict_list_to_df([val_dict])` — wrap in list — works but awkward for single record
- Missing: Direct `ValDict.to_df()` instance method (see issue #2 above)

---

## Testing Notes

### Test Organization
- **Framework:** pytest
- **Structure:** Class-based test grouping (e.g., `class TestVar:`)
- **Fixtures:** Inline per file — **no `conftest.py`**
- **Naming:**
  - `tests/test_vars.py` → `class TestVar`
  - `tests/test_vars_numpy.py` → `class TestVar`
  - `tests/test_vars_pandas.py` → `class Test_Pandas_Integration`
  - `tests/test_vars_json.py` → `class TestVarJson`
  - `tests/test_doc_examples.py` → `class TestDocExamples`, `class TestValDictDocExamples`

### NumPy Assertions
- Use `numpy.testing.assert_array_equal(actual, expected)` for array comparisons
- Example:
  ```python
  import numpy as np
  from numpy.testing import assert_array_equal
  
  assert_array_equal(result, expected)
  ```

### Component Unpacking Tests
- Test both `component_axis=0` and `component_axis=1`
- Test with both Python lists and NumPy ndarrays
- Verify correct axis movement via `np.moveaxis`

### Integration Tests
- `test_doc_examples.py` mirrors README examples
- Ensures documentation examples remain valid
- Tests full round-trip workflows (define vars → create data → convert to DataFrame → serialize → deserialize)

---

## Common Workflows

### Define a Variable
```python
import varmeta as vm

temperature = vm.Var(
    key="temp",
    name="Temperature",
    units="Celsius",
    description="Ambient temperature",
    components=None,
    data_type="float"
)

force = vm.Var(
    key="force",
    name="Force",
    units="N",
    description="Force vector",
    components=("x", "y", "z"),
    component_axis=1
)
```

### Create VarDict and Data Dict
```python
TEMP = "temp"
FORCE = "force"

var_dct = vm.VarDict({TEMP: temperature, FORCE: force})
data_dct = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}
```

### Unpack Components
```python
vars, vals = vm.unpack(var_dct, data_dct)
# vars: {'temp': Temperature [Celsius], 'force_x': Force - x [N], ...}
# vals: {'temp': 25.0, 'force_x': 10.0, 'force_y': 20.0, 'force_z': 30.0}
```

### Create DataFrame from Dict
```python
df = vm.dict_to_df(var_dct, data_dct)
# MultiIndex columns: (key, name, units)
# Data automatically unpacked
```

### Create DataFrame from Records
```python
data_dict_lst = [
    {TEMP: 30, FORCE: [200, 250, -30]},
    {TEMP: 40, FORCE: [300, 350, -100]},
]
df = vm.records_to_df(var_dct, data_dict_lst)
```

### Serialize/Deserialize
```python
import json

# Serialize
var_data = vm.vars_to_dict(var_dct)
json_str = json.dumps(var_data)

# Deserialize
var_data_loaded = json.loads(json_str)
var_dct_recreated = vm.vars_from_dict(var_data_loaded)
```

### Use ValDict
```python
val_dict = vm.ValDict({temperature: 25.0, force: [10.0, 20.0, 30.0]})

# Split into VarDict and data dict
var_dct, data_dct = val_dict.split()

# Unpack components
unpacked_val_dict = val_dict.unpack()

# Serialize to ValData dict
valdata_dct = val_dict.to_valdata_dict()

# Deserialize from ValData dict
val_dict_recreated = vm.ValDict.from_valdata_dict(valdata_dct)
```

---

## Implementation Notes for AI Assistants

### When Adding New Features
1. **Update Public API Section** in this file if adding new exports to `__init__.py`
2. **Add Type Annotations** — required by ruff `ANN` rule in `src/`
3. **Add Google Docstrings** — required by ruff `D` rule in `src/`
4. **Keep Line Length ≤ 79** — enforced by ruff
5. **Add Tests** — follow class-based grouping pattern; no docstrings/annotations required in tests
6. **Update README.md** if adding user-facing features

### When Fixing Bugs
1. **Add Regression Test** before fixing
2. **Verify All Tests Pass** with `pytest`
3. **Run Ruff** to ensure no lint violations introduced

### When Refactoring
1. **Maintain Frozen Dataclass Contract** — `Var` must remain frozen and hashable
2. **Preserve `key` Field Behavior** — `compare=False` is critical for dict key usage
3. **Keep `__str__` Format** — `"Name [units]"` is relied upon for pandas column headers
4. **Maintain NumPy/List Compatibility** — component unpacking must work with both

### Priority Fixes Needed
1. **Implement `ValDict.to_df()`** — currently tested but not implemented (see Known Gaps #2)
2. **Decide on `vardicts.py`** — remove empty file or implement planned functionality

---

## Additional Resources

- **README.md** — User tutorial and examples
- **pyproject.toml** — Authoritative source for dependencies, build config, and ruff rules
- **tests/test_doc_examples.py** — Runnable versions of README examples

---

**End of AI Assistant Context Guide**

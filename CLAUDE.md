# varmeta — AI Assistant Context Guide

**Version:** 0.2.0  
**Python:** ≥ 3.11  
**Last Updated:** April 19, 2026

---

## Project Overview

`varmeta` is a lightweight Python library for attaching metadata (name, units, description, component structure) to variable identifiers and using that metadata to drive pandas DataFrame construction, serialization, and data unpacking in scientific and engineering workflows.

**Core Value Proposition:**
- Define variables with rich metadata once (`Var` instances)
- Collect them into a `VarSet` container
- Use shared literal string keys across `VarSet` and data dictionaries
- Automatically unpack multi-component variables (e.g., 3D force → force__x, force__y, force__z)
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
│       ├── __init__.py    # Public API re-exports (Var, VarData, VarSet)
│       ├── vars.py        # Core: Var dataclass, VarData TypedDict, internal helpers
│       └── varset.py      # VarSet: collection class with DataFrame/unpack/serialization
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
uv run pytest              # Run all tests
uv run pytest -v           # Verbose output
uv run pytest tests/test_vars.py  # Run specific test file
```

### Linting & Formatting
```bash
uv run ruff check src/    # Lint source code
uv run ruff check .       # Lint all Python files (including tests)
uv run ruff format src/   # Auto-format source code
```

### Build
```bash
python -m build           # Build distribution packages (requires build)
```

---

## Public API

All symbols exported from `src/varmeta/__init__.py`:

### Core Types
- **`Var`** — Frozen, ordered dataclass representing a variable with metadata (key, name, units, description, components, component_axis, data_type)
- **`VarData`** — `TypedDict` for `Var` serialization (all fields of `Var` as dict keys)

### Container
- **`VarSet`** — An ordered collection of `Var` instances with dict-like access, DataFrame construction, component unpacking, and serialization

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
  - `.component_vars()` — generates list of sub-Vars (e.g., `force` → `force__x`, `force__y`, `force__z`)
  - `.unpack(data)` — returns `(list[Var], list|NDArray)` — uses `np.moveaxis` for multi-dimensional arrays
  - `.unpack_tuples(data)` — returns `list[tuple[Var, value]]`

### `VarSet` Container
- Accepts `Sequence[Var]` or `dict[str, Var]` in constructor
- Dict-like access: `varset["temp"]` returns a `Var`; supports `in`, `len()`, iteration over keys
- **`.to_dataframe(data)`** — unified DataFrame creation; accepts single `dict` or `list[dict]`
- **`.unpack(data, raise_extra=False)`** — expands component variables, returns `(VarSet, dict)`
  - `raise_extra=True` raises KeyError for extra keys in data not in VarSet
  - `raise_extra=False` (default) silently ignores extra keys
- **`.pack(data, raise_missing=False)`** — reconstructs original structure from unpacked data with component keys
  - `raise_missing=True` raises KeyError if variables in VarSet are missing from data
  - `raise_missing=False` (default) silently skips missing variables
- **`.to_dict()` / `.from_dict()`** — JSON serialization round-trip

### Shared Literal String Keys
```python
# Pattern used throughout codebase and tests
TEMP = "temp"
FORCE = "force"

varset = VarSet([temperature_var, force_var])
data = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}
```
This pattern ensures consistency and prevents key mismatches between var metadata and data.

### Component Unpacking
- Variables can have `components=("x", "y", "z")` attribute
- `component_axis` (default 0) specifies which axis to unpack along
- Uses `np.moveaxis` internally → handles both Python lists and NumPy ndarrays uniformly
- Unpacked var keys follow pattern: `{original_key}__{component}` (e.g., `force__x`, `force__y`, `force__z`)
- Unpacked var names follow pattern: `{original_name} - {component}` (e.g., `Force - x`, `Force - y`, `Force - z`)
- **Component separator:** Double underscore `__` minimizes collision risk with regular variable names

### Component Packing
- `VarSet.pack(data, raise_missing=False)` reconstructs original structure from unpacked component data
- Reverses the unpacking operation: `force__x`, `force__y`, `force__z` → `force: [x, y, z]`
- Respects `component_axis` for multi-dimensional arrays
- Optional `raise_missing` parameter (default False):
  - `raise_missing=True`: Raises KeyError if variables in VarSet are missing from data
  - `raise_missing=False`: Silently skips variables not present in data
- Partial component keys always raise an error (e.g., having `force__x` but missing `force__y`)
- Round-trip invariant (when all data present): `varset.pack(varset.unpack(data)[1]) == data`

### MultiIndex DataFrames
- Default MultiIndex uses `(key, name, units)` tuples for each variable
- Customizable via `attrs` parameter (e.g., `attrs=["name", "units"]`)
- Component variables automatically unpacked before DataFrame construction

### Internal Helpers (in `vars.py`)
- **`_unpack(var_dct, data_dct)`** — expands components in both var and data dicts; used by `VarSet`
- **`_vars_to_multi_index_data(lst, attrs)`** — builds MultiIndex tuple list from Var attrs

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
  - `tests/test_doc_examples.py` → `class TestDocExamples`

### NumPy Assertions
- Use `numpy.testing.assert_array_equal(actual, expected)` for array comparisons

### Component Unpacking Tests
- Test both `component_axis=0` and `component_axis=1`
- Test with both Python lists and NumPy ndarrays

### Integration Tests
- `test_doc_examples.py` mirrors README examples
- Tests full round-trip workflows (define vars → create VarSet → create data → convert to DataFrame → serialize → deserialize)

---

## Common Workflows

### Define Variables and Create VarSet
```python
import varmeta as vm

TEMP = "temp"
FORCE = "force"

temperature = vm.Var(
    key=TEMP,
    name="Temperature",
    units="Celsius",
    description="Ambient temperature",
)

force = vm.Var(
    key=FORCE,
    name="Force",
    units="N",
    description="Force vector",
    components=("x", "y", "z"),
    component_axis=1,
)

varset = vm.VarSet([temperature, force])
```

### Create DataFrame from Dict
```python
data = {TEMP: [30, 40], FORCE: [[200, 250, -30], [300, 350, -100]]}
df = varset.to_dataframe(data)
# MultiIndex columns: (key, name, units)
# Components automatically unpacked
```

### Create DataFrame from Records
```python
records = [
    {TEMP: 30, FORCE: [200, 250, -30]},
    {TEMP: 40, FORCE: [300, 350, -100]},
]
df = varset.to_dataframe(records)
```

### Unpack Components
```python
data = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}
unpacked_varset, unpacked_data = varset.unpack(data)
# unpacked_data: {"temp": 25.0, "force__x": 10.0, "force__y": 20.0, "force__z": 30.0}

# Pack back to original structure
packed_data = varset.pack(unpacked_data)
# packed_data: {"temp": 25.0, "force": [10.0, 20.0, 30.0]}
```

### Serialize/Deserialize
```python
import json

# Serialize
var_data = varset.to_dict()
json_str = json.dumps(var_data)

# Deserialize
var_data_loaded = json.loads(json_str)
varset_recreated = vm.VarSet.from_dict(var_data_loaded)
```

---

## Implementation Notes for AI Assistants

### When Adding New Features
1. Add to `VarSet` class if it involves collection-level operations
2. Add to `Var` class if it involves single-variable behavior
3. **Add Type Annotations** — required by ruff `ANN` rule in `src/`
4. **Add Google Docstrings** — required by ruff `D` rule in `src/`
5. **Keep Line Length ≤ 79** — enforced by ruff
6. **Add Tests** — follow class-based grouping pattern
7. **Update README.md** if adding user-facing features

### When Fixing Bugs
1. **Add Regression Test** before fixing
2. **Verify All Tests Pass** with `uv run pytest`
3. **Run Ruff** with `uv run ruff check src/`

### When Refactoring
1. **Maintain Frozen Dataclass Contract** — `Var` must remain frozen and hashable
2. **Preserve `key` Field Behavior** — `compare=False` is critical for dict key usage
3. **Keep `__str__` Format** — `"Name [units]"` is relied upon for pandas column headers
4. **Maintain NumPy/List Compatibility** — component unpacking must work with both

---

## Additional Resources

- **README.md** — User tutorial and examples
- **pyproject.toml** — Authoritative source for dependencies, build config, and ruff rules
- **tests/test_doc_examples.py** — Runnable versions of README examples

---

**End of AI Assistant Context Guide**

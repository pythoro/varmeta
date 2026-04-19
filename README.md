
# varmeta

`varmeta` is a lightweight Python package for managing variable metadata in scientific, engineering, and data analysis workflows. It automatically unpacks multi-component variables and generates pandas DataFrames with rich multi-level column headers.

## Purpose

Scientific and engineering data often has variables with multiple components (e.g., x, y, and z components of a force vector). `varmeta` makes it easy to:

- Define variables once with metadata (name, units, description, components)
- Automatically unpack component variables (e.g., `force` → `force__x`, `force__y`, `force__z`)
- Generate pandas DataFrames with multi-index headers showing keys, names, and units
- Serialize and deserialize variable metadata to/from JSON

## Quick-start tutorial

### 1. Define variables with metadata

```python
import varmeta as vm

TEMP = "temp"
FORCE = "force"

# Scalar variable
temperature = vm.Var(
    key=TEMP,
    name="Temperature",
    units="Celsius",
    description="Ambient temperature",
)

# Vector variable (e.g., 3D force)
force = vm.Var(
    key=FORCE,
    name="Force",
    units="N",
    description="Force vector",
    components=("x", "y", "z"),
    component_axis=1,
)
```

### 2. Create a VarSet collection

```python
# Create a VarSet from a list of Var instances
varset = vm.VarSet([temperature, force])

# Dict-like access by key
print(varset[TEMP])  # Temperature [Celsius]
print(varset[FORCE])  # Force [N]
```

### 3. Unpack and pack data with components

Component variables can be unpacked (expanded) and packed (reconstructed):

```python
data = {TEMP: 25.0, FORCE: [10.0, 20.0, 30.0]}

# Unpack: expand components
unpacked_varset, unpacked_data = varset.unpack(data)
print(unpacked_data)
# {'temp': 25.0, 'force__x': 10.0, 'force__y': 20.0, 'force__z': 30.0}

# Pack: reconstruct original structure
packed_data = varset.pack(unpacked_data)
print(packed_data)
# {'temp': 25.0, 'force': [10.0, 20.0, 30.0]}
```

**Component separator:** Double underscore `__` (e.g., `force__x`) minimizes collision risk with regular variable names.

**Optional error handling:**
- `unpack(data, raise_extra=True)`: Raise error if data contains extra keys not in VarSet (default: silently ignore)
- `pack(data, raise_missing=True)`: Raise error if VarSet variables are missing from data (default: silently skip)

### 4. Create pandas DataFrames

It's easy to tabulate data into a DataFrame. Components are automatically unpacked, even from numpy arrays!

```python
# Single dict → DataFrame
data = {TEMP: [30, 40], FORCE: [[200, 250, -30], [300, 350, -100]]}
df = varset.to_dataframe(data)
print(df)
# key          temp  force__x  force__y  force__z
# name  Temperature Force - x Force - y Force - z
# units     Celsius         N         N         N
# 0              30       200       250       -30
# 1              40       300       350      -100
```

### 5. Create DataFrames from records

You can also pass a list of data dictionaries (records):

```python
records = [
    {TEMP: 30, FORCE: [200, 250, -30]},
    {TEMP: 40, FORCE: [300, 350, -100]},
]
df = varset.to_dataframe(records)
print(df)
# key          temp  force__x  force__y  force__z
# name  Temperature Force - x Force - y Force - z
# units     Celsius         N         N         N
# 0              30       200       250       -30
# 1              40       300       350      -100
```

## Serialization

You can serialize VarSet metadata to JSON and reconstruct it later:

```python
import json

# Serialize to JSON-compatible dict
var_data = varset.to_dict()
json_str = json.dumps(var_data)

# Deserialize from dict
varset_recreated = vm.VarSet.from_dict(json.loads(json_str))

# Verify equality
for key in varset:
    print(f"{key}: {'matches!' if varset[key] == varset_recreated[key] else 'differs!'}")
# Output:
# temp: matches!
# force: matches!
``` 






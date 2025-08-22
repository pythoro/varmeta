
# varmeta

`varmeta` is a lightweight Python package for managing variables and their metadata in scientific, engineering, and data analysis workflows. It provides a robust way to associate units, descriptions, and component structure with variables, making them hashable and easy to use as dictionary keys, DataFrame columns, or for serialization. The package is especially useful for handling vector/tensor variables (e.g., x, y, z components) and for keeping metadata and values tightly coupled.

## Purpose

`varmeta` solves the problem of keeping variable metadata (units, descriptions, components) in one place, while making variables easy to use in code. It enables:

- Hashable variable objects for use as dict keys or DataFrame columns
- Automatic handling of variables with components (e.g., vector/tensor variables)
- Easy unpacking of values into labeled components
- Consistent serialization and deserialization of variable metadata

## Quick-start tutorial

### 1. Define variables with metadata

```python
from varmeta.vars import Var

# Scalar variable
temperature = Var(
	key="temp",
	name="Temperature",
	units="Celsius",
	desciption="Ambient temperature",
	components=None
)

# Vector variable (e.g., 3D force)
force = Var(
	key="F",
	name="Force",
	units="N",
	desciption="Force vector",
	components=("x", "y", "z")
)
```

### 2. Use variables as dictionary keys

```python
data = {
	temperature: 25.0,
	force: [10.0, 20.0, 30.0]
}
print(data)
# Output:
# {Temperature [Celsius]: 25.0, Force [N]: [10.0, 20.0, 30.0]}
```

### 3. Unpack variables with components

```python
# Using the Var API directly
unpacked = force.unpack([10.0, 20.0, 30.0])
print(unpacked)
# Output:
# {Force x [N]: 10.0, Force y [N]: 20.0, Force z [N]: 30.0}
```

### 4. Store values and variables together

```python
from varmeta.vals import Val, ValList, ValDict

# Single value
val = Val(data=25.0, var=temperature)

# List of values
val_list = ValList(
	Val(data=10.0, var=force),
	Val(data=20.0, var=force),
	Val(data=30.0, var=force)
)

# Dictionary of variables and values
val_dict = ValDict({temperature: 25.0, force: [10.0, 20.0, 30.0]})
```

### 5. Use with pandas DataFrames

```python
import pandas as pd
from varmeta.vars import Var

var1 = Var(key="solar_radiation", name="Solar Radiation", units="W/m^2", desciption="Solar radiation at surface", components=None)
var2 = Var(key="mass", name="Mass", units="kg", desciption="Mass of the object", components=None)
df = pd.DataFrame({var1: [200, 300], var2: [3, 4]})
print(df)
# Output:
#    Solar Radiation [W/m^2]  Mass [kg]
# 0                  200         3
# 1                  300         4
```

### 6. Serialize and deserialize variable metadata

```python
# Serialize
var_dict = force.to_dict()

# Deserialize
force2 = Var(**var_dict)
assert force == force2
```

## More

See the `tests/` folder for more usage examples and edge cases.



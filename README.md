
# varmeta

`varmeta` is a small and lightweight Python package for managing and using variable metadata in scientific, engineering, and data analysis workflows in outputs. It's designed with type safety in mind for use with modern IDEs like VSCode + pylance.

## Purpose

We often have variables with several components (e.g. x, y, and z components). We want to use them as lists or arrays, but tabulate them nicely for outputs. `varmeta` solves this problem in a simple way. 

- Set up a dictionary of Var instances, with string keys.
- Set up matching dictionaries of data.
- Create pandas dataframes with nice multi-index headings containing not just the variable keys, but also their names and units, OR:
- Split variables into components automatically for other uses.

## Quick-start tutorial

### 1. Define variables with metadata

Let's first set up some imports, constants, and Var instances. 

```python
import varmeta as vm

TEMP = "temperature"
FORCE = "force"

# Scalar variable
temperature = vm.Var(
	key=TEMP,
	name="Temperature",
	units="Celsius",
	desciption="Ambient temperature",
	components=None
)

# Vector variable (e.g., 3D force)
force = vm.Var(
	key=FORCE,
	name="Force",
	units="N",
	desciption="Force vector",
	components=("x", "y", "z"),
	component_axis=1
)
```

### 2. Use literal keys for Var and data dictionaries

Use shared literal string keys for dictionaries of Var instances and
data dictionaries.

```python
data_dct = {
	TEMP: 25.0,
	FORCE: [10.0, 20.0, 30.0]
}

var_dct = {
	TEMP: temperature,
	FORCE: force
}
```

### 3. Unpack data with components

```python
vars, vals = vm.unpack(var_dct, data_dct)
print(vars)
# {'temp': Temperature [Celsius], 'force_x': Force - x [N], 'force_y': Force - y [N], 'force_z': Force - z [N]}
print(vals)
# {'temp': 25.0, 'force_x': 10.0, 'force_y': 20.0, 'force_z': 30.0}
```

### 5. Tabulate dict-based data into pandas DataFrames

It's easy to tabulate data into a DataFrame. Data is automatically unpacked,
even numpy arrays!

```python
data_dct = {FORCE: [[200, 250, -30], [300, 350, -100]], TEMP: [30, 40]}
df = vm.dict_to_df(var_dct, data_dct)
print(df)
# key     force_x   force_y   force_z        temp
# name  Force - x Force - y Force - z Temperature
# units         N         N         N     Celsius
# 0           200       250       -30          30
# 1           300       350      -100          40
data_dct = {TEMP: [30, 40], FORCE: [[200, 250, -30], [300, 350, -100]]}
df = vm.dict_to_df(var_dct, data_dct)
print(df)
# key          temp   force_x   force_y   force_z
# name  Temperature Force - x Force - y Force - z
# units     Celsius         N         N         N
# 0              30       200       250       -30
# 1              40       300       350      -100
```

### 6. Tabulate records easily

Say we'd had many records instead. We can make tables with lists of data
in dictionaries, unpacking each automatically, like this:

```python
data_dict_lst = [
	{FORCE: [200, 250, -30], TEMP: 30},
	{FORCE: [300, 350, -100], TEMP: 40},
]
df = vm.records_to_df(var_dct, data_dict_lst)
print(df)
# key     force_x   force_y   force_z        temp
# name  Force - x Force - y Force - z Temperature
# units         N         N         N     Celsius
# 0           200       250       -30          30
# 1           300       350      -100          40
```

## Serialisation

We can convert to dictionaries like this:
```python
var_data = vm.vars_to_dict(var_dct)
print(var_data)
# Output
# {'temp': {'key': 'temp', 'name': 'Temperature', 'units': 'Celsius', 'desciption': 'Ambient temperature', 'components': None, 'component_axis': 0, 'data_type': 'object'}, 'force': {'key': 'force', 'name': 'Force', 'units': 'N', 'desciption': 'Force vector', 'components': ('x', 'y', 'z'), 'component_axis': 1, 'data_type': 'object'}}
```

Then we can convert back to Var instances like this:
```python
var_dct_recreated = vm.vars_from_dict(var_data)
for k, v in var_dct_recreated:
	print(f"k: match is {v == var_dct[k]}")
# Output
# temp: match is True
# force: match is True
```

The data (`var_data`) can be easily saved and read from JSON using the 
standard *json* library. 






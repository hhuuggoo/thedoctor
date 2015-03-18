### thedoctor
The doctor is a library that makes python function input validation easy in attempt to keep large codebases sane.  The motivation is to make it easier to deal with large (often enterprise) code bases, where you look at a function and have no idea what it's supposed to take, or return.  Secondary motivation is to catch problems as early as possible in a stack trace.  The library is intentionally tiny and easy to understand - the core is 141 lines and the additional lines are just optional convenient validator functions.

The main entrypoint is the `validate` decorator.  The `validate` decorator
takes key word arguments, whose names should match the parameters to your function.  Each field accepts
either a list of validators, or a single validator.  If a validator is specified as a type or a tuple, it
 is assumed that the intention is for type checking.  Validators are merely functions which take the
 value of the argument in question, and throw an instance of thedoctor.ValidationError if validation
 fails.  In addition to field level validators, there is a `_all` validator, which is a validator
 which is passed a dictionary of argument names/argument values and can run validation across multiple
 function parameters.  Finally there is a `_return` validator, which runs validation against the return
 value of your function

### Installation

- With conda: `conda install -c hugo thedoctor`
- With pip:  `pip install thedoctor`

### Examples

#### Simple Type Checking

```
from thedoctor import validate

@validate(x=int, y=int)
def func(x, y):
    return x + y

@validate(x=(float, int), y=(float, int))
def func(x, y):
    return x + y
```

#### Ensure columns present in a dataframe
In this example, we ensure that the `data` parameter to the
function is both a pandas DataFrame, and has columns 'names' and 'dates'

```
from thedoctor import validate
from thedoctor.validators import has
import pandas as pd
@validate(data=[pd.DataFrame, has('names', 'dates')]):
def process(data):
    pass

```

#### Check values across all inputs

```
from thedoctor import validate
from thedoctor import ValidationError

def match_columns(all_args):
    x = all_args['x']
    y = all_args['y']
    if x.columns != y.columns:
        raise ValidationError("Column Mismatch")
@validate(_all=match_columns)
def add(x, y):
    return x + y
```

#### Check numpy broadcastability
```
from thedoctor import validate
from thedoctor.validators import broadcastable
@validate(_all=broadcastable('first', 'second'))
def process(first, second, third):
    pass
```

#### Check for singular matrices

```
from thedoctor import validate
from thedoctor.validators import nonsingular
@validate(first=nonsingular)
def process(first, second, third):
    pass
```
#### validators using lambdas

Sometimes it can be convenient to write ad-hoc validators as lambda functions.
Our validators raise Exceptions, and lambda functions cannot raise ad-hoc exceptions.
So we provide a `true` function which can be used as such

```
from thedoctor import validate
from thedoctor.validators import true
@validate(a=lambda x : true(x % 2 == 0, "Must be even"))
def func(a):
    pass
```

### Disabling validation
You can completely disable validation by setting the environment variable NO_DOCTOR before starting python.
If that variable is set - the validate decorator will return the original function


# thedoctor
python function input validation

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

```

from thedoctor import validate
from thedoctor.validators import has
import pandas as pd
@validate(data=[pd.DataFrame, has('names', 'dates')]):
def process(data):
    pass

```

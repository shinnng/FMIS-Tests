# PlatON-tracing
This is an automated test project of the PaltON-Go

## Installation and operation dependencies
Install the python 3.7 environment and configure pip, then execute the following command to install the dependency library:
```shell script
pip install -r requirements.txt
```
     
## Run test

### Execute all test cases

```shell script
pytest test_start.py --genesis "conf/genesis.json" --config "conf/config.yaml" 
```

### test case example:
```python
import pytest
@pytest.mark.P1
def test_case_001():
    print("begin: test_case_001")
    SomeTxAPI("test_case_001")
    print("end: test_case_001")
```
    

# Flight search service
Fourth project of non-relational databases

[Flight search service API](https://mif-nosql-assignments.s3.eu-central-1.amazonaws.com/2024/neo4j/neo4j-1.html) - reference point
> [!NOTE]
> **run.sh** for linux/mac, **run.bat** - for windows machines

> [!TIP]
To run python virtual environment for tests, use commands below

For windows:
```powershell
python -m venv ./.venv
./.venv/Scripts/activate.ps1 
pip3 install -r requirements.txt
pytest ./test/test_api.py
```

For linux/mac:
```shell
python -m venv ./.venv
source ./.venv/Scripts/activate.bat
pip3 install -r requirements.txt
pytest ./test/test_api.py
```
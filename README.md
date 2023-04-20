# CODEBUILD CI

Code Build Pipelines run Asynchronously and there is no provision to wait for them in bitbucket pipelines/ github actions to complete.
This project will wait for Codebuild pipeline to complete and log all the log events as well. This handles any abrupt pipeline stops.

## How to use

---

```bash
pip install codebuild-ci
```

```bash
python -m codebuild --project project --log-group <aws log group>
```

Checking for other options:

```bash
python -m codebuild --help
```

### Integrate with Bitbucket Pipeline

```yml
- script:
    - python -m pip install codebuild-ci
    - python -m codebuild-ci --project project --log-group <aws log group>
```

## contributing to code

---

You can Fork the repo and raise a PR for the active development.

## Tips for testing

---

### Stubbing Code

```python
from botocore.stub import Stubber
# stub code
stubber = Stubber(client)
stubber.add_response('start_build', {
    'build': {
        'id': 'foo-project:foo-id'
    }
})
stubber.add_response('batch_get_builds', {
    'builds': [{
        'id': 'foo-project:foo-id',
        'buildStatus': 'SUCCEEDED'
    }]
})
stubber.activate()
```

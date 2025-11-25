-# Develop
?TODO(add tags on syntax changes)

-## Scripts
Run all scripts from project directory.
- `apply` - installs all requirements, builds and installs package as editable
- `build-readme` - generates `README.md` from docs
- `run-tests` - invokes `unittest` and `pylint`

-## Tests
To run tests use `unittest` from project directory.
```sh
python -m unittest
```

If you're feeling fancy try `pylint` (also from project directory).
```sh
pylint src/yaptex/**/*.py
```

-## Code Style
Notes based on pylint yap:
- If the *docstring* is not needed fill it with some yap (best is to use something thematic).
- "Too few public methods" indicates that the file or mechanism might be too clean. There is no point in making it more stupid.
- Pylint is not deterministic.

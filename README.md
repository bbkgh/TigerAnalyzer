# TigerAnalyzer
Using a local LLM as a static analyzer (POC)

Analyzes git diffs of commits, runs rules over changes, and fails in case of errors.

https://github.com/astral-sh/ruff/issues/14085

## Usage:
``` bash
ollama run qwen2.5
pip install -r requirements.txt
# Update config.yaml
python ./analyzer.py COMMIT_ID
```

## Ideas:
- Modify analyzer.py to work with pre-commit.
- Add sample rules from ProjectX's git history.
- Suggest automatic rules for preventing the same kinds of bugs by using an LLM and git diffs of commits (prompt: suggest an analyzer rule if a bug exists).
- Run a commit suggester that reads the commit before committing and suggests refactors and hints for the current commit (learning)
- Make this more performant, single prompt with multiple rule
- Bigger context. Send related files (e.g: fields, ...)

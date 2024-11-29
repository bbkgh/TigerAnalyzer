#!/bin/python
import argparse
import subprocess

from ollama import Client
import yaml
from dataclasses import dataclass


@dataclass
class RuleResult:
    passed: bool
    result: str
    rule_name: str


def parse_config(path: str) -> dict:
    with open(path, "r") as file:
        return yaml.safe_load(file)


configs = parse_config("./config.yaml")


def get_git_diff_text(commit_id, git_directory):
    try:
        result = subprocess.run(
            ["git", "--no-pager", "diff", f"{commit_id}^", commit_id],
            capture_output=True,
            text=True,
            check=True,
            cwd=git_directory,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get git diff for commit {commit_id}.")
        print(f"Git error message: {e.stderr}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def analyze_diff_with_ollama(diff_text):
    results = []
    rules = configs["rules"]
    client = Client(host=configs["ollama"]["endpoint"])

    for rule in rules:
        response = client.chat(
            model=configs["ollama"]["model"],
            messages=[
                {
                    "role": "system",
                    # change this to llm
                    "content": "You are an Static analyzer tool. I give you git diff of new commit and one rule. you tell me if this rule is violated in new commit or not. if rule is violated say FAIL else say PASS.  Just consider changes lines in consideration. Be concise. Always Say FAIL or PASS in first line and say details after newline so Your first word must be PASS or FAIL. show final verdict result in first word.",
                },
                {
                    "role": "user",
                    "content": f"""The rule is : {rule['value']} 
                    Git commit diff is: 
                    {diff_text}""",
                },
            ],
        )
        result = response["message"]["content"]
        passed = not result.startswith("FAIL")
        results.append(RuleResult(result=result, rule_name=rule["name"], passed=passed))
        print(f"Rule: {rule['name']} - {result}")
    return results


def process_commit(commit_id, git_directory):
    diff_text = get_git_diff_text(commit_id, git_directory)
    print(f"{diff_text}")
    analysis_results = analyze_diff_with_ollama(diff_text)
    print(f"xxxxxx, {[a.passed for a in analysis_results]}")
    for result in analysis_results:
        if not result.passed:
            raise Exception(f"FAIL {result.rule_name} \n \n {result.result}")
    print(f"Analysis finished for Commit: {commit_id} without any errors.")


def main():
    parser = argparse.ArgumentParser(description="Process a commit ID")
    parser.add_argument(
        "commit_id",
        help="The commit hash to process",
        default="cc2739fbff205b03d090e8ec9cb7342668578938",
        nargs="?",
    )
    parser.add_argument(
        "directory",
        help="The git directory to process",
        default=".",
        nargs="?",
    )
    args = parser.parse_args()

    process_commit(args.commit_id, args.directory)


if __name__ == "__main__":
    main()

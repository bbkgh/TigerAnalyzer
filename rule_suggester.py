#!/bin/python
# import argparse
import subprocess

import yaml
from ollama import Client


def parse_config(path: str) -> dict:
    with open(path, "r") as file:
        return yaml.safe_load(file)


configs = parse_config("./config.yaml")


def get_all_commit_ids(git_directory) -> [str]: # type: ignore
    try:
        result = subprocess.run(
            ["git", "rev-list", "--all"],
            capture_output=True,
            text=True,
            check=True,
            cwd=git_directory,
        )
        commit_ids = result.stdout.strip().splitlines()
        return commit_ids

    except subprocess.CalledProcessError as e:
        print(f"Git error message: {e.stderr}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []


def get_message_and_diff(git_directory, commit_id):
    try:
        message_result = subprocess.run(
            ["git", "show", "-s", "--format=%s", commit_id],
            capture_output=True,
            text=True,
            check=True,
            cwd=git_directory,
        )
        commit_message = message_result.stdout.strip()
        diff_result = subprocess.run(
            ["git", "--no-pager", "diff", f"{commit_id}^", commit_id],
            capture_output=True,
            text=True,
            check=True,
            cwd=git_directory,
        )
        commit_diff = diff_result.stdout
        return commit_message, commit_diff
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to get git information for commit {commit_id}.")
        print(f"Git error message: {e.stderr}")
        return None, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None, None


def analyze_diff_with_ollama(diff_text, commit_message):
    client = Client(host=configs["ollama"]["endpoint"])

    response = client.chat(
        model=configs["ollama"]["model"],
        messages=[
            {
                "role": "system",
                "content": """You are a senior programming engineer. I give you git changes of commit and commit message. You suggest me some hints for better coding and if commit fixes a problem suggest me rules to consider for not take a same mistake in future. """,
            },
            {
                "role": "user",
                "content": f"""commit message: {commit_message} 
                    Git commit diff is: 
                    {diff_text}""",
            },
        ],
    )
    return response["message"]["content"]


def process_commit(git_directory, commit_id):
    diff_text, commit_message = get_message_and_diff(git_directory, commit_id)
    print(f"{commit_message=}\n\n{diff_text=}")
    analysis_results = analyze_diff_with_ollama(diff_text, commit_message)
    print(f"{analysis_results=}")


def main():
    # parser = argparse.ArgumentParser(description="Process a commit ID")
    # parser.add_argument(
    #     "commit_id",
    #     help="The commit hash to process",
    #     default="60391cba3d7dd6cad31cd47f39ca2db74334fb0c",
    #     nargs="?",
    # )
    # _args = parser.parse_args()
    # process_commit(git_directory, _args.commit_id)

    git_directory = "."
    ids = get_all_commit_ids(git_directory)
    for cid in ids:
        process_commit(git_directory, cid)


if __name__ == "__main__":
    main()

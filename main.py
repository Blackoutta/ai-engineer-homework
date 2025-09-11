from shlex import join
from tools.cloner import GitCloner
from dotenv import load_dotenv
import os
import subprocess
from prompts import REVIEW_PROMPT_EN, EXTRACT_REPO_INFO_PROMPT
import logging
from datetime import datetime
import json
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    force=True,
)

def parse_repo_info(output: str) -> dict:
    if not output or not isinstance(output, str):
        raise ValueError("Invalid output: expected non-empty string")

    # Try to extract JSON from fenced code block first
    codeblock_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", output, re.IGNORECASE)
    json_str = None
    if codeblock_match:
        json_str = codeblock_match.group(1)
    else:
        # If no fenced block, try direct JSON parse
        trimmed = output.strip()
        # If the whole output looks like JSON
        if trimmed.startswith("{") and trimmed.endswith("}"):
            json_str = trimmed
        else:
            # Fallback: best-effort to find the first {...} block
            first_brace = output.find("{")
            last_brace = output.rfind("}")
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                json_str = output[first_brace : last_brace + 1]

    if not json_str:
        raise ValueError("Failed to locate JSON in the provided output")

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {e}")

    # Normalize keys
    repo_url = (
        data.get("repo_url")
        or data.get("repo")
        or data.get("repository")
        or data.get("url")
    )
    branch = data.get("branch") or data.get("ref") or data.get("default_branch")
    user_homework_dir = (
        data.get("user_homework_dir")
        or data.get("homework_dir")
        or data.get("dir")
        or data.get("path")
    )

    if not repo_url:
        raise ValueError("Missing 'repo_url' or equivalent key in parsed data")

    # Ensure repo ends with .git for common hosts
    repo = repo_url.strip()
    if re.search(r"^(https?://|git@).+", repo) and not repo.endswith(".git"):
        # Only append for common git hosts when URL doesn't already end with .git
        if any(host in repo for host in ["github.com", "gitee.com", "gitlab.com", "bitbucket.org"]):
            repo = repo + ".git"

    if not branch:
        raise ValueError("Missing 'branch' in parsed data")
    if not user_homework_dir:
        raise ValueError("Missing 'user_homework_dir' in parsed data")

    return {
        "repo": repo,
        "branch": branch,
        "user_homework_dir": user_homework_dir,
    }

def main():
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    link = "https://gitee.com/aqualion/ai-engineer-training/tree/main/week03-homework-2"
    current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    homework_requirement_path = "./homework_requirement/week03-pt2.md"

    # extract repo info
    extract_repo_info_prompt = EXTRACT_REPO_INFO_PROMPT.format(link=link)
    repo_extraction_result = subprocess.run(
    "claude -p \"" + extract_repo_info_prompt + "\" --output-format json --allowed-tools Bash,Read,WebFetch",
    shell=True,
    capture_output=True,
    text=True,
    )
    logger.info(repo_extraction_result.stdout)
    stdout_json = json.loads(repo_extraction_result.stdout)

    repo = ""
    branch = ""
    user_homework_dir = ""

    try:
        repo_info = parse_repo_info(stdout_json["result"])
        repo = repo_info["repo"]
        branch = repo_info["branch"]
        user_homework_dir = repo_info["user_homework_dir"]
        logger.info(
            f"Parsed repo info -> repo: {repo}, branch: {branch}, user_homework_dir: {user_homework_dir}"
        )
    except Exception as e:
        logger.error(f"Failed to parse repo info: {e}")
        return
    tmp_dir = f"tmp/{current_timestamp}"

    # clone repository
    cloner = GitCloner()
    cloned_path = cloner.clone_repository(repo, tmp_dir, branch=branch)
    target_homework_dir = os.path.join(cloned_path, user_homework_dir)
    output_path = os.path.join(cloned_path, f"homework-review-{current_timestamp}.md")
    logger.info("output_path: " + output_path)
    logger.info(f"Cloned repository to {cloned_path}")

    # begin llm review process
    logger.info("inferencing...")
    final_review_prompt = REVIEW_PROMPT_EN.format(
        target_homework_dir=target_homework_dir,
         output_path=output_path,
          homework_requirement_path=homework_requirement_path)
    result = subprocess.run(
        "claude -p \"" + final_review_prompt + "\" --output-format json --allowed-tools Bash,Read,Write",
        shell=True,
        capture_output=True,
        text=True,
    )

    # print review results
    logger.info("Command stdout:")
    logger.info(result.stdout)
    logger.info(f"Command executed with exit code: {result.returncode}")

if __name__ == "__main__":
    main()
import json
import re
import subprocess
import logging
from typing import Dict, Optional, Any
from prompts import EXTRACT_REPO_INFO_PROMPT


class RepoExtractor:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("RepoExtractor")

    def extract_repo_info(self, link: str) -> Dict[str, str]:
        extract_repo_info_prompt = EXTRACT_REPO_INFO_PROMPT.format(link=link)
        
        try:
            repo_extraction_result = self._call_llm(extract_repo_info_prompt)
            stdout_json = json.loads(repo_extraction_result)
            
            repo_info = self._parse_llm_output(stdout_json["result"])
            self.logger.info(
                f"Parsed repo info -> repo: {repo_info['repo']}, "
                f"branch: {repo_info['branch']}, "
                f"user_homework_dir: {repo_info['user_homework_dir']}, "
                f"author: {repo_info['author']}"
            )
            
            return repo_info
            
        except Exception as e:
            self.logger.error(f"Failed to extract repo info: {e}")
            raise

    def _call_llm(self, prompt: str) -> str:
        result = subprocess.run(
            f"claude -p \"{prompt}\" --output-format json --allowed-tools Bash,Read,WebFetch",
            shell=True,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"LLM call failed with exit code {result.returncode}: {result.stderr}")
        
        self.logger.info(result.stdout)
        return result.stdout

    def _parse_llm_output(self, output: str) -> Dict[str, str]:
        if not output or not isinstance(output, str):
            raise ValueError("Invalid output: expected non-empty string")

        codeblock_match = re.search(r"```json\s*(\{[\s\S]*?\})\s*```", output, re.IGNORECASE)
        json_str = None
        
        if codeblock_match:
            json_str = codeblock_match.group(1)
        else:
            trimmed = output.strip()
            if trimmed.startswith("{") and trimmed.endswith("}"):
                json_str = trimmed
            else:
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

        repo_url = (
            data.get("repo_url")
            or data.get("repo")
            or data.get("repository")
            or data.get("url")
        )
        branch = data.get("branch") or data.get("ref") or data.get("default_branch")
        user_homework_dir = data.get("user_homework_dir", ".")
        
        author = data.get("author")

        if not repo_url:
            raise ValueError("Missing 'repo_url' or equivalent key in parsed data")

        repo = repo_url.strip()
        if re.search(r"^(https?://|git@).+", repo) and not repo.endswith(".git"):
            if any(host in repo for host in ["github.com", "gitee.com", "gitlab.com", "bitbucket.org"]):
                repo = repo + ".git"

        if not branch:
            raise ValueError("Missing 'branch' in parsed data")
        if not user_homework_dir:
            user_homework_dir = "."
        if not author:
            raise ValueError("Missing 'author' in parsed data")

        return {
            "repo": repo,
            "branch": branch,
            "user_homework_dir": user_homework_dir,
            "author": author,
        }
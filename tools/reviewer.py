import subprocess
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from prompts import REVIEW_PROMPT_EN


class Reviewer:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("Reviewer")

    def review_homework(
        self, 
        target_homework_dir: str, 
        homework_requirement_path: str, 
        output_path: str
    ) -> Dict[str, Any]:
        try:
            self.logger.info("Starting homework review process...")
            
            review_prompt = self._generate_review_prompt(
                target_homework_dir, homework_requirement_path, output_path
            )
            self.logger.info("review_prompt:\n " + review_prompt)
            
            result = self._call_llm(review_prompt)
            
            self.logger.info("Review completed successfully")
            self.logger.info(f"Command executed with exit code: {result.get('returncode', 'unknown')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to review homework: {e}")
            raise

    def _generate_review_prompt(
        self, 
        target_homework_dir: str, 
        homework_requirement_path: str, 
        output_path: str
    ) -> str:
        return REVIEW_PROMPT_EN.format(
            target_homework_dir=target_homework_dir,
            output_path=output_path,
            homework_requirement_path=homework_requirement_path
        )

    def _call_llm(self, prompt: str) -> Dict[str, Any]:
        self.logger.info("Calling LLM for review...")
        
        result = subprocess.run(
            f"claude -p \"{prompt}\" --output-format json --allowed-tools Bash,Read,Write",
            shell=True,
            capture_output=True,
            text=True,
        )
        
        if result.returncode != 0:
            self.logger.error(f"LLM call failed with exit code {result.returncode}")
            self.logger.error(f"Error output: {result.stderr}")
            raise RuntimeError(f"LLM call failed: {result.stderr}")
        
        self.logger.info("Command stdout:")
        self.logger.info(result.stdout)
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
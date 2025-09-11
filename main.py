import argparse
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from tools.cloner import GitCloner
from tools.repo_extractor import RepoExtractor
from tools.reviewer import Reviewer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    force=True,
)

def parse_args():
    parser = argparse.ArgumentParser(description="AI Homework Reviewer")
    parser.add_argument("--link", required=True, help="Repository link to extract")
    parser.add_argument("--req", required=True, help="Path to homework requirements")
    return parser.parse_args()

def main():
    load_dotenv()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    args = parse_args()
    current_timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Initialize components
    repo_extractor = RepoExtractor(logger)
    cloner = GitCloner(logger)
    reviewer = Reviewer(logger)

    try:
        # Extract repository information
        logger.info(f"Extracting repository info from: {args.link}")
        repo_info = repo_extractor.extract_repo_info(args.link)
        
        # Clone repository
        tmp_dir = f"tmp/{current_timestamp}"
        cloned_path = cloner.clone_repository(
            repo_info["repo"], 
            tmp_dir, 
            branch=repo_info["branch"]
        )
        
        # Setup paths
        target_homework_dir = os.path.join(cloned_path, repo_info["user_homework_dir"])
        logger.info("target_homework_dir: " + target_homework_dir)
        output_path = os.path.join(cloned_path, f"homework-review-{current_timestamp}.md")
        
        logger.info(f"Cloned repository to {cloned_path}")
        logger.info(f"Output path: {output_path}")
        
        # Perform review
        logger.info("Starting homework review...")
        review_result = reviewer.review_homework(
            target_homework_dir=target_homework_dir,
            homework_requirement_path=args.homework_requirement_path,
            output_path=output_path
        )
        
        logger.info(f"Review process completed successfully:\n{review_result}")
        
    except Exception as e:
        logger.error(f"Review process failed: {e}")
        raise

if __name__ == "__main__":
    main()
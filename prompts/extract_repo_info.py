EXTRACT_REPO_INFO_PROMPT = """
Given the following link: {link}
Extract the target information from the provided link in json format like this:
branch name is usually after /tree or /blob, before the final directory name
example1: 
link: https://gitee.com/JShengJun/ai-engineer-training/tree/homework/week03-2/week03-homework-2
{{
    "repo_url": "https://gitee.com/JShengJun/ai-engineer-training.git",
    "branch": "homework/week03-2",
    "user_homework_dir": "week03-homework-2",
    "author": "JShengJun"
}}
example2:
link: https://gitee.com/somebodys/week03-homework
if no /tree presented, then the branch name is main
{{
    "repo_url": "https://gitee.com/somebodys/week03-homework.git",
    "branch": "main",
    "user_homework_dir": "week03-homework",
    "author": "somebodys"
}}
MAKE SURE THE REPOSITORY IS VALID BEFORE OUTPUTING THE FINAL RESULT
DO NOT CLONE THE REPOSITORY YOURSELF, JUST OUTPUT THE JSON
"""
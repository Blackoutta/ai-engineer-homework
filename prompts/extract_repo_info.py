EXTRACT_REPO_INFO_PROMPT = """
Given the following link: {link}
Extract the target information from the provided link in json format like this:
# about branch name 
- branch name is usually after /tree or /blob and before the final directory name
- branch name may contain slash /, so be really careful
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
    "repo_url": "https://gitee.com/somebodys/ai-engineer-training/week03-homework.git",
    "branch": "main",
    "user_homework_dir": "week03-homework",
    "author": "somebodys"
}}
example3: branch name with slash
link: https://gitee.com/bai615/ai-engineer-training/tree/this/is/a/branch/week05-my-homework
{{
    "repo_url": "https://gitee.com/bai615/ai-engineer-training.git",
    "branch": "this/is/a/branch",
    "user_homework_dir": "week05-my-homework",
    "author": "bai615"
}}
MAKE SURE THE REPOSITORY IS VALID BEFORE OUTPUTING THE FINAL RESULT
DO NOT CLONE THE REPOSITORY YOURSELF, JUST OUTPUT THE JSON
"""
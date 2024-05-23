#!/usr/bin/python3
import json
import ollama
import argparse
import subprocess
from zhipuai import ZhipuAI

client = None
OLLAMA_URL = 'http://localhost:11434'
OLLAMA_MODEL_ENGINE = "llama3"
ZHIPU_API_KEY = "YOUR_API_KEY"
ZHIPU_MODEL_ENGINE = "glm-4"
PROMPT_FMT = '''
通俗易懂的角色描述：基于需求描述和实现该需求的git diff变更代码，自动生成规范的git提交信息。 
需求描述的标题如下：{title}

git diff变更代码如下：
(DIFF-START)
{git_diff}
(DIFF-END)

任务拆解
1.  解析需求标题： 
提取关键信息，如功能点、问题点等。
对文本进行清洗，去除无关字符和格式。
2.  分析git diff变更代码：
识别变更的文件和代码块。
分析代码变更的类型（如新增、修改、删除等）。
3.  生成Commit Message：
结合需求标题以及代码变更分析，编写Commit Message。 
确保提取的内容符合对应项的要求，如“summary: 少于30字的中文，简洁的、准确的描述Git Commit Message”等。
4.  验证Commit Message： 
检查Commit Message是否清晰、准确。
5.  按以下格式输出CommitMessage，『请仅输出内容，不要做任何解释』：
{{
  "summary": string  // 少于30字的中文，简洁的、准确的描述Git Commit Message
}}
'''


def commit_generate(api, title, git_diff):
    global client
    if api == "zhipu":
        if client is None:
            client = ZhipuAI(api_key=ZHIPU_API_KEY)
        return commit_generate_zhipu(client, title, git_diff)
    else:
        if client is None:
            client = ollama.Client(host=OLLAMA_URL, timeout=120)
        return commit_generate_ollama(client, title, git_diff)


def commit_generate_zhipu(client, title, git_diff):
    prompt = PROMPT_FMT.format(title=title, git_diff=git_diff)
    response = client.chat.completions.create(model=ZHIPU_MODEL_ENGINE,
                                              messages=[{
                                                  "role": "user",
                                                  "content": prompt
                                              }],
                                              temperature=0.95,
                                              top_p=0.7,
                                              max_tokens=4096)
    return json.loads(response.choices[0].message.content)["summary"]


def commit_generate_ollama(client, title, git_diff):
    prompt = PROMPT_FMT.format(title=title, git_diff=git_diff)
    response = client.chat(
        model=OLLAMA_MODEL_ENGINE,
        messages=[{
            "role": "user",
            "content": prompt
        }],
        options={
            "temperature": 2.5,
            "top_p": 0.99,
            "top_k": 100
        },
        format="json",
    )
    if response["done"]:
        return json.loads(response['message']['content'])["summary"]
    else:
        return "模型调用失败，请检查模型是否可用！"


def main():
    parser = argparse.ArgumentParser(description='AI COMMIT MESSAGE')
    parser.add_argument('-m',
                        '--message',
                        required=True,
                        type=str,
                        help='The message to be printed')
    parser.add_argument('--api',
                        default="ollama",
                        type=str,
                        help='default api is "ollama", online api is "zhipu"')
    args = parser.parse_args()

    title = args.message
    git_diff = subprocess.check_output(["git", "diff",
                                        "--cached"]).decode('utf-8')
    if git_diff == "":
        print("No changes to commit.")
        exit(0)

    while True:
        commit_message = commit_generate(args.api, title, git_diff)
        print(f"Generated commit message:\n{commit_message}")
        user_input = input("Accept commit message? (y/n/e): ")
        # Commit the changes or regenerate the message
        if user_input.lower() == "y":
            subprocess.run(["git", "commit", "-m", commit_message])
            print("Changes committed!")
            break
        elif user_input.lower() == "e":
            edited_text = input("Enter edited commit message: ")
            subprocess.run(["git", "commit", "-m", edited_text])
            print("Changes committed!")
            break
        else:
            print("Regenerating commit message...")


if __name__ == "__main__":
    main()

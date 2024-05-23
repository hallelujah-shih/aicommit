# aicommit
```
git commit msg generator tool (chinese version)
```

## usage
```
pip3 install --user -r requirements.txt

edit $HOME/.bashrc
--------------------
function git_ai_commit() {
    if [ "$#" -ne 1 ]; then
        echo "Usage: aicommit <git_commit_title>"
        return 1
    fi

    default_api="zhipu"
    python3 /path/to/aicommit.py --api "$default_api" -m "$1"
}

alias aicommit='git_ai_commit'
--------------------

可以根据自己的需要通过ollama api调用本地模型

source ~/.bashrc

aicommit "实现一个大陆使用的智能CommitMessage生成工具"
```

## ref
* [aicommit](https://github.com/Elhameed/aicommits)
* [大模型效能工具之智能CommitMessage](https://segmentfault.com/a/1190000044907149?utm_source=sf-similar-article)

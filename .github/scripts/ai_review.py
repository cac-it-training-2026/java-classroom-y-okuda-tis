import os
import google.generativeai as genai
from github import Github

# 環境変数から情報を取得
gemini_key = os.getenv("GEMINI_API_KEY")
github_token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")
pr_number = int(os.getenv("PR_NUMBER"))

# Geminiの設定
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-2.5-flash')

# GitHubクライアントの準備
g = Github(github_token)
repo = g.get_repo(repo_name)
pr = repo.get_pull(pr_number)

# 変更されたファイルの内容を取得してGeminiに投げる
files = pr.get_files()
for file in files:
    if file.filename.endswith(".java"):
        # プロンプトの工夫（答えを教えず、考えさせる）
        prompt = f"""
        あなたはJava研修の優しいメンターです。
        以下の受講生のコードをレビューし、初学者に向けた改善のアドバイスを3点以内で日本語で伝えてください。
        
        【ルール】
        - コンパイルエラーや実行時エラーについては該当箇所を明確に伝える。
        - 答え（修正コード）をそのまま教えない。
        - 命名規則、読みやすさ、Javaの作法について触れる。
        - できた部分は褒める。
        
        ファイル名: {file.filename}
        コード:
        {file.patch}
        """
        response = model.generate_content(prompt)
        
        # PRにコメントとして投稿
        pr.create_issue_comment(f"### 🤖 Geminiメンターのレビュー\n{response.text}")

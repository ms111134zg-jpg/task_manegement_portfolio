# ベースイメージ（軽量なslim版を使う）
FROM python:3.13-slim

# コンテナ内の作業ディレクトリを設定
WORKDIR /app

# 依存ライブラリを先にコピー＆インストール
# （コードより先にやることでキャッシュが効き、ビルドが速くなる）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリのコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# コンテナ起動時に実行するコマンド
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
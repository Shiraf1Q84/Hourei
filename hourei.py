import streamlit as st
import sqlite3
import spacy
from spacy.lang.ja import Japanese

# spaCyモデルのロード（大きめの日本語モデルを使用）
try:
    nlp = spacy.load("ja_core_news_lg")
except IOError:
    st.error("spaCyの日本語モデルがインストールされていません。'python -m spacy download ja_core_news_lg'を実行してインストールしてください。")
    st.stop()

# データベース接続
def get_db_connection():
    return sqlite3.connect('law_database.db')

# 法令データの取得
def get_laws(cursor):
    cursor.execute("SELECT id, name, article_number, content FROM laws")
    return cursor.fetchall()

# 自然言語処理による検索
def search_laws(query, laws):
    doc = nlp(query)
    
    # 検索結果をランキングする
    ranked_results = []
    for law in laws:
        law_doc = nlp(law[3])  # 条文本文
        similarity = law_doc.similarity(doc)
        ranked_results.append((similarity, law))
    ranked_results.sort(key=lambda x: x[0], reverse=True)

    # 上位10件まで返す
    return [result[1] for result in ranked_results[:10]]

# Streamlit アプリケーション
def main():
    st.title("法令検索")

    query = st.text_input("キーワードまたは文章を入力してください")

    if query:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                laws = get_laws(cursor)
                
            results = search_laws(query, laws)
            if results:
                st.write("検索結果:")
                for law in results:
                    st.subheader(f"{law[1]} - {law[2]}")
                    st.write(law[3])
            else:
                st.write("該当する条文が見つかりませんでした。")
        except sqlite3.Error as e:
            st.error(f"データベースエラーが発生しました: {e}")
        except Exception as e:
            st.error(f"予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":
    main()
import streamlit as st
import sqlite3
from spacy.lang.ja import Japanese
from spacy.tokens import Doc
from spacy.matcher import Matcher

# データベース接続
conn = sqlite3.connect('law_database.db')
cursor = conn.cursor()

# 法令データの取得 (仮データ)
def get_laws():
    cursor.execute("SELECT id, name, article_number, content FROM laws")
    laws = cursor.fetchall()
    return laws

# spaCyモデルのロード
nlp = Japanese()
matcher = Matcher(nlp.vocab)

# 自然言語処理による検索
def search_laws(query):
    doc = nlp(query)
    matches = matcher(doc)

    # 検索結果をランキングする
    ranked_results = []
    for law in get_laws():
        law_doc = nlp(law[3]) # 条文本文
        similarity = law_doc.similarity(doc)
        ranked_results.append((similarity, law))
    ranked_results.sort(key=lambda x: x[0], reverse=True)

    # 上位10件まで表示
    return [result[1] for result in ranked_results[:10]]

# Streamlit アプリケーション
def main():
    st.title("法令検索")

    query = st.text_input("キーワードまたは文章を入力してください")

    if query:
        results = search_laws(query)
        if results:
            st.write("検索結果:")
            for law in results:
                st.subheader(f"{law[1]} - {law[2]}")
                st.write(law[3])
        else:
            st.write("該当する条文が見つかりませんでした。")

if __name__ == "__main__":
    main()
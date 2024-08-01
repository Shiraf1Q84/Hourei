import streamlit as st
import pandas as pd

@st.cache_resource
def load_spacy_model():
    import spacy
    return spacy.load("ja_core_news_lg")

nlp = load_spacy_model()

# CSVファイルからデータを読み込む
@st.cache_data
def load_data():
    return pd.read_csv('laws.csv')

laws_df = load_data()

# 検索関数
def search_laws(query):
    doc = nlp(query)
    ranked_results = []
    for _, law in laws_df.iterrows():
        law_doc = nlp(law['content'])
        similarity = law_doc.similarity(doc)
        ranked_results.append((similarity, law))
    ranked_results.sort(key=lambda x: x[0], reverse=True)
    return [result[1] for result in ranked_results[:10]]

# メイン関数
def main():
    st.title("法令検索")
    query = st.text_input("キーワードまたは文章を入力してください")
    if query:
        results = search_laws(query)
        if results:
            st.write("検索結果:")
            for law in results:
                st.subheader(f"{law['name']} - {law['article_number']}")
                st.write(law['content'])
        else:
            st.write("該当する条文が見つかりませんでした。")

if __name__ == "__main__":
    main()

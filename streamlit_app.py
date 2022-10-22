import datetime
import time
import tools

import streamlit as st
import pymongo

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Set up webpage
page_title = "Some Youtube statistics"
page_icon = ":chart:"
layout = "centered"

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# Some data
locations = {"CA": [43.65, -79.35], "GB": [51.50, -0.118], "JP": [35.65, 139.84], "KR": [37.53, 127.03],
             "MX": [19.43, -99.133], "RU": [55.75, 37.61]}
country = ["All", "CA", "GB", "JP", "KR", "MX", "RU"]
video_category = ['All', 'Film & Animation', 'Autos & Vehicles', 'Music', 'Pets & Animals', 'Sports', 'Short Movies',
                  'Travel & Events', 'Gaming', 'Videoblogging', 'People & Blogs', 'Comedy', 'Entertainment',
                  'News & Politics', 'Howto & Style', 'Education', 'Science & Technology', 'Movies', 'Anime/Animation',
                  'Action/Adventure', 'Classics', 'Comedy', 'Documentary', 'Drama', 'Family', 'Foreign', 'Horror',
                  'Sci-Fi/Fantasy', 'Thriller', 'Shorts', 'Shows', 'Trailers']

# Query example
# {Country: "CA", category_id: 10, views:{$gt:1000}, likes:{$gt:1000}, dislikes:{$gt:1000}, comment_count:{$gt:1000},
# trending_date: "17.14.11", comments_disabled: "FALSE", ratings_disabled: "FALSE", video_error_or_removed: "FALSE"}

# If country is ALL then it is not included
# T/F also when they're none
# {"Country": selected_country, "category_id": tools, "views":{$gt:views}, "likes":{$gt:likes}, "dislikes":{$gt:dislikes}, "comment_count":{$gt:comments},
# "trending_date": tools, "comments_disabled": comm_disabled, "ratings_disabled": rating_disabled, "video_error_or_removed": video_removed}

# Set up database connection
@st.experimental_singleton
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()
videos = client["Estadisticas"]["Videos"]

dv = False

with st.container():
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("Set your filters")
        with st.expander("Geography"):
            col1, col2 = st.columns(2)
            selected_country = col1.selectbox("Select Country:", country, key="country")
        with st.expander("Numbers"):
            col3, col4, = st.columns(2)
            with col3:
                category = st.selectbox("Select Category:", video_category, key="category")
                views = st.number_input("Views greater than:", min_value=0, format="%i", step=100)
                likes = st.number_input("Likes greater than:", min_value=0, format="%i", step=100)
                dislikes = st.number_input("Dislikes greater than:", min_value=0, format="%i", step=100)
                comments = st.number_input("Comment count greater than:", min_value=0, format="%i", step=100)
        with st.expander("Date"):
            date = st.date_input("Select trending date:", min_value=datetime.date(2017, 11, 14),
                                 max_value=datetime.date(2018, 6, 14), value=datetime.date(2017, 11, 14))
            st.info("This dataset only contains data from 2017/11/14 to 2018/06/14")
        with st.expander("Other filters"):
            comm_disabled = st.radio("Comment disabled:", ["BOTH", "TRUE", "FALSE"])
            rating_disabled = st.radio("Rating disabled:", ["BOTH", "TRUE", "FALSE"])
            video_removed = st.radio("Video removed:", ["BOTH", "TRUE", "FALSE"])

        # request = {"Country": selected_country,
        #            "category_id": tools.translate_category_by_name(category),
        #            "views": {"$gt": views},
        #            "likes": {"$gt": likes},
        #            "dislikes": {"$gt": dislikes},
        #            "comment_count": {"$gt": comments},
        #            "trending_date": tools.pretty_date(date.strftime("%Y/%m/%d")),
        #            "comments_disabled": comm_disabled,
        #            "ratings_disabled": rating_disabled,
        #            "video_error_or_removed": video_removed}

        request = {"views": {"$gt": views},
                   "likes": {"$gt": likes},
                   "dislikes": {"$gt": dislikes},
                   "comment_count": {"$gt": comments},
                   "trending_date": tools.pretty_date(date.strftime("%Y/%m/%d"))}

        "---"

        submitted = st.form_submit_button("Save filters")
        if submitted:
            loaded_data = tools.request(request)
            with st.spinner('Wait for it...'):
                time.sleep(3)
            st.success('Done!')
            dv = True

    if dv:
        with st.form("Data Visualization"):
            st.subheader("Data Visualization")
            # substitutable data
            d1 = {"status": ["cd", "cnd"], "value": [300, 200]}
            d2 = {"status": ["rd", "rnd"], "value": [175, 325]}
            d3 = {"status": ["r", "nr"], "value": [50, 450]}

            df1 = pd.DataFrame(data=d1)
            df2 = pd.DataFrame(data=d2)
            df3 = pd.DataFrame(data=d3)

            tv = 0
            tl = 0
            tdl = 0
            dic_cat = {}
            for item in loaded_data:
                tv += item["views"]
                tl += item["likes"]
                tdl += item["dislikes"]

                t = tools.translate_category_by_id(item["category_id"])
                if t in dic_cat.keys():
                    dic_cat[t] += item["views"]
                else:
                    dic_cat[t] = item["views"]

            nr = tl + tdl
            nr = tv - nr

            dic = {"Category": [], "Views": []}

            for cat in dic_cat:
                dic["Category"].append(cat)
                dic["Views"].append(dic_cat[cat])

            df = pd.DataFrame(data=dic)
            names = df["Category"]
            values = df["Views"]


            def plot_map(trending_countries):
                df = []
                for c in trending_countries:
                    df.append(locations[c])
                df = pd.DataFrame(df, columns=["lat", "lon"])
                st.map(df)


            submitted = st.form_submit_button("Plot data")
            with st.expander("Sankey chart"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Views on trending", tv)
                col2.metric("Likes", tl)
                col3.metric("Dislikes", tdl)
                col4.metric("Not rated", nr)

                # Crate sankey chart
                label = ["Views", "Total views", "Like", "Dislike", "Not rated"]
                source = [0] + [1] * 3
                target = [1, 2, 3, 4]
                value = [tv, tl, tdl, nr]

                # data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30, color="#E694FF")
                data = go.Sankey(link=link, node=node)

                # plot it
                fig = go.Figure(data)
                fig.update_layout(margin=dict(l=0, r=0, t=5, b=5))
                st.plotly_chart(fig, use_container_width=True)
            with st.expander("Category pie"):
                fig2 = px.pie(df, values=values, names=names, title="Category proportion")
                fig2.update_layout(legend_title_text="Category")
                fig2.update_traces(textposition="inside", textinfo="percent+label")
                st.plotly_chart(fig2, use_container_width=True)
            with st.expander("Comments, Rating and Video disabled"):
                col1, a = st.columns(2)
                col2, a = st.columns(2)
                col3, a = st.columns(2)
                with col1:
                    names = df1["status"]
                    values = df1["value"]
                    fig3 = px.pie(df1, values=values, names=names, title="Comment disabled proportion")
                    fig3.update_layout(legend_title_text="Disabled")
                    fig3.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(fig3, use_container_width=True)
                with col2:
                    names = df2["status"]
                    values = df2["value"]
                    fig4 = px.pie(df2, values=values, names=names, title="Rating disabled proportion")
                    fig4.update_layout(legend_title_text="Disabled")
                    fig4.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(fig4, use_container_width=True)
                with col3:
                    names = df3["status"]
                    values = df3["value"]
                    fig5 = px.pie(df3, values=values, names=names, title="Video disabled proportion")
                    fig5.update_layout(legend_title_text="Disabled")
                    fig5.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(fig5, use_container_width=True)
            with st.expander("Trending Map"):
                selected_video = st.selectbox("Trending videos on " + date.strftime("%Y/%m/%d"), video_category)
                df = ["GB", "JP", "KR", "MX", "RU"]
                if submitted:
                    plot_map(df)


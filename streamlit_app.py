import datetime
import time
import tools

import streamlit as st
import pymongo

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

dv = False
# Set up webpage
page_title = "Some Youtube statistics"
page_icon = ":chart:"
layout = "centered"

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

# Some data
locations = {"CA": [43.65, -79.35], "GB": [51.50, -0.118], "JP": [35.65, 139.84], "KR": [37.53, 127.03],
             "MX": [19.43, -99.133], "RU": [55.75, 37.61]}


# Set up database connection
@st.experimental_singleton
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])


client = init_connection()
videos = client["Estadisticas"]["Videos"]

with st.container():
    with st.expander("Web propose"):
        st.info("This web works as a visual expose of some data collected from youtube videos. "
                "It can be use to compare tendencies among videos and their geography audience.")
    with st.form("entry_form"):
        st.subheader("Set your filters")
        with st.expander("Numbers"):
            col3, col4, = st.columns(2)
            with col3:
                # category = st.selectbox("Select Category:", video_category, key="category")
                views = st.number_input("Views greater than:", min_value=0, value=0, format="%i", step=100)
                likes = st.number_input("Likes greater than:", min_value=0, value=0, format="%i", step=100)
                dislikes = st.number_input("Dislikes greater than:", min_value=0, value=0, format="%i", step=100)
                comments = st.number_input("Comment count greater than:", min_value=0, value=0, format="%i", step=100)
        with st.expander("Date"):
            date = st.date_input("Select trending date:", min_value=datetime.date(2017, 11, 14),
                                 max_value=datetime.date(2018, 6, 14), value=datetime.date(2017, 11, 14))
            st.info("This dataset only contains data from 2017/11/14 to 2018/06/14")
        with st.expander("Other filters"):
            comm_disabled = st.radio("Comment disabled:", ["BOTH", "TRUE", "FALSE"])
            rating_disabled = st.radio("Rating disabled:", ["BOTH", "TRUE", "FALSE"])
            video_removed = st.radio("Video removed:", ["BOTH", "TRUE", "FALSE"])

        request = {"views": {"$gt": views},
                   "likes": {"$gt": likes},
                   "dislikes": {"$gt": dislikes},
                   "comment_count": {"$gt": comments},
                   "trending_date": tools.pretty_date(date.strftime("%Y/%m/%d"))}

        if comm_disabled != "BOTH":
            request["comments_disabled"] = comm_disabled

        if rating_disabled != "BOTH":
            request["ratings_disabled"] = rating_disabled

        if video_removed != "BOTH":
            request["video_error_or_removed"] = video_removed

        "---"

        submitted = st.form_submit_button("Save filters")
        if submitted:
            # st.write(request)
            loaded_data = tools.request(request)
            with st.spinner('Wait for it...'):
                time.sleep(3)
            st.success('Done!')
            dv = True

    if dv:
        with st.container():
            st.subheader("Data Visualization")

            tv = 0
            tl = 0
            tdl = 0
            dic_cat = {}
            vid_names = []
            total_videos = 0

            comment_status = ["Disabled", "Not Disabled"]
            cs = [0, 0]

            rating_status = ["Disabled", "Not Disabled"]
            rs = [0, 0]

            video_status = ["Removed", "Not Removed"]
            vs = [0, 0]

            for item in loaded_data:
                total_videos += 1

                tv += item["views"]
                tl += item["likes"]
                tdl += item["dislikes"]

                if item["comments_disabled"] == "TRUE":
                    cs[0] += 1
                else:
                    cs[1] += 1

                if item["ratings_disabled"] == "TRUE":
                    rs[0] += 1
                else:
                    rs[1] += 1

                if item["video_error_or_removed"] == "TRUE":
                    vs[0] += 1
                else:
                    vs[1] += 1

                t = tools.translate_category_by_id(item["category_id"])
                if t in dic_cat.keys():
                    dic_cat[t] += item["views"]
                else:
                    dic_cat[t] = item["views"]

                name = item["title"]
                if name in vid_names:
                    pass
                else:
                    vid_names.append(name)

            nr = tl + tdl
            nr = tv - nr

            dic = {"Category": [], "Views": []}

            for cat in dic_cat:
                dic["Category"].append(cat)
                dic["Views"].append(dic_cat[cat])

            df = pd.DataFrame(data=dic)
            names = df["Category"]
            values = df["Views"]

            d1 = {"status": comment_status, "value": cs}
            d2 = {"status": rating_status, "value": rs}
            d3 = {"status": video_status, "value": vs}

            df1 = pd.DataFrame(data=d1)
            df2 = pd.DataFrame(data=d2)
            df3 = pd.DataFrame(data=d3)

            st.metric("Total number of entries", tools.millify(total_videos))

            with st.expander("Sankey chart"):
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Views on trending", tools.millify(tv))
                col2.metric("Likes", tools.millify(tl))
                col3.metric("Dislikes", tools.millify(tdl))
                col4.metric("Not rated", tools.millify(nr))

                # Crate sankey chart
                label = ["Views", "Total views", "Like", "Dislike", "Not rated"]
                source = [0] + [1] * 3
                target = [1, 2, 3, 4]
                value = [tv, tl, tdl, nr]

                # data to dict, dict to sankey
                link = dict(source=source, target=target, value=value)
                node = dict(label=label, pad=20, thickness=30, color="#5dc1b9")
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
                selected_video = st.selectbox("Trending videos on " + date.strftime("%Y/%m/%d"), vid_names)

                request = {"trending_date": tools.pretty_date(date.strftime("%Y/%m/%d")),
                           "title": selected_video}
                video_popularity = tools.request(request)

                countries = []
                for item in video_popularity:
                    c = item["Country"]
                    if c in countries:
                        pass
                    else:
                        countries.append(c)

                df = []
                for c in countries:
                    df.append(locations[c])
                df = pd.DataFrame(df, columns=["lat", "lon"])
                st.map(df)

st.write("Made with :heart: by Kemer, Leonard and Will")

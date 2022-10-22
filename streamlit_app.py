import datetime
import time

import streamlit as st

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

#Some data
locations = {"CA": [43.65, -79.35], "GB": [51.50, -0.118], "JP": [35.65, 139.84], "KR": [37.53, 127.03], "MX": [19.43, -99.133], "RU": [55.75, 37.61]}
country = ["All", "CA", "GB", "JP", "KR", "MX", "RU"]
video_category = ['All','Film & Animation','Autos & Vehicles','Music','Pets & Animals','Sports','Short Movies','Travel & Events','Gaming','Videoblogging','People & Blogs','Comedy','Entertainment','News & Politics','Howto & Style','Education','Science & Technology','Movies','Anime/Animation','Action/Adventure','Classics','Comedy','Documentary','Drama','Family','Foreign','Horror','Sci-Fi/Fantasy','Thriller','Shorts','Shows','Trailers']

#Set up webpage
page_title = "Some Youtube statistics"
page_icon = ":chart:"
layout = "centered"

st.set_page_config(page_title=page_title, page_icon=page_icon, layout=layout)
st.title(page_title + " " + page_icon)

with st.container():
    with st.form("entry_form", clear_on_submit=True):
        st.subheader("Set your filters")
        with st.expander("Geography"):
            col1, col2 = st.columns(2)
            col1.selectbox("Select Country:", country, key="country")
        with st.expander("Numbers"):
            col3, col4, = st.columns(2)
            with col3:
                category = st.selectbox("Select Category:", video_category, key="category")
                views = st.number_input("Views greater than:", min_value=0, format="%i", step=100)
                likes = st.number_input("Likes greater than:", min_value=0, format="%i", step=100)
                dislikes = st.number_input("Dislikes greater than:", min_value=0, format="%i", step=100)
                comments = st.number_input("Comment count greater than:", min_value=0, format="%i", step=100)
        with st.expander("Date"):
            date = st.date_input("Select trending date:", min_value=datetime.date(2017, 11, 14), max_value=datetime.date(2018, 6, 14), value=datetime.date(2017, 11, 14))
            st.info("This dataset only contains data from 2017/11/14 to 2018/06/14")
        with st.expander("Other filters"):
            title = st.text_input("Video name filter", placeholder="Search exactly what video you want")
            comm_disabled = st.radio("Comment disabled:", ["NONE", "TRUE", "FALSE"])
            rating_disabled = st.radio("Rating disabled:", ["NONE", "TRUE", "FALSE"])
            video_removed = st.radio("Video removed:", ["NONE", "TRUE", "FALSE"])
        "---"
        submitted = st.form_submit_button("Save filters")
        if submitted:
            with st.spinner('Wait for it...'):
                time.sleep(3)
            st.success('Done! See your request on "Data Visualization"')
    with st.form("Data Visualization"):
        st.subheader("Data Visualization")
        # substitutable data
        d1 = {"status": ["cd", "cnd"], "value": [300, 200]}
        d2 = {"status": ["rd", "rnd"], "value": [175, 325]}
        d3 = {"status": ["r", "nr"], "value": [50, 450]}

        df1 = pd.DataFrame(data=d1)
        df2 = pd.DataFrame(data=d2)
        df3 = pd.DataFrame(data=d3)

        tv = 2000
        tl = 1000
        tdl = 500
        nr = tl + tdl
        nr = tv - nr

        df = pd.read_excel("Book1.xlsx")
        names = df["cat"]
        values = df["views"]

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

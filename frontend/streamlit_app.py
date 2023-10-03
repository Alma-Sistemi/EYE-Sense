import streamlit as st
from streamlit_option_menu import option_menu

st.set_page_config(page_title="EYE-Sense ",page_icon = 'favicon', layout="wide")
from apps.utils import initialize
from apps import sarShipDetectionGEE,sarShipDetection,home, landSurfaceTemperature,nightlights,atmospheric,waterQuality,vhrDetection  # import your app modules here
import json

#st.set_page_config(page_title="Streamlit Geospatial", layout="wide")




styles = {
    "container": {
        "margin-top": "0 !important",
        "padding": "10px !important"
    }, # Full width
    "nav-item":{"width":"100% !important"},
}

select = option_menu(
            menu_title=None,  # required
            options=["Services", "Use Cases", "Project Info"],  # required
            default_index=0,  # optional
            icons = ["wrench","book","file-fill"],
            orientation="horizontal",
            styles=styles,
)





st.markdown(
            f'''
            <style>
                 
                .nav-item .icon.bi-caret-right {{
                    display: none !important;
                }}

                .reportview-container .sidebar-content {{
                    padding-top: {1}rem;
                }}
                .reportview-container .main .block-container {{
                    padding-top: {1}rem;
                }}
            </style>
            ''',unsafe_allow_html=True)

#st.components.v1.html('<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.9.1/font/bootstrap-icons.css">')

# A dictionary of apps in the format of {"App title": "App icon"}
# More icons can be found here: https://icons.getbootstrap.com
#{"func": upload.app, "title": "Ship Detection", "icon": "tsunami"},
#{"func": upload.app, "title": "Plane Detection", "icon":"gear"},
# {"func": landSurfaceTemperature.app, "title": "Land Surface Temperature", "icon": "map"},
# {"func": upload.app, "title": "SAR Ship Detection","icon":"tsunami"},
#{"func": vhrDetection.app, "title": "   VHR Object Detection","icon":"gear"},
apps = [
    {"func": home.app, "title": "Home", "icon": "houseGIBBERISH"},
    {"func": sarShipDetectionGEE.app,"title": "Ship Detection GEE","icon":"tsunami"},
    {"func": nightlights.app, "title": "    Nightlight Activity", "icon": "lamp-fill"},
    {"func": landSurfaceTemperature.app, "title": "     Land Surface Temperature", "icon": "map"},
    {"func": waterQuality.app, "title": "   Water Quality", "icon": "water"},
    {"func": atmospheric.app, "title": "    Atmospheric Quality", "icon": "globe2"},
    {"func": sarShipDetection.app, "title": "   SAR Ship Detection","icon":"tsunami"},
    {"func": vhrDetection.app, "title": "   VHR Object Detection","icon":"gear"},
    
]



titles = [app["title"] for app in apps]
titles_lower = [title.lower() for title in titles]
icons = [app["icon"] for app in apps]

params = st.experimental_get_query_params()

if "page" in params:
    default_index = int(titles_lower.index(params["page"][0].lower()))
else:
    default_index = 0








# Used to hide hamburger Menu
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

if select == "Services":
    with st.sidebar:
        st.markdown( 
            """
                <link rel="stylesheet" href="cdn.jsdelivr.net/npm/bootstrap-icons@1.10.2/font/…">
            """
        ,unsafe_allow_html=True)

        
        # icons=icons,
        selected = option_menu(
            menu_title = None,
            options=titles[1:],
            icons=icons[1:],
            menu_icon=None,
            default_index=default_index,
        )

    
        st.markdown( 
            """
                <link rel="stylesheet" href="cdn.jsdelivr.net/npm/bootstrap-icons@1.10.2/font/…">
                <div style="bottom:-500px; position:absolute; display:hidden;">
                    <h3 style="margin-top:0; text-align:center;">Economy bY spacE (EYE)<h3>
                    <img src="https://i.imgur.com/x9fJelE.png" width="100%" style="margin-top:0; position:absolute;"/>
                    <p style="margin-top:120px; font-size:70%">
                    Marie Skłodowska-Curie Actions (MSCA)  Research and Innovation Staff Exchange (RISE) H2020-MSCA-RISE-2020 G.A. 101007638
                    </p>
                    <!-- 
                    <img src="https://i.imgur.com/yEF6GB3.png" width="100%" style="bottom:0px; position:relative;"/>
                    -->
                    
                </div>
            """
        ,unsafe_allow_html=True)
        
    

   


    for app in apps[1:]:

        if app["title"] == selected:
            app["func"]()
            break
else:
    apps[0]['func']()
    
        

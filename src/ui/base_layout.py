import streamlit as st


def style_background_home():
    st.markdown("""
    <style>

    .stApp{
        background: #8ea1ff   !important}
    </style>

    
    """,unsafe_allow_html=True)


def style_background_dashboard():
    st.markdown("""
    <style>

    .stApp{
        background: #E0E3FF; 
     !important}
    </style>

    
    """,unsafe_allow_html=True)





def style_base_layout():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&display=swap');@import url('https://fonts.googleapis.com/css2?family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&display=swap');

   
    .block-container{
        padding-top: 1.5rem;
        }

    .stApp{
        background-color: 5865F2 !important
        }
    .stApp div[data-testid="stHorizontalBlock"] {
    display: flex;              /* Ensure flex layout */
    flex-direction: row;        /* Align children side by side */
   
    transform: translateX(-50px);                /* Space between the boxes */
}

    .stApp div[data-testid="stColumn"]{
        background-color: #E0E3FF !important;
        padding: 2.7rem !important;
        border-radius: 4.5rem !important;
       
    }

    h1{
        font-family: 'Google Sans', sans-serif !important;
        font-size: 3.5rem !important;
        line-height:1.1 !important;
        margin-bottom:0 rem !important;
        
    
    }

    h2{
        font-family: 'Google Sans', sans-serif !important;
        font-size: 3.5rem !important;
        line-height:1.1 !important;
        margin-bottom: 0rem !important;
    
    }
    h3, h4, p {
        font-family: 'Outfit', sans-serif, bold !important;
        text-align: left;
        color: black !important; 
    }

    button:hover{
        transform: scale(1.1) !important;
    }

    button{
        border-radius: 1.5rem !important;
        background-color: purple !important;
        color: white !important;
        padding: 10px 20px !important;
        border: none !important;
        transition: transform 0.25s ease-in-out !important;
        cursor: pointer !important;

    }

    button[kind="Secondary"]{
        border-radius: 1.5rem !important;
        background-color: #222222 !important;
        color: white !important;
        padding: 10px 20px !important;
        border: none !important;
        transition: transform 0.25s ease-in-out !important;
    }

     button[kind="Tertiary"]{
        border-radius: 1.5rem !important;
        background-color: purple !important;
        color: white !important;
        padding: 10px 20px !important;
        border: none !important;
        transition: transform 0.25s ease-in-out !important;
    }

    
    
        /* Button styles */
.stButton>button {
    border-radius: 5px !important;
    color: white !important;
}

/* Teacher Portal button */
.stButton>button:nth-of-type(1) {
    background-color: #5865f2 !important;
    font-weight: bold;
    width: 200px !important;
}

/* Student Portal button */
.stButton>button:nth-of-type(2) {
    background-color: #49c347 !important;
    font-weight: bold;
    width: 200px !important;
    margin-right: 250px !important;
    margin-left: 250px !important;
    position: absolute;
   right: -160px; /* pushes it to sharp edge */
    bottom: 20px;
}

/* Container to center buttons */
.button-container {
    display: flex;
    justify-content: center;
    gap: 25px;  /* Space between buttons */
}


    </STYLE>


    
    """,unsafe_allow_html=True)
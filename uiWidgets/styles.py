from .theme import apply_theme

primary_button = apply_theme("""
    color: white;
    margin: 14px 20px;
    margin-right: 0;
    padding: 8px; 
    background-color: {color.primary_green};
    border-radius: 5%;
    font-size: 13px;
    font-weight: bold;
    QToolTip { 
       background-color: black; 
       color: white; 
       border: black solid 1px
   }
""")

progress_bar = """    
    QProgressBar {
        color: white;
        width: 100px;
        border: 2px solid #9fa6ad;
        background-color: #9fa6ad;
        border-radius: 5%;
        text-align: center;
        font-size: 13px;
        font-weight: bold;
    }
    QProgressBar::chunk {
        border-radius: 5%;
        background: QLinearGradient( x1: 0, y1: 0, x2: 1, y2: 0,
            stop: 0 #5dcc77,
            stop: 0.4999 #40cc61,
            stop: 0.5 #22d04b,
            stop: 0.75 #06d036,
            stop: 1 #09a92f 
        );
    }
"""

title_label = apply_theme("""
    color: {color.secondary_green};
    padding: 4px;
    font-size: 16px;
    font-weight: bold;
""")

loading_label = apply_theme("""
    color: {color.primary_green};
    padding: 4px;
    font-size: 16px;
    font-weight: bold;
""")

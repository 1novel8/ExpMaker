from .theme import apply_theme

primary_button = apply_theme("""
    QPushButton::hover {
        color: {color.primary_light};
        border: none;
    }
    QPushButton::disabled {
        background-color: {color.light_gray};
    }
    QPushButton {
        color: {color.secondary_light};
        margin: 14px 20px;
        margin-right: 0;
        padding: 8px; 
        background-color: {color.primary_green};
        border: 1px solid {color.light_gray};
        border-radius: 5%;
        font-size: 13px;
        font-weight: bold;
    }
    QToolTip { 
       background-color: {color.primary_light};
       color: {color.dark_gray}; 
       border: 1px solid {color.primary_green};
   }
""")

default_table = apply_theme("""
    QHeaderView::section{
        background-color: {color.primary_blue};
        color: {color.primary_light};
        padding: 2px;
        margin: 1px;
        border-radius: 2px; 
        font-size: 14px;
        font-weight: bold;
    }
    alternate-background-color: {color.secondary_light};
    background-color: {color.background_light};
    border-radius: 3px; 
    border: 1px solid {color.dark_gray};
    color: #1E54B1; 
    font-size: 12px
""")

representation_table_label = """
    color: #D3D3D3; 
    background-color: #323C3D;
    font-size: 14px; 
    padding: 0 15px;
"""

splitter = """
    QSplitter::handle:horizontal {
        # background: {color.primary_green};
        # border: 1px solid #777;
        width: 3px;
        margin-top: 2px;
        margin-bottom: 2px;
        border-radius: 1px;
    }
"""

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
    font-size: 16px;
    font-weight: bold;
""")

loading_label = apply_theme("""
    color: {color.primary_green};
    padding: 4px;
    font-size: 16px;
    font-weight: bold;
""")


class ExpSelectorStyles:
    root = apply_theme("""
        background-color: {color.primary_blue};
        color: {color.primary_light};
        padding: 0;
        margin: 0;
        border-radius: 4px; 
        font-size: 14px;
        font-weight: bold;
    """)
    dropdown = apply_theme("""
        border-radius: 2px;
        font-size: 12px; 
        padding: 0 2px;
        color: white; 
        min-height: 14px;
        border: 1px solid #C3FFF1;
    """)
    title = """
        color: #C3FFF1;
        font-size: 12px;
        min-height: 14px;
    """


class SourceWidgetStyles:
    src_lbl = """
        color: white; 
        margin: 0; 
        padding: 4px; 
        background-color: #115f50; 
        border-top-left-radius: 8%;
        border-bottom-left-radius: 8%;
        border: 1px solid #00BA4A
    """
    title_lbl = """
        color: #115f50;
        padding: 4px;
        font-size: 12px;
        font-weight: bold;
    """
    src_btn = """
        background-color: #00BA4A; 
        color: white;
        padding: 5px;
        font-size: 15px;
        border-top-right-radius: 8%;
        border-bottom-right-radius: 8%;
    """

class Color:
    primary_light = 'white'
    secondary_light = '#f3f3f4'
    background_light = '#cacad3'
    primary_green = '#00BA4A'
    secondary_green = '#115f50'
    primary_blue = '#07c'
    secondary_blue = '#035793'
    light_gray = '#9fa6ad'
    dark_gray = '#5f6062'
    accent_red = 'red'


theme = {
    'color': Color(),
}


def apply_theme(styles):
    def format_style(style):
        if '{' in style and '}' in style:
            return style.format(**theme)
        return style

    splitted_styles = styles.split('\n')
    return ''.join(map(format_style, splitted_styles))
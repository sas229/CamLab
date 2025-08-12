def get_color_for_rpm(rpm):
    """Get color based on RPM value with finer gradients every 50 RPM"""
    if rpm >= 1200:
        return "#FF0000"    # Pure Red
    elif rpm >= 1150:
        return "#FF1A1A"    # Bright Red
    elif rpm >= 1100:
        return "#FF3333"    # Light Red
    elif rpm >= 1050:
        return "#FF4D4D"    # Lighter Red
    elif rpm >= 1000:
        return "#FF6666"    # Very Light Red
    elif rpm >= 950:
        return "#FF794D"    # Red-Orange
    elif rpm >= 900:
        return "#FF8533"    # Dark Orange
    elif rpm >= 850:
        return "#FF944D"    # Medium-Dark Orange
    elif rpm >= 800:
        return "#FFA64D"    # Medium Orange
    elif rpm >= 750:
        return "#FFB366"    # Light Orange
    elif rpm >= 700:
        return "#FFC080"    # Very Light Orange
    elif rpm >= 650:
        return "#FFD11A"    # Dark Yellow
    elif rpm >= 600:
        return "#FFD633"    # Medium-Dark Yellow
    elif rpm >= 500:
        return "#FFE680"    # Medium Yellow
    elif rpm >= 450:
        return "#FFEB99"    # Light Yellow
    elif rpm >= 400:
        return "#99FF99"    # Very Light Green
    elif rpm >= 350:
        return "#66FF66"    # Light Green
    elif rpm >= 300:
        return "#33FF33"    # Medium-Light Green
    elif rpm >= 250:
        return "#1AFF1A"    # Medium Green
    elif rpm >= 200:
        return "#00FF00"    # Pure Green
    elif rpm >= 150:
        return "#33FF33"    # Medium-Light Green
    elif rpm >= 100:
        return "#66FF66"    # Light Green
    else:
        return "#99FF99"    # Very Light Green

def get_dial_label_style(is_active=False, rpm=0):
    """Get the style for the dial value label based on state and RPM"""
    if is_active:
        color = get_color_for_rpm(abs(rpm))
    else:
        color = "white"
        
    return f"""
        QLabel {{
            font-size: 11pt;
            font-weight: bold;
            color: {color};
        }}
    """

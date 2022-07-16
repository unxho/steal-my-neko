def get_media(m):
    if m.photo:
        return m.photo
    if m.video:
        return m.video
    if m.animation:
        return m.animation

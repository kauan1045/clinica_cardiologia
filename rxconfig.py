import reflex as rx

config = rx.Config(
    app_name="ProjetoCl_nicaCardiologia",
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@600&family=Poppins:wght@600&display=swap",
    ],
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(),
    ]
)
import streamlit as st
from gsheetsdb import connect
import toml

from utils.ui import to_do, to_button, image_from_url

INIT_GSHEET = f"""**If you don't have one yet, [create a new Google Sheet](https://sheets.new/)**.  

Give it any name, and fill it with mock data."""

MAKE_IT_PUBLIC = f"""**Make sure that your Sheet is public**  

Open your Sheet, click on {to_button("Share")} > {to_button("Share with ...")} and select {to_button("Anyone with the link can view")}."""

PASTE_INTO_SECRETS = f"""**Paste these TOML credentials into your Streamlit Secrets! **  

To open your settings, click on {to_button("Manage app")} > {to_button("⋮")} > {to_button("⚙ Settings")} and then update {to_button("Sharing")} and {to_button("Secrets")}"""


@st.experimental_singleton()
def get_connector():
    connector = connect()

    assert st.secrets["gsheets"]["public_gsheets_url"].startswith(
        "https://docs.google.com/"
    ), "Invalid URL, must start with https://docs.google.com"

    return connector


def tutorial():

    to_do(
        [
            (st.write, INIT_GSHEET),
        ],
        "google_sheet_public_gsheet",
    )

    to_do(
        [
            (st.write, MAKE_IT_PUBLIC),
            (
                st.image,
                image_from_url(
                    "https://user-images.githubusercontent.com/7164864/143441230-0968925f-86a0-4bf1-bc89-c8403df6ef36.png"
                ),
            ),
        ],
        "make_it_public",
    )

    def url_to_toml():
        url_input_str = st.text_input("URL of the Google Sheet")
        convert = st.button("Create TOML credentials")
        if url_input_str or convert:
            if not url_input_str.startswith("https://docs.google.com/"):
                st.error(
                    "Invalid URL! The URL must start with https://docs.google.com. Please retry!"
                )
            else:
                toml_output = toml.dumps(
                    {"gsheets": {"public_gsheets_url": url_input_str}}
                )
                st.code(toml_output, "toml")

    to_do(
        [
            (
                st.write,
                """**Create TOML credentials**""",
            ),
            (url_to_toml,),
        ],
        "google_sheet_creds_formatted",
    )

    to_do(
        [
            (st.write, PASTE_INTO_SECRETS),
            (
                st.image,
                image_from_url(
                    "https://user-images.githubusercontent.com/7164864/143465207-fa7ddc5f-a396-4291-a08b-7d2ecc9512d2.png"
                ),
            ),
        ],
        "copy_pasted_secrets",
    )


def app():
    import streamlit as st
    import pandas as pd
    from gsheetsdb import connect

    # Share the connector across all users connected to the app
    @st.experimental_singleton()
    def get_connector():
        return connect()

    # Time to live: the maximum number of seconds to keep an entry in the cache
    TTL = 24 * 60 * 60

    # Using `experimental_memo()` to memoize function executions
    @st.experimental_memo(ttl=TTL)
    def query_to_dataframe(_connector, query: str) -> pd.DataFrame:
        rows = _connector.execute(query, headers=1)
        dataframe = pd.DataFrame(list(rows))
        return dataframe

    @st.experimental_memo(ttl=600)
    def get_data(_connector, gsheets_url) -> pd.DataFrame:
        return query_to_dataframe(_connector, f'SELECT * FROM "{gsheets_url}"')

    st.markdown(f"## 📝 Connecting to a public Google Sheet")

    gsheet_connector = get_connector()
    gsheets_url = st.secrets["gsheets"]["public_gsheets_url"]

    data = get_data(gsheet_connector, gsheets_url)
    st.write("👇 Find below the data in the Google Sheet you provided in the secrets:")
    st.dataframe(data)

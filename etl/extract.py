import time
from pathlib import Path

import pandas as pd
import requests
import toml
from bs4 import BeautifulSoup
from loguru import logger
from parse import parse

STEM_FILENAME = "/file?uri=/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/datasets/monthlyfiguresondeathsregisteredbyareaofusualresidence/"
ONS_URL_DATA_PAGE = "https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/deaths/datasets/monthlyfiguresondeathsregisteredbyareaofusualresidence"
ONS_MAIN_URL = "https://www.ons.gov.uk"

# Read local `config.toml` file.
config = toml.load("config.toml")
MIN_YEAR = config["min_year"]


def find_files(url: str) -> list:
    """Finds all xlsx and xls files at a given url.

    Args:
        url (str): Web page to look for files on.

    Returns:
        list: file links with extensions
    """
    soup = BeautifulSoup(requests.get(url).text, features="html5lib")

    hrefs = [a["href"] for a in soup.find_all("a")]
    hrefs = [a for a in hrefs if len(a.split(".")) > 1]
    hrefs = [
        a for a in hrefs if (a.split(".")[1] == "xlsx" or a.split(".")[1] == "xls")
    ]
    return hrefs


def download_and_save_file(file_url: str, file_name: str):
    """Grabs known files from ONS' website and downloads them.

    Args:
        file_url (str): The url where the data file can be found.
        file_name (str): What to save the file under going forwards.

    Returns:
        str: same as input
    """
    # if scratch path doesn't exist, create it
    dl_path = Path(config["downloads_location"])
    dl_path.mkdir(parents=True, exist_ok=True)
    # Now check if file exists already. If not, dl it
    file_location = dl_path / file_name
    if file_location.is_file():
        logger.info(f"Skipping download of {file_name}; file already exists")
    else:
        r = requests.get(ONS_MAIN_URL + file_url, stream=True)
        with open(file_location, "wb") as f:
            f.write(r.content)
    logger.info(f"Success: file download of {file_name} complete")


def get_the_urls_of_files() -> pd.DataFrame:
    """Retrieves data file URLs from the ONS website

    Returns:
        pd.DataFrame: Data frame containing href, file_name, year, and file_extension
    """
    list_of_hrefs = find_files(ONS_URL_DATA_PAGE)
    # filter these to fit the /{year}/ukbusinessworkbook{year}.{filename} pattern
    text_to_parse = STEM_FILENAME + "{year}/{name}.{file_extension}"
    list_of_dict_of_info = [parse(text_to_parse, url).named for url in list_of_hrefs]
    for x, y in zip(list_of_dict_of_info, list_of_hrefs):
        x["href"] = y
    # put these in a data frame for convenience.
    files_to_dl_df = pd.DataFrame.from_dict(list_of_dict_of_info)
    files_to_dl_df["year"] = files_to_dl_df["year"].astype(int)
    files_to_dl_df = files_to_dl_df.loc[files_to_dl_df["year"] >= MIN_YEAR, :].copy()
    # new file names for these
    files_to_dl_df["file_name"] = files_to_dl_df.apply(
        lambda x: str(x["year"]) + "." + x["file_extension"], axis=1
    )
    return files_to_dl_df


def get_ons_deaths_data() -> None:
    files_to_dl_df = get_the_urls_of_files()
    for index, row in files_to_dl_df.iterrows():
        time.sleep(1)
        logger.info("Downloading" + row["file_name"])
        download_and_save_file(row["href"], row["file_name"])


if __name__ == "__main__":
    get_ons_deaths_data()

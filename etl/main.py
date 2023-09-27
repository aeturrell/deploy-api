from extract import get_ons_deaths_data
from transform import transform_from_excel_to_tidy_parquet


def main_flow():

    get_ons_deaths_data()
    transform_from_excel_to_tidy_parquet()


if __name__ == "__main__":
    main_flow()

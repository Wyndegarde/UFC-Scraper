from ufc_scraper.base_classes import DataFrameABC


class CacheProcessor(DataFrameABC):
    def clear_cache(self):
        ...

    def check_cache(self):
        ...

    def add_to_cache(self):
        ...

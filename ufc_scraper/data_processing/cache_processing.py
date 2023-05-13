import pandas as pd

from ufc_scraper.base_classes import DataFrameABC


class CacheProcessor(DataFrameABC):
    """
    This Class is responsible for checking for links that have already been scraped.
    Currently skips events that have already been scraped and retrieves fighter profile information if it has already been processed.
    """

    def __init__(
        self, csv_path: str, cache_column_name: str, allow_creation: bool = False
    ) -> None:
        super().__init__(csv_path, allow_creation)
        self.cache_df: pd.DataFrame = self._instantiate_df()
        self.cache_column_name: str = cache_column_name

    def check_cache(self, link: str) -> bool:
        """
        Checks the cache for a link. If it exists, returns True. If it does not exist, returns False.

        Args:
            link (str): The link to check for.

        Returns:
            bool: True if the link exists in the cache, False if it does not.
        """
        return bool(link in self.object_df[self.cache_column_name].values)

    def clear_cache(self) -> None:
        """
        Clears the cache.
        """
        self.object_df = pd.DataFrame(columns=[self.cache_column_name])

    def add_to_cache(self, link_to_add: str) -> None:
        """
        Adds a link to the cache.

        Args:
            link_to_add (str): The link to add to the cache.
        """
        # self.object_df.loc[len(self.object_df)] = {self.cache_column_name: link_to_add}

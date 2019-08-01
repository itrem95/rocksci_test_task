import pandas as pd


class AssetPerfomances:
    """
    Calculate price, currency and total perfomances for each asset.
    All supporting functions have "private" visible.
    All function with used in next calculations data  have "protected" visible.
    """

    def __init__(self) -> None:
        """
        Upload next data:
        • prices.csv Daily asset prices. Columns: asset ids, rows: dates
        • currencies.csv Asset currency. Columns: currency, rows: asset id
        • weights.csv Daily portfolio weights. Columns: asset id, rows: dates
        • exchanges.csv Daily exchange rate (to dollar). Columns: currency names, rows: dates
        """
        self._prices = pd.read_csv('prices.csv', index_col=0)
        self._exchanges = pd.read_csv('exchanges.csv', index_col=0)
        self._currencies = pd.read_csv('currencies.csv', index_col=0)
        self._weights = pd.read_csv('weights.csv', index_col=0)

    @staticmethod
    def __replace_na_values(column: pd.Series) -> pd.Series:
        """
         Replace missing values with the last valid value.
        :param column: Series with missing values
        :return: Series after replacement missing values
        """
        column.fillna(method='ffill', inplace=True)
        column.fillna(method='bfill',
                      inplace=True)  # if elements at start of the column have NaN value, it will be replaced by the 1st valid value in this column
        return column

    @staticmethod
    def __get_new_index(df: pd.DataFrame) -> pd.DataFrame:
        """
        Some dataframes have different indexes range. Changing index in Dataframe to "daily".
        :param df: Dataframe with "weekday" range
        :return: Dataframe with "daily" range
        """
        new_df = pd.DataFrame(index=pd.date_range(df.index[0], df.index[-1], freq='D'))
        new_df = new_df.join(df)

        return new_df

    def __get_series_by_currency(self, asset: str) -> pd.Series:
        """
        Get currency values for asset.
        Catch exception KeyError because Dataframe "currencies" hasn't column with USD currency.
        :param asset: Current asset
        :return: Series with currency values for this asset
        """
        try:
            column = self._currencies.loc[asset].values
            return self._exchanges[column].squeeze()
        except KeyError:
            return pd.Series([1] * len(self._exchanges), index=self._exchanges.index)

    def __count_return_prices_for_asset(self, asset: str) -> pd.Series:
        """
        Calculate return price for asset.
        :param asset: Current asset
        :return: Series with price perfomance for this asset
        """
        self.__new_prices = self.__get_new_index(self._prices)
        self.__new_prices = self.__replace_na_values(self.__new_prices[asset])
        perfomance_for_asset = []

        for i in range(1, len(self.__new_prices)):
            perfomance_for_asset.append((self.__new_prices.iloc[i] - self.__new_prices.iloc[
                i - 1]) / self.__new_prices.iloc[i - 1])

        return pd.Series(perfomance_for_asset)

    def __count_currency_perfomance_for_asset(self, asset: str) -> pd.Series:
        """
        Calculate currency perfomance for asset.
        :param asset: Current asset
        :return: Series with currency perfomance for this asset
        """
        cur_currency = self._currencies.loc[asset].values[0]
        if cur_currency == 'USD':
            return pd.Series([0] * (len(self._exchanges) - 1))
        self.__new_exchanges = self.__replace_na_values(self._exchanges[cur_currency])
        perfomance_for_asset = []

        for i in range(1, len(self.__new_exchanges)):
            perfomance_for_asset.append((self.__new_exchanges.iloc[i] - self.__new_exchanges.iloc[
                i - 1]) / self.__new_exchanges.iloc[i - 1])

        return pd.Series(perfomance_for_asset)

    def __count_total_perfomance_for_asset(self, asset: str) -> pd.Series:
        """
        Calculate total perfomance for asset.
        :param asset: Current asset
        :return: Series with total perfomance for asset
        """
        self.__new_prices = self.__get_new_index(self._prices)
        self.__new_prices = self.__replace_na_values(self.__new_prices[asset]).values
        perfomance_for_asset = []

        self.__currency_for_asset = self.__get_series_by_currency(asset).values

        for i in range(1, len(self.__new_prices)):
            value1 = self.__currency_for_asset[i] * self.__new_prices[i]
            value2 = self.__currency_for_asset[i - 1] * self.__new_prices[i - 1]
            perfomance_for_asset.append((value1 - value2) / value2)

        return pd.Series(perfomance_for_asset)

    def _calculate_price_perfomance_for_all_assets(self) -> pd.DataFrame:
        """
        Calculate price perfomance for all assets.
        :return: Dataframe with price perfomance for each asset.
        """
        price_perform_df = pd.DataFrame()

        for column in self._prices.columns:
            price_perform_df[column] = self.__count_return_prices_for_asset(column)
        price_perform_df.index = self.__get_new_index(self._prices).index[1:]
        return price_perform_df

    def _calculate_currency_perfomance_for_all_assets(self) -> pd.DataFrame:
        """
        Calculate currency perfomance for all assets.
        :return: Dataframe with currency perfomance for each asset.
        """
        currency_perform_df = pd.DataFrame()

        for column in self._prices.columns:
            currency_perform_df[column] = self.__count_currency_perfomance_for_asset(column)
        currency_perform_df.index = self.__get_new_index(self._exchanges).index[1:]

        return currency_perform_df

    def _calculate_total_perfomance_for_all_assets(self) -> pd.DataFrame:
        """
        Calculate total perfomance for all assets.
        :return: Dataframe with total perfomance for each asset.
        """
        total_perform_df = pd.DataFrame()

        for column in self._prices.columns:
            total_perform_df[column] = self.__count_total_perfomance_for_asset(column)
        total_perform_df.index = self.__get_new_index(self._prices).index[1:]

        return total_perform_df

    def _prepare_weights_df(self) -> pd.DataFrame:
        """
        "Weights" dataframe also has "weekday" index range. Change it to "daily"
        :return: Weights dataframe with "daily" index range
        """
        self.__new_weights = self.__get_new_index(self._weights)
        self.__new_weights.fillna(method='ffill', inplace=True)
        self.__new_weights.fillna(method='bfill',
                                  inplace=True)

        return self.__new_weights.iloc[:-1]


class PerfomancesWithWeights(AssetPerfomances):
    """
    Calculate price, currency and total perfomances for each asset according their asset weights.
    All function with used in next calculations data  have "protected" visible.
    """

    def __init__(self) -> None:
        """
        Get calculated perfomances and "weights" dataframe from inheritable class.
        """
        super().__init__()
        self.__rt = super()._calculate_price_perfomance_for_all_assets()
        self.__crt = super()._calculate_currency_perfomance_for_all_assets()
        self.__trt = super()._calculate_total_perfomance_for_all_assets()
        self.__weights = super()._prepare_weights_df()

    def _calculate_price_perfomance_according_on_weights(self) -> pd.Series:
        """
        Calculate price perfomance for all assets according on their weights.
        :return: Series with price perfomance for each time t.
        """
        self.__rt_with_weights = self.__rt * self.__weights
        price_perform_for_each_t = [sum(self.__rt_with_weights.iloc[i].values) for i in
                                    range(len(self.__rt_with_weights))]

        return pd.Series(price_perform_for_each_t, index=self.__rt_with_weights.index)

    def _calculate_currency_perfomance_according_on_weights(self) -> pd.Series:
        """
        Calculate currency perfomance for all assets according on their weights.
        :return: Series with currency perfomance for each time t.
        """
        self.__crt_with_weights = self.__crt * self.__weights
        currency_perform_for_each_t = [sum(self.__crt_with_weights.iloc[i].values) for i in
                                       range(len(self.__crt_with_weights))]

        return pd.Series(currency_perform_for_each_t, index=self.__crt_with_weights.index)

    def _calculate_total_perfomance_according_on_weights(self) -> pd.Series:
        """
        Calculate total perfomance for all assets according on their weights.
        :return: Series with total perfomance for each time t.
        """
        self.__trt_with_weights = self.__trt * self.__weights
        total_perform_for_each_t = [sum(self.__trt_with_weights.iloc[i].values) for i in
                                    range(len(self.__trt_with_weights))]

        return pd.Series(total_perform_for_each_t, index=self.__trt_with_weights.index)


class TotalPerfomance(PerfomancesWithWeights):
    """
    Calculate asset, currency and total perfomances.
    All supporting functions have "private" visible.
    All function with perfomance calculations data have "public" visible.
    """

    def __init__(self) -> None:
        """
        Get calculated perfomances from inheritable class. Set default perfomance value at day 0.
        """
        super().__init__()
        self.__res_t = super()._calculate_price_perfomance_according_on_weights()
        self.__currency_res_t = super()._calculate_currency_perfomance_according_on_weights()
        self.__total_res_t = super()._calculate_total_perfomance_according_on_weights()
        self.__P = 1
        self.__CP = 1
        self.__TP = 1

    @staticmethod
    def __get_index_of_start_date_element(column: pd.Series, start_date: str) -> int:
        """
        Get int index from Series with the following start_date.
        :param column: Selected Series.
        :param start_date: Converted to str datetime parameter.
        :return: int index of start_date.
        """
        return column.index.get_loc(start_date)

    @staticmethod
    def __get_index_of_end_date_element(column: pd.Series, end_date: str) -> int:
        """
        Get int index from Series with the following end_date.
        :param column: Selected Series.
        :param end_date: Converted to str datetime parameter.
        :return: int index of end_date.
        """
        return column.index.get_loc(end_date)

    def calculate_asset_performance(self, start_date: str, end_date: str) -> pd.Series:
        """
        Calculate asset perfomance from start_date to end_date.
        :param start_date: 1st parameter. Has converted to str datetime type.
        :param end_date: 2nd parameter. Has converted to str datetime type.
        :return: Series with asset perfomance.
        """
        asset_performance = [1]
        start = self.__get_index_of_start_date_element(self.__res_t, start_date)
        end = self.__get_index_of_end_date_element(self.__res_t, end_date)
        for i in range(start + 1, end + 1):
            as_perform = asset_performance[-1] * (1 + self.__res_t.iloc[i])
            asset_performance.append(as_perform)
        overall_asset = pd.Series(asset_performance, index=self.__res_t.loc[start_date:end_date].index)

        return overall_asset

    def calculate_currency_performance(self, start_date: str, end_date: str) -> pd.Series:
        """
        Calculate currency perfomance from start_date to end_date.
        :param start_date: 1st parameter. Has converted to str datetime type.
        :param end_date: 2nd parameter. Has converted to str datetime type.
        :return: Series with currency perfomance.
        """
        currency_performance = [self.__CP]
        start = self.__get_index_of_start_date_element(self.__currency_res_t, start_date)
        end = self.__get_index_of_end_date_element(self.__currency_res_t, end_date)
        for i in range(start + 1, end + 1):
            currency_performance.append(currency_performance[-1] * (1 + self.__currency_res_t.iloc[i]))
        overall_currency = pd.Series(currency_performance, index=self.__currency_res_t.loc[start_date:end_date].index)

        return overall_currency

    def calculate_total_performance(self, start_date: str, end_date: str) -> pd.Series:
        """
        Calculate total perfomance from start_date to end_date.
        :param start_date: 1st parameter. Has converted to str datetime type.
        :param end_date: 2nd parameter. Has converted to str datetime type.
        :return: Series with total perfomance.
        """
        total_performance = [self.__TP]
        start = self.__get_index_of_start_date_element(self.__total_res_t, start_date)
        end = self.__get_index_of_end_date_element(self.__total_res_t, end_date)
        for i in range(start + 1, end + 1):
            total_performance.append(total_performance[-1] * (1 + self.__total_res_t.iloc[i]))
        overall_total_perform = pd.Series(total_performance, index=self.__total_res_t.loc[start_date:end_date].index)

        return overall_total_perform

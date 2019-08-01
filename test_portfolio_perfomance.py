import unittest
import portfolio_perfomance


class TotalPerfomanceTest(unittest.TestCase):

    def test_calculate_asset_performance(self):
        count_perfomance = portfolio_perfomance.TotalPerfomance()
        asset_result1 = count_perfomance.calculate_asset_performance('2014-01-18', '2014-02-09')
        self.assertIn('2014-01-25', asset_result1.index)
        self.assertNotIn('2014-02-10', asset_result1.index)
        self.assertGreater('2014-02-09', '2014-01-18')
        self.assertEqual(asset_result1.iloc[4], 0.9890729316993252)

        with self.assertRaises(KeyError):
            count_perfomance.calculate_asset_performance('2014-01-12', '2014-02-09')

        with self.assertRaises(ValueError):
            count_perfomance.calculate_asset_performance('2014-04-11', '2014-03-09')

    def test_calculate_currency_performance(self):
        count_perfomance = portfolio_perfomance.TotalPerfomance()
        currency_result = count_perfomance.calculate_currency_performance('2014-01-25', '2014-04-15')
        self.assertIn('2014-03-12', currency_result.index)
        self.assertNotIn('2014-08-16', currency_result.index)
        self.assertEqual(currency_result.iloc[65], 1.0198146254833957)
        self.assertGreater('2014-04-15', '2014-01-25')

        with self.assertRaises(KeyError):
            count_perfomance.calculate_currency_performance('2017-01-12', '2020-02-09')

        with self.assertRaises(ValueError):
            count_perfomance.calculate_currency_performance('2017-03-11', '2017-03-09')

    def test_calculate_total_performance(self):
        count_perfomance = portfolio_perfomance.TotalPerfomance()
        total_result = count_perfomance.calculate_total_performance('2014-05-29', '2014-07-21')
        self.assertIn('2014-06-13', total_result.index)
        self.assertNotIn('2014-05-28', total_result.index)
        self.assertEqual(total_result.iloc[12], 1.0101079429736806)
        self.assertGreater('2014-07-21', '2014-05-29')

        with self.assertRaises(KeyError):
            count_perfomance.calculate_total_performance('2012-01-12', '2019-02-09')

        with self.assertRaises(ValueError):
            count_perfomance.calculate_total_performance('2017-03-10', '2017-03-09')


if __name__ == '__main__':
    unittest.main()

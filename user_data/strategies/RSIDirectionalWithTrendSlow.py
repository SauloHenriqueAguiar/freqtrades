from freqtrade.strategy import IStrategy, merge_informative_pair
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.exchange import timeframe_to_minutes
import numpy  # noqa


class RSIDirectionalWithTrendSlow(IStrategy):

   

    # Prazo ideal para a estratégia
    timeframe = '5m'

    # ROI mínimo projetado para a estratégia.
    # Este atributo será substituído se o arquivo de configuração contiver "minimal_roi"

    timeframe_mins = timeframe_to_minutes(timeframe)
    minimal_roi = {
        "0": 0.08,                       # 5% para as primeiras 3 candles
        str(timeframe_mins * 12): 0.04,  # 2% após 3 candles
        str(timeframe_mins * 24): 0.02,  # 1% Após 6 candles
     }

    # Este atributo será substituído se o arquivo de configuração contiver "stoploss"
    stoploss = -0.2

    # trailing stoploss
    trailing_stop = True

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe['rsi_slow'] = ta.RSI(dataframe, timeperiod=10)
        dataframe['ema600'] = ta.EMA(dataframe, timeperiod=600)

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
               # RSI cruza acima de 25
                (qtpylib.crossed_above(dataframe['rsi_slow'], 25)) &
                (dataframe['low'] > dataframe['ema600']) &  # # candle baixa está acima da EMA
                # Certifique-se de que esta candle tenha volume (importante para backtesting)
                (dataframe['volume'] > 0)
            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:

        dataframe.loc[
            (
                # RSI cruza acima de 20
                (qtpylib.crossed_below(dataframe['rsi_slow'], 20)) |
                 # OR o preço está abaixo da tendência ema
                (dataframe['low'] < dataframe['ema600'])
            ),
            'sell'] = 1
        return dataframe
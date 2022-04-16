# --- Do not remove these libs ---
from freqtrade.strategy.interface import IStrategy
from pandas import DataFrame
import talib.abstract as ta


# --------------------------------


class ADXMomentum(IStrategy):
  

    # ROI mínimo projetado para a estratégia.
    # ajustar com base nas condições de mercado. Recomendamos mantê-lo baixo para reviravoltas rápidas
    # Este atributo será substituído se o arquivo de configuração contiver "minimal_roi"
    minimal_roi = {
        "0": 0.01
    }

    # Stoploss ideal projetado para a estratégia
    stoploss = -0.25

    # Prazo ideal para a estratégia
    timeframe = '5m'

    # Número de velas que a estratégia requer antes de produzir sinais válidos
    startup_candle_count: int = 20

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe['adx'] = ta.ADX(dataframe, timeperiod=14) #(Índice Direcional Médio)indicador de tendencia se mercado está em alta ou baixa
        dataframe['di +'] = ta.PLUS_DI(dataframe, timeperiod=25) #Positive Directional Indicator(Quando a linha de crescimento do DI+ fica acima da linha do DI-, a indicação é de alta, podendo ser considerado como um sinal para comprar ações)
        dataframe['di -'] = ta.MINUS_DI(dataframe, timeperiod=25) #Negative Directional Indicator(Quando a linha de crescimento do DI- fica acima da linha do DI+, a indicação é de baixa, podendo ser considerado como um sinal para vender ações)
        dataframe['sar'] = ta.SAR(dataframe)#Stop and Reverse "Parada e Reversão", ou seja, o indicador pode determinar a tendência e, além disso, sinalizar a hora de fechar a operação em cima dessa tendência e olhar na direção oposta)
        dataframe['mom'] = ta.MOM(dataframe, timeperiod=14) #mede o quanto o preço de uma ação mudou durante um certo período de tempo. Momento = Preço de Fechamento hoje - Preço de Fechamento n dias atrás.indicador da velocidade do mercado.

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['adx'] > 25) &
                    (dataframe['mom'] > 0) &
                    (dataframe['di +'] > 25) &
                    (dataframe['di +'] > dataframe['di -'])

            ),
            'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[
            (
                    (dataframe['adx'] > 25) &
                    (dataframe['mom'] < 0) &
                    (dataframe['di -'] > 25) &
                    (dataframe['di +'] < dataframe['di -'])

            ),
            'sell'] = 1
        return dataframe
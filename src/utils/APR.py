import numpy as np
import pandas as pd
import math

# Prices must be sorted
def APR(prices, n):
    return math.log(prices[0] / prices[n]) * 365/n if n>0 else 0

def APR_SMA(prices, n, k):
    sum_APR = 0
    for i in range(k):
        sum_APR += APR(prices[i:], n)
    return sum_APR / k

def APR_SMA_table(prices, N, K):
    table = np.zeros((N, K))
    for n in range(1, N+1):  # n values from 1 to N
        for k in range(1, K+1):  # k values from 1 to K
            if k <= len(prices) - n + 1:  # Ensure we have enough data
                table[n-1, k-1] = APR_SMA(prices, n, k)
    
    # Create DataFrame with proper index and column labels
    return pd.DataFrame(
        table, 
        index=[f'n={i}' for i in range(1, N+1)],
        columns=[f'k={j}' for j in range(1, K+1)]
    ).apply(lambda x: x*100).round(2)  # Multiply by 100 and round to 2 decimal places

if __name__ == '__main__':
    prices = [1.0536842953168815, 1.0601862496275964, 1.0592805020788363, 1.0587321977313833, 1.057816966791741, 1.0573708928245351, 1.0568227681142341, 1.0577502222209032, 1.0567088356430845, 1.0549408065123758, 1.0537705736628373, 1.0507466684680826, 1.0484231961061876, 1.0476904338955648, 1.0439948911065882, 1.0421244501987224, 1.0398847657795487, 1.0390391150893459, 1.0387376530056465, 1.0386217955184147, 1.0385919378326025, 1.0379250176330315, 1.0378716221997337, 1.037798259354703, 1.037738265156076, 1.0377313107894732, 1.0377250732771326, 1.0377216979082888, 1.037689086987993, 1.0375883810372715, 1.0375412263750639, 1.0374494400454901, 1.0373965619580128, 1.037360263014198, 1.0372525706042306, 1.0371402874999724, 1.0370974841858507, 1.036967132821046, 1.036852207377033, 1.0367669861091304, 1.0367532452349961, 1.0367523282907942, 1.036634182168544, 1.0365947193713139, 1.0365704360061725, 1.0365523091161357, 1.0365259987568136, 1.0365200220521957, 1.0365194532587447, 1.036180980669682, 1.0361404261231681, 1.0361218155105831, 1.0360884918523658, 1.036043860418367]
    print(APR(prices, 7))
    print(APR_SMA(prices, 7, 4))

    df = APR_SMA_table(prices, 30, 15)
    
    print(df)
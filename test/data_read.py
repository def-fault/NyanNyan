import pandas as pd
from tabulate import tabulate
from wcwidth import wcswidth

from table2ascii import table2ascii as t2a, PresetStyle


df1 = pd.read_excel('data.xlsx', sheet_name = 'Growth') # 성장의 비약
df2 = pd.read_excel('data.xlsx', sheet_name = 'Point') # EXP쿠폰
df3 = pd.read_excel('data.xlsx', sheet_name = 'Extreme') # 익스트림 몬스터파크
df6 = pd.read_excel('data.xlsx', sheet_name = 'Hexa') # 6차전직표

def swap_variables(a, b):
    a, b = b, a  # 변수 a와 b의 값을 스왑

def EXPcal(startlevel, endlevel=0):

    if endlevel == 0:
        value = df2.at[startlevel-200, 'EXPPoint']
        return value

    # 끝 레벨이 더 작을 경우
    if (startlevel < endlevel):
        swap_variables(startlevel, endlevel)

    i = j = 0
    start = startlevel-200
    end = endlevel-200
    sum1 = sum2 = 0

    while i < start:
        value = df2.at[i, 'EXPPoint']
        sum1 += value
        i += 1

    while j < end:
        value = df2.at[j, 'EXPPoint']
        sum2 += value
        j += 1

    return sum2 - sum1


def EXPPotion(level):
    if level < 200:
        return 0
    value = df1.at[level-200, 'Percent']
    return round(value*100, 3)

def Extreme(level):
    if level < 260:
        return 0

    value1 = df3.at[level-260, 'Percent']
    return round(value1, 3)


def Hexa(startlevel, endlevel=0):
    if startlevel < 1 :
        return 0, 0, 0, 0, 0, 0
    if startlevel > 29:
        return 0, 0, 0, 0, 0, 0

    if endlevel == 0:
        Sol6 = df6.at[startlevel-1, 'SixSol']
        Sol5 = df6.at[startlevel-1, 'FiveSol']
        Sol4 = df6.at[startlevel-1, 'FourSol']
        Piece6 = df6.at[startlevel-1, 'SixPiece']
        Piece5 = df6.at[startlevel-1, 'FivePiece']
        Piece4 = df6.at[startlevel-1, 'FourPiece']

        return Sol6, Piece6, Sol5, Piece5, Sol4, Piece4

    # 끝 레벨이 더 작을 경우
    if (startlevel < endlevel):
        swap_variables(startlevel, endlevel)


    start = startlevel-1
    end = endlevel-1

    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'SixSol']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'SixSol']
        sum2 += value
        j += 1

    Sol6 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'SixPiece']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'SixPiece']
        sum2 += value
        j += 1

    Piece6 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'FiveSol']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'FiveSol']
        sum2 += value
        j += 1

    Sol5 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'FivePiece']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'FivePiece']
        sum2 += value
        j += 1

    Piece5 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'FourSol']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'FourSol']
        sum2 += value
        j += 1

    Sol4 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    while i < start:
        value = df6.at[i, 'FourPiece']
        sum1 += value
        i += 1

    while j < end:
        value = df6.at[j, 'FourPiece']
        sum2 += value
        j += 1

    Piece4 = sum2 - sum1
    i = j = 0
    sum1 = sum2 = 0

    return Sol6, Piece6, Sol5, Piece5, Sol4, Piece4

Sol6, Piece6, Sol5, Piece5, Sol4, Piece4 = Hexa(5)
d = [ ["오리진(6차)",Sol6,Piece6], ["강화(5차)",Sol5,Piece5], ["마스터리(4차)",Sol4,Piece4]]
df = pd.DataFrame(d, columns= ['Kind','Sol Erda','Sol Piece'])

output = t2a(
    header=list(df.columns),
    body=[df.iloc[0].values.tolist(),df.iloc[1].values.tolist(),df.iloc[2].values.tolist()],
    first_col_heading=True
)
print(f'\n{output}\n')




'''
print(str(level) + "레벨에서 익몬을 뛰었을 때 오르는 경험치량 : " + str(Extreme(level)) + "%")
print("+ 선데이에 익몬을 뛰었을 때 오르는  경험치량 : " + str(Extreme(level)*1.5) + "%")
level = 200
print(str(level) + "레벨에서 극성비를 먹었을 때 오르는 경험치량 :" + str(EXPPotion(level)) + "%")

start_level = 200
print(str(start_level) + " : " + str(EXPcal(start_level)))

end_level = 218
print(str(start_level) + "레벨에서 " + str(end_level) + "레벨까지 필요한 EXP쿠폰 갯수 : " + str(EXPcal(start_level,end_level)))
'''
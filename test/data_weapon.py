import pandas as pd

df4 = pd.read_excel('data.xlsx', sheet_name = 'Option') # 추옵표

pd.set_option('display.float_format', '{:.0f}'.format)

  # 0부터 시작하는 인덱스이므로 3번째 행은 인덱스 2

target_name = '한손검'
result = df4[df4['Weapon'] == target_name]
selected_row = df4.iloc[result.index]
new_df = pd.DataFrame(selected_row)

print(new_df.to_string(index=False))

# 아 이게 데이터가 표 1개에 4개의 데이터가 들어간 게 아니라
# 표 4개에 1개씩 데이터가 들어간 거라서 정렬이 안되네

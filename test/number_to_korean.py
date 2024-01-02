def number_to_korean(num):
    units = ['', '만', '억', '조', '경']
    result = ''

    for i in range(len(units)):
        current_num = num % 10000
        if current_num != 0:
            result = str(current_num) + units[i] + result
        num //= 10000

    return result

input_number = 4932203389
korean_representation = number_to_korean(input_number)

print(korean_representation)
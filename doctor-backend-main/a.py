from difflib import SequenceMatcher

def calculate_similarity(str1, str2):
    return SequenceMatcher(None, str1, str2).ratio()

str1 = "示例地址"
str2 = "示例地址"
str3 = "示例地址"

similarity = calculate_similarity(str1, str2)
similarity2 = calculate_similarity(str1, str3)
print(f"相似度: {similarity:.2f}")
print(f"相似度: {similarity2:.2f}")

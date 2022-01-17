"""
3. Задание на закрепление знаний по модулю yaml.
 Написать скрипт, автоматизирующий сохранение данных
 в файле YAML-формата.
Для этого:

Подготовить данные для записи в виде словаря, в котором
первому ключу соответствует список, второму — целое число,
третьему — вложенный словарь, где значение каждого ключа —
это целое число с юникод-символом, отсутствующим в кодировке
ASCII(например, €);

Реализовать сохранение данных в файл формата YAML — например,
в файл file.yaml. При этом обеспечить стилизацию файла с помощью
параметра default_flow_style, а также установить возможность работы
с юникодом: allow_unicode = True;

Реализовать считывание данных из созданного файла и проверить,
совпадают ли они с исходными.
"""
import yaml
INP_DATA = {
    'key1': ['value1','value2','value3'],
    'key2': 3,
    'key3': { '1\u20ac':'евро','2\u20bd':'рубль'}
}
OUT_DATA = {}
with open('file.yaml', 'w', encoding='utf-8') as f_n:
    yaml.dump(INP_DATA, f_n, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open("file.yaml", 'r', encoding='utf-8') as f_o:
    OUT_DATA = yaml.load(f_o,Loader=yaml.SafeLoader)

print(INP_DATA == OUT_DATA)
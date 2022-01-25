"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import csv
import re



def get_data(filename):
    with open(filename,encoding='utf-8') as f_n:
        for line in f_n:
            my_list = line.split(':')
            if(my_list[0] in dictionary.keys()):
                my_list[1] = re.sub(r'^\s+','',my_list[1])
                my_list[1] = re.sub(r'\s+$', '', my_list[1])
                dictionary[my_list[0]].append(my_list[1])

def write_to_csv(filename):
    FILES = ['info_1.txt','info_2.txt','info_3.txt']
    main_data = []
    for file in FILES:
       get_data(file)
    main_data.append(dictionary.keys())
    for i in range(1,4):
       main_data.append([])
    for i in range(1,4):
       for key in dictionary.keys():
          main_data[i].append(dictionary[key][i-1])
    with open(filename,'w',encoding='utf-8') as f_n:
     F_N_WRITER = csv.writer(f_n, quoting=csv.QUOTE_NONNUMERIC)
     for row in main_data:
       F_N_WRITER.writerow(row)

dictionary = {
 'Изготовитель ОС': [],
 'Название ОС': [],
 'Код продукта': [],
 'Тип системы': []
}
write_to_csv('main_data.csv')
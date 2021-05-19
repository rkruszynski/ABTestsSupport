from selenium import webdriver
from time import sleep
import pyperclip
import PySimpleGUI as sg
import csv
from selenium.webdriver.common.action_chains import ActionChains
import datetime
from selenium.common.exceptions import NoSuchElementException, InvalidArgumentException

driver = webdriver.Chrome('C:/Users/rysza/Documents/chromedriver.exe')

is_log_written = False
logfile_name = ''

layout = [
    [sg.FileBrowse("Browse", file_types=(("csv", "*.csv"), ("txt", "*.txt")), key='csv', enable_events=True)],
    [sg.Button("Preview", key='-open preview-')],
    [sg.Button('Previous'), sg.Button('Next'), sg.Button('+10'), sg.Button('+100'), sg.Button('+1000'), sg.Button('Take screenshot')],
    [sg.Text(size=(40,1), key='refid'), sg.Button('Copy value', key='Copy value')],
    [sg.Text('Your xpath go here:')],
    [sg.InputText(key='-xpath-')],
    [sg.Button('Scroll'), sg.Text(size=(33, 1), key='-OUTPUT-')],
    [sg.Button('Save log'), sg.InputText(key='-log-')],
    [sg.Button('Quit')]
]


def file_preview(csv_file):
    # modal window for csv file preview
    modal_layout = [
        [sg.Text(size=(70, 10), key='-preview-')],
        [sg.CloseButton('Close')]
    ]

    modal_window = sg.Window("Preview", modal_layout, modal=True, finalize=True)
    while True:
        with open(csv_file, 'r') as csv_file_preview:
            # hardcoded: only first 10 rows
            csv_file_preview_head = [next(csv_file_preview) for line in range(10)]
            modal_window['-preview-'].update(csv_file_preview_head)
        modal_event, modal_values = modal_window.read()
        if modal_event == "Exit" or modal_event == sg.WIN_CLOSED:
            break
    modal_window.close()


sg.theme('DarkAmber')
window = sg.Window("Demo", layout, finalize=True)

while True:
    event, values = window.read()

    if event == "Quit" or event == sg.WIN_CLOSED:
        driver.quit()
        window.close()
        break

    if event in ('+10', '+100', '+1000'):
        power = ['+10', '+100', '+1000'].index(event) + 1
        if url_index + 10**power > len(url_list):
            sg.popup_error("Index would be out of range!")
        else:
            url_index += 10**power

    if event == 'Next':
        try:
            window['refid'].update(refid_list[url_index])
            driver.get(url_list[url_index])
            url_index += 1
        except NameError:
            sg.popup_error("CSV file is not loaded")
        except InvalidArgumentException:
            sg.popup_error('"{}" is not a valid page'.format(url_list[url_index]))

    if event == 'Previous':
        try:
            window['refid'].update(refid_list[url_index])
            driver.get(url_list[url_index])
            url_index -= 1
        except NameError:
            sg.popup_error("CSV file is not loaded")
        except InvalidArgumentException:
            sg.popup_error('"{}" is not a valid page'.format(url_list[url_index]))

    if event == 'Copy value':
        pyperclip.copy(window['refid'].get())

    if event == 'Scroll':
        xpath = values['-xpath-']
        try:
            element = driver.find_element_by_xpath(xpath)
            actions = ActionChains(driver)
            actions.move_to_element(element).perform()
            window['-OUTPUT-'].update("Done")
        except NoSuchElementException:
            window['-OUTPUT-'].update("Couldn't find this element")

    if event == 'Take screenshot':
        today = datetime.date.today()
        today = today.strftime("%Y-%m-%d")
        driver.save_screenshot("screenshot{page}_{date}.png".format(page='j', date=today))

    if event == 'Save log':
        if not is_log_written:
            is_log_written = True
            today = datetime.datetime.now().strftime("%d-%m-%Y %H-%M-%S")
            logfile_name = "log_{page}_{date}.txt".format(page='j', date=today)
        with open(logfile_name, 'a') as logfile:
            logfile.write(driver.current_url + ', "' + values['-log-'] + '"\n')

    if event == '-open preview-':
        try:
            file_preview(values['csv'])
        except FileNotFoundError:
            sg.popup_error("CSV file is not loaded")

    if event == 'csv':
        with open(values['csv'], 'r') as f:
            reader = csv.reader(f)
            refid_list = []
            url_list = []
            for column in reader:
                refid_list.append(column[0])
                url_list.append(column[1])
            url_index = 0

import logging
import hwinfo
import requests
import json

from aiogram import Bot, Dispatcher, executor, types


def printLogo():
    print("  __      __                      ")
    print(" / /____ / /__ ___ ________ ___ _ ")
    print("/ __/ -_) / -_) _ `/ __/ _ `/  ' \\")
    print("\\__/\\__/_/\\__/\\_, /_/  \\_,_/_/_/_/")
    print("             /___/                ")
    print("     __               __        __        __ ")
    print(" ___/ /__  ___  ___ _/ /____   / /  ___  / /_")
    print("/ _  / _ \\/ _ \\/ _ `/ __/ -_) / _ \\/ _ \\/ __/")
    print("\\_,_/\\___/_//_/\\_,_/\\__/\\__/ /_.__/\\___/\\__/ ")
    print("                                             ")
    print("\n")


hwinfo.tools.clearConsole()
printLogo()
print('Starting...')


def percentStyleConfigurator():
    hwinfo.tools.clearConsole()
    printLogo()
    while True:
        style = input('Выберите стиль прогресса сбора.\n\n'
                      '1. Windows 95 (█░░░░)\n'
                      '2. Modern (▰▱▱▱▱)\n'
                      'Выбор (1): ').strip()

        if style not in ('1', '2'):
            if style == '':
                style = '1'
                break
            print('Пожалуйста, выберите между 1 и 2\n')
        else:
            break
    return style


def configurator():
    hwinfo.tools.clearConsole()
    printLogo()

    Token = input('Пожалуйста, введите токен бота: ').strip()
    hwinfo.tools.clearConsole()
    printLogo()

    Link = input('Пожалуйста, введите ссылку на сбор: ').strip()
    hwinfo.tools.clearConsole()
    printLogo()

    Text = input('Пожалуйста, введите текст для кнопки: ').strip()
    hwinfo.tools.clearConsole()
    printLogo()

    style = percentStyleConfigurator()
    hwinfo.tools.clearConsole()
    printLogo()

    print('Подождите, идет настройка...')

    with open('config.json', 'w') as file:
        json.dump({'botToken': Token,
                   'donationLink': Link,
                   'buttonText': Text,
                   'progressBar': style}, file, indent=4)

    print('Настройка завершена. Пожалуйста, перезагрузите скрипт.')
    exit(0)


try:
    with open('config.json', 'r') as f:
        config = json.loads(f.read())

    botToken = config['botToken']
    donationLink = config['donationLink']
    buttonText = config['buttonText']
    progress_style = config['progressBar']
except (KeyError, FileNotFoundError, json.decoder.JSONDecodeError):
    configurator()
    botToken = 'pep8 иди нахуй'

logging.basicConfig(level=logging.INFO, filename='aiogram_logs')

bot = Bot(token=botToken)

dp = Dispatcher(bot)


def organizer(req: str):
    for line in req.splitlines():
        if 'organizerName' in line:
            return line.split(
                'organizerName'
            )[1].split(''
                       '"CrowdPage">'
                       )[1].split(
                '</span>')[0]

        else:
            continue
    else:
        return None


def description(req: str):
    for line in req.splitlines():
        if 'CollectMoneyPayForm__description' in line:
            return line.split(
                'CollectMoneyPayForm__description'
            )[1].split(
                '"CollectMoneyPayForm">'
            )[1].split('</span>')[0]
        else:
            continue
    else:
        return None


def name(req: str):
    for line in req.splitlines():
        if '<meta property="og:title" content="' in line:
            return line.split(
                '<meta property="og:title" content="'
            )[1].split('"')[0]
        else:
            continue
    else:
        return None


def remains(tar, coll):
    try:
        return int(int(tar) - int(coll))
    except TypeError:
        return None


def target(req: str):
    for line in req.splitlines():
        if '<span class="CollectionInfoHeader__goal' in line:
            temp_target = line.split(
                '<span class="CollectionInfoHeader__goal'
            )[1].split(
                '"CollectionInfoHeader">Цель: '
            )[1].split(' ₽</span>')[0]
            temp = str()

            for symbol in temp_target:
                if symbol in '1234567890,.':
                    temp += symbol

            return int(float(temp.replace(',', '.')))
        else:
            continue
    else:
        return None


def collected(req: str):
    for line in req.splitlines():
        if 'class="CollectionInfoHeader__percents' in line:
            temp_collected = line.split(
                '"CollectionInfoHeader">Собрано: '
            )[1].split(' ₽</span>')[0]

            temp = str()

            for symbol in temp_collected:
                if symbol in '1234567890,.':
                    temp += symbol

            return int(float(temp.replace(',', '.')))
        else:
            continue
    else:
        return None


def progressPercentage(collect, targ):
    try:
        return round(collect / targ * 100)
    except TypeError:
        return None


def progressBar(progressPercent):
    try:
        if progress_style == '1':
            progressBar_icon_empty = '░'
            progressBar_icon_full = '█'
            progressBar_container = None
        elif progress_style == '2':
            progressBar_icon_empty = '▱'
            progressBar_icon_full = '▰'
            progressBar_container = '[]'
        else:
            progressBar_icon_empty = '-'
            progressBar_icon_full = '#'
            progressBar_container = '[]'
        if progressPercent >= 100:
            return progressBar_icon_full * 20
        else:
            collect = (round(progressPercent / 5)) * progressBar_icon_full
            residual = (20 - len(collect)) * progressBar_icon_empty
            if progressBar_container is not None:
                return "{}{}".format(collect,
                                     residual).join(
                                         progressBar_container
                                     )
            else:
                return collect + residual
    except TypeError as e:
        print(e)
        return None


@dp.message_handler(content_types=['text'])
async def text_handler(message: types.Message):
    inline_kb_full = types.InlineKeyboardMarkup(row_width=1)
    inline_kb_full.add(
        types.InlineKeyboardButton(buttonText, url=donationLink))

    tempMessage = await message.reply('<i>Загрузка...</i>', parse_mode='html')

    request = requests.get(donationLink).text

    donationName = name(request)
    donationOrganizer = organizer(request)
    donationDescription = description(request)
    donationTarget = target(request)
    donationCollected = collected(request)
    donationProgressPercentage = progressPercentage(donationCollected,
                                                    donationTarget)
    donationProgressBar = progressBar(donationProgressPercentage)
    donationRemains = remains(donationTarget, donationCollected)

    message = str()

    if donationName is not None:
        message += f'<b>{donationName}</b>\n\n'

    if donationOrganizer is not None:
        message += f'<b>Организатор сбора:</b> <i>{donationOrganizer}</i>\n'

    if donationTarget is not None:
        message += f'<b>Цель:</b> <i>{donationTarget} ₽</i>\n'

    if donationCollected is not None:
        message += f'<b>Собрано:</b> <i>{donationCollected} ₽</i>\n'

    if donationRemains is not None:
        message += f'<b>Осталось:</b> <i>{donationRemains} ₽</i>\n\n'

    if donationProgressBar is not None and donationProgressPercentage is not None:  # noqa
        message += f'<b>Прогресс:</b>\n<b>{donationProgressBar}</b> {donationProgressPercentage} %\n\n'  # noqa

    if donationDescription is not None:
        message += f'<b>Описание:</b>\n<i>{donationDescription}</i>'

    return await tempMessage.edit_text(message, parse_mode='html',
                                       reply_markup=inline_kb_full)


if __name__ == '__main__':
    print('Started!')
    executor.start_polling(dp, skip_updates=True)

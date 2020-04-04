import logging
import hwinfo
import requests
import json

from aiogram import Bot, Dispatcher, executor, types

print('Starting...')


def configurator():
    hwinfo.tools.clearConsole()

    Token = input('Пожалуйста, введите токен бота: ')
    hwinfo.tools.clearConsole()

    Link = input('Пожалуйста, введите ссылку на сбор: ')
    hwinfo.tools.clearConsole()

    Text = input('Пожалуйста, введите текст для кнопки: ')
    hwinfo.tools.clearConsole()

    print('Подождите, идет настройка...')

    with open('config.json', 'w') as file:
        json.dump({'botToken': Token,
                   'donationLink': Link,
                   'buttonText': Text}, file, indent=4)

    print('Настройка завершена. Пожалуйста, перезагрузите скрипт.')


try:
    with open('config.json', 'r') as f:
        config = json.loads(f.read())

    botToken = config['botToken']
    donationLink = config['donationLink']
    buttonText = config['buttonText']
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
                if symbol in '1234567890.':
                    temp += symbol

            return int(temp)
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
                if symbol in '1234567890.':
                    temp += symbol

            return int(temp)
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
        if progressPercent >= 100:
            return '████████████████████'
        else:
            collect = (round(progressPercent / 5)) * '█'
            residual = (20 - len(collect)) * '░'
            return collect + residual
    except TypeError:
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
    donationProgressPercentage = progressPercentage(donationCollected, donationTarget)
    donationProgressBar = progressBar(donationProgressPercentage)

    message = str()

    if donationName is not None:
        message += f'<b>{donationName}</b>\n\n'

    if donationOrganizer is not None:
        message += f'<b>Организатор сбора:</b> <i>{donationOrganizer}</i>\n'

    if donationTarget is not None:
        message += f'<b>Цель:</b> <i>{donationTarget}₽</i>\n'

    if donationCollected is not None:
        message += f'<b>Собрано:</b> <i>{donationCollected}₽</i>\n\n'

    if donationProgressBar is not None and donationProgressPercentage is not None:
        message += f'<b>Прогресс:</b>\n<b>{donationProgressBar}</b> {donationProgressPercentage}%\n\n'

    if donationDescription is not None:
        message += f'<b>Описание:</b>\n<i>{donationDescription}</i>'

    return await tempMessage.edit_text(message, parse_mode='html', reply_markup=inline_kb_full)


if __name__ == '__main__':
    hwinfo.tools.clearConsole()
    print('Started!')
    executor.start_polling(dp, skip_updates=True)

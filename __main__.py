import sys  # noqa
if sys.version_info < (3, 8, 0):
    print("Ваша версия Python ниже минимально-поддерживаемой(3.8.0)")
    exit(1)
def printHelp():
    return print("Usage: python3 __main__.py (--no-logo) (--not-clear)"
                 " (--kek) (--minimize) (--help/-h)")
if "--help" in sys.argv or "-h" in sys.argv:
    printHelp()
    exit()

print("Loading...")
from time import sleep  # noqa
sleep(0.2)
import logging  # noqa
import requests  # noqa
import json  # noqa

print("Preparing modules resolver...")
from modules.moduleResolver import ModuleResolver  # noqa
print("Modules resolver loaded.")
print("Preparing hwinfo...")
import hwinfo  # noqa
print("hwinfo loaded.")
print("Preparing to start...")

from aiogram import Bot, Dispatcher, executor, types  # noqa

version = '1.7'


def print_logo():
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


if "--not-clear" not in sys.argv:
    hwinfo.tools.clearConsole()
if "--no-logo" not in sys.argv:
    print_logo()
if "--minimize" not in sys.argv:
    print('Starting Telegram Donate Bot v{}'.format(version))
else:
    print('Starting...')


def percent_style_configurator():
    hwinfo.tools.clearConsole()
    print_logo()
    while True:
        hwinfo.tools.clearConsole()
        print_logo()
        style = input('Выберите стиль прогресса сбора.\n\n'
                      '1. Windows 95 (█░░░░)\n'
                      '2. Modern (▰▱▱▱▱)\n'
                      'Выбор (1): ').strip()

        if style not in ('1', '2'):
            if style == '':
                style = '1'
                break
            continue
        else:
            break
    return style


def donate_module_configurator():
    hwinfo.tools.clearConsole()
    print_logo()
    donate_modules = ['Tinkoff']
    module_list = ""
    i = 0
    for module in donate_modules:
        i += 1
        module_list += "{}. {}\n".format(i, module)
    while True:
        hwinfo.tools.clearConsole()
        print_logo()
        module = input('Выберите модуль для приема донатов.\n\n'
                       f'{module_list}'
                       'Выбор (1): ').strip()

        try:
            int(module)
        except ValueError:
            if module == "":
                module = '1'
                break
            continue

        if int(module) not in (range(len(donate_modules) + 1)):
            continue
        else:
            break
    moduleSelected = int(module) - 1
    return donate_modules[moduleSelected].lower()


def configurator():
    while True:
        hwinfo.tools.clearConsole()
        print_logo()
        Token = input('Пожалуйста, введите токен бота: ').strip()
        if Token == "":
            continue
        else:
            break
    hwinfo.tools.clearConsole()
    print_logo()

    module = donate_module_configurator()

    while True:
        hwinfo.tools.clearConsole()
        print_logo()
        Link = input('Пожалуйста, введите ссылку на сбор: ').strip()
        if "http://" not in Link and "https://" not in Link:
            continue
        else:
            break

    while True:
        hwinfo.tools.clearConsole()
        print_logo()
        Text = input('Пожалуйста, введите текст для кнопки: ').strip()
        if Text == "":
            continue
        else:
            break
    hwinfo.tools.clearConsole()
    print_logo()

    style = percent_style_configurator()
    hwinfo.tools.clearConsole()
    print_logo()

    print('Подождите, идет настройка...')

    with open('config.json', 'w') as file:
        json.dump({'bot_token': Token,
                   'donation_link': Link,
                   'button_text': Text,
                   'progress_bar': style,
                   'using_module': module}, file, indent=4)
    sleep(0.5)

    print('Настройка завершена. Пожалуйста, перезагрузите скрипт.')
    exit(0)


if "--configurator" in sys.argv:
    configurator()


try:
    with open('config.json', 'r') as f:
        config = json.loads(f.read())

    bot_token = config['bot_token']
    donation_link = config['donation_link']
    button_text = config['button_text']
    progress_style = config.get('progress_bar')
    using_module = config.get('using_module')
    if not using_module or not progress_style:
        while True:
            update = input("WARNING! Ваш конфиг устарел. "
                           "Вы хотите обновить его? (y/N): ")
            if update.lower() in ('y', 'yes', 'да', 'д'):
                configurator()
                break
            else:
                print("Обновление не запущено. Будут использованы "
                      "нативные настройки.")
                if not using_module:
                    using_module = 'tinkoff'
                if not progress_style:
                    progress_style = '1'
                break
    resolve = ModuleResolver(using_module)
    if "--minimize" not in sys.argv:
        print('Using module \"{}\"'.format(using_module).title())
        print('Progress style: {}'.format(
            'Windows 95' if progress_style == '1' else "Modern" if progress_style == '2' else "Linux"  # noqa
        ))
except (KeyError, FileNotFoundError, json.decoder.JSONDecodeError):
    configurator()
    bot_token = 'pep8 иди нахуй'

logging.basicConfig(level=logging.INFO, filename='aiogram_logs.log')

bot = Bot(token=bot_token)

dp = Dispatcher(bot)


def remains(tar, coll):
    try:
        return int(int(tar) - int(coll))
    except TypeError:
        return None


def progress_percentage(collect, targ):
    try:
        return round(collect / targ * 100)
    except TypeError:
        return None


def progress_bar(progress_percent, progress_style):
    try:
        full_icons = {
            "1": "█",
            "2": "▰",
            "linux": "#"
        }
        empty_icons = {
            "1": "░",
            "2": "▱",
            "linux": "-"
        }
        containers = {
            "1": None,
            "2": "[]",
            "linux": "[]"
        }
        if progress_style not in ("1", "2"):
            progress_style = "linux"
        if progress_percent >= 100:
            return full_icons[progress_style] * 20
        else:
            collect = (round(progress_percent / 5)) * full_icons[progress_style]
            residual = (20 - len(collect)) * empty_icons[progress_style]
            if containers[progress_style] is not None:
                return "{}{}".format(collect,
                                     residual).join(
                                         containers[progress_style]
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
        types.InlineKeyboardButton(button_text, url=donation_link))

    temp_message = await message.reply('<i>Загрузка...</i>',
                                       parse_mode='html')

    try:
        request = requests.get(donation_link).text

        donation_name = resolve.name(request)
        donation_organizer = resolve.organizer(request)
        donation_description = resolve.description(request)
        donation_target = resolve.target(request)
        donation_collected = resolve.collected(request)
        donation_progress_percentage = progress_percentage(donation_collected,
                                                           donation_target)
        donation_progress_bar = progress_bar(donation_progress_percentage,
                                             progress_style)
        donation_remains = remains(donation_target, donation_collected)

        message = str()

        if donation_name is not None:
            message += f'<b>{donation_name}</b>\n\n'

        if donation_organizer is not None:
            message += f'<b>Организатор сбора:</b> <i>{donation_organizer}</i>\n'  # noqa

        if donation_target is not None:
            message += f'<b>Цель:</b> <i>{donation_target} ₽</i>\n'

        if donation_collected is not None:
            message += f'<b>Собрано:</b> <i>{donation_collected} ₽</i>\n'

        if donation_remains is not None:
            message += f'<b>Осталось:</b> <i>{donation_remains} ₽</i>\n\n'

        if donation_progress_bar is not None and donation_progress_percentage is not None:  # noqa
            message += f'<b>Прогресс:</b>\n<b>{donation_progress_bar}</b> {donation_progress_percentage} %\n\n'  # noqa

        if donation_description is not None:
            message += f'<b>Описание:</b>\n<i>{donation_description}</i>'

        return await temp_message.edit_text(message, parse_mode='html',
                                           reply_markup=inline_kb_full)
    except Exception as e:
        return await temp_message.edit_text(
            '<b>Произошла ошибка:</b> <code>{}</code>'.format(str(e)),
            parse_mode="html"
        )


if __name__ == '__main__':
    if '--kek' in sys.argv:
        print("""[Интро]
Sayonara boy
Sayonara boy

[Припев]
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы

[Куплет 1]
Бейбе, твои глаза, твои дреды
Люди вокруг нас — всего лишь скелеты
Я хочу тебя даже одетой
Быть такими-такими-такими как мы — под запретом
В твоем лофте, ты-ты-ты-ты в моей кофте
Фотки-фотки-фотки-фотки-фотки если мы на тусовке
Любимые кроссовки топчут с тобою вместе
Мы жуем мятную жовку под одну из моих песен

[Припев 2]
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
О-о-о-о-о, о-о-о!
О-о-о-о-о-очень рваные джинсы
О-о-о-о-о, о-о-о!

[Куплет 2]
Девочка — чупа-чупс, перегазировка чувств
Я торчу на тебе, ведь я этого хочу
И ты тоже (тоже, тоже)
Бегут мурашки по коже (коже, коже)
Глаза-стекляшки
В стакане газировка с ягодным сиропом
У нас передозировка, не звоните копам
В стакане газировка с ягодным сиропом
У нас передозировка, не звоните копам

[Припев 2]
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
Детка, ты любишь рваные джинсы
О-о-о-о-о-очень рваные джинсы
О-о-о-о-о, о-о-о!
О-о-о-о-о, очень рваные джинсы
О-о-о-о-о, о-о-о!

[Аутро]
Sayonara boy-boy-boy-boy-boy
Sayonara boy""")
    skip_updates = False
    if "--skip" in sys.argv:
        skip_updates = True
    print('Started!')
    executor.start_polling(dp, skip_updates=skip_updates)

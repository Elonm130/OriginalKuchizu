# DEV: @Kuchizu
import asyncio
import os
import requests

from pyrogram import Client, filters
from requests import get

os.chdir(os.path.dirname(os.path.abspath(__file__)))

logs_id = -1001440234388
database_id = -1001720941508
link = '🔗'
bread = '🥖'
edit_timeout = 0
api_id = '123123'
api_hash = '123asd123asd'
bot_token = '123123:AA123123BB123'

bot = Client("Cookie", bot_token=bot_token, api_id=api_id, api_hash=api_hash)


async def callback(curr, size, chat_id, message_id):
    try:
        global edit_timeout
        if edit_timeout < 30:
            edit_timeout += 1
            return
        edit_timeout = 0

        done = int(20 * curr / int(size))
        per = f'{curr * 100 / int(size):.1f}%  [{curr / 1024 / 1024:.1f} / {int(size) / 1024 / 1024:.1f} MB]'
        yet = '#' * done
        of = ' ' * (20 - done)
        await bot.edit_message_text(chat_id, message_id, 'Uploading... {}\n'
                                                         '[{}{}]'.format(per, yet, of))

    except Exception as e:
        print(repr(e))


@bot.on_message(filters.text & filters.private)
async def tfload(client, message):
    try:
        await bot.forward_messages(logs_id, message.chat.id, message.message_id)
        if '/start' in message.text.lower() or '/' not in message.text:
            await bot.send_message(message.chat.id, f"Send download link {link}")
            return

        url = message.text
        file_name = url.split("/")[-1]
        file_name = f'{file_name[:20]}...{file_name[-10:]}' if len(file_name) > 50 else file_name
        response = get(url, stream=True)
        size = response.headers.get('content-length')
        load = await bot.send_message(message.chat.id, 'Downloading...')

        if response.status_code != 200 or not size:
            await bot.send_message(message.chat.id, f'Unable to obtain file size of {url}')
            return
        if int(size) / 1024 / 1024 > 1910:
            await bot.send_message(message.chat.id, f'Unable to send file more than 1900MB.')
            return

        with open(file_name, 'wb') as f:
            ded, x = 0, 0
            for chunk in response.iter_content(4096):
                f.write(chunk)
                ded += len(chunk)
                x += 1
                if x % 5000 == 0:
                    done = int(20 * ded / int(size))
                    per = f'{ded * 100 / int(size):.1f}%  [{ded / 1024 / 1024:.1f} / {int(size) / 1024 / 1024:.1f} MB]'
                    yet = '#' * done
                    of = ' ' * (20 - done)
                    try:
                        await bot.edit_message_text(message.chat.id, load.message_id, 'Downloading... {}\n'
                                                                                      '[{}{}]'.format(per, yet, of))
                    except Exception as e:
                        print(repr(e))

        await bot.edit_message_text(message.chat.id, load.message_id, f'Downloading... 100%')
        upload = await bot.send_message(message.chat.id, 'Uploading...')
        file = await bot.send_document(message.chat.id, file_name, progress=callback,
                                       progress_args=(message.chat.id, upload.message_id))
        await bot.delete_messages(message.chat.id, [load.message_id, upload.message_id])
        await bot.forward_messages(database_id, message.chat.id, file.message_id)

        try:
            os.remove(file_name)
        except FileNotFoundError:
            pass

    except Exception as e:
        await bot.send_message(logs_id, repr(e))
        await bot.send_message(message.chat.id, 'Error occurred.')

bot.run()

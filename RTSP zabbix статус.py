import subprocess
import cv2
import requests
import time

MAX_RETRIES = 5
RETRY_DELAY = 10

ZABBIX_SERVER = 'адресс сервера'
ZABBIX_PORT = 10051

def send_to_zabbix_trapper(item_key, value):
    zabbix_sender_path = '/usr/bin/zabbix_sender'  # Путь к zabbix_sender
    zabbix_config_path = '/etc/zabbix/zabbix_agentd.conf'  # Путь к конфигурационному файлу zabbix_agentd.conf
    cmd = [zabbix_sender_path, '-z', ZABBIX_SERVER, '-p', str(ZABBIX_PORT), '-s', 'Укажите имя узла сети', '-k', item_key, '-o', str(value), '-vv', '-c', zabbix_config_path]

    # Выводим отладочную информацию перед выполнением команды
    print("Debug: Executing zabbix_sender command:")
    print(" ".join(cmd))

    subprocess.run(cmd)
def check_rtsp_streams_with_retries(urls):
    while True:
        results = {}
        for url in urls:
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    cap = cv2.VideoCapture(url)
                    if not cap.isOpened():
                        retries += 1
                        print(f"Не удалось подключиться к RTSP потоку {url}. Повторная попытка через {RETRY_DELAY} секунд.")
                        time.sleep(RETRY_DELAY)
                    else:
                        cap.release()
                        results[url] = True
                        break
                except Exception as e:
                    print(f"Ошибка при проверке потока {url}: {e}")
                    retries += 1
                    print(f"Повторная попытка через {RETRY_DELAY} секунд.")
                    time.sleep(RETRY_DELAY)
            if retries == MAX_RETRIES:
                results[url] = False

        for url, status in results.items():
            if status:
                print(f"RTSP поток {url} доступен")
                send_to_zabbix_trapper(f"rtsp.status", 1)
            else:
                print(f"RTSP поток {url} недоступен")
                send_to_zabbix_trapper(f"rtsp.status", 0)

#RTSP URL для проверки
rtsp_urls = ["Вставте вашу ссылку"]

check_rtsp_streams_with_retries(rtsp_urls)
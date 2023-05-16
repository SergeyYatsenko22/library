import requests
#
# url = "https://dvmn.org/filer/canonical/1542890876/16/"
#
# responce = requests.get(url)
# responce.raise_for_status()
#
# file_name = 'dvm.svg'
# with open (file_name, 'wb') as file:
#     file.write(responce.content)


url = "https://tululu.org/txt.php?id=32168"

responce = requests.get(url)
responce.raise_for_status()

file_name = 'sands_of_mars.txt'
with open (file_name, 'wb') as file:
    file.write(responce.content)

import urllib.request, urllib.error

for path in ['/','/projects/','/reports/','/users/me']:
    url = f'http://127.0.0.1:8000{path}'
    try:
        resp = urllib.request.urlopen(url)
        print(path, '->', resp.status)
        data = resp.read().decode()
        print(data[:200])
    except urllib.error.HTTPError as e:
        print(path, '-> HTTP', e.code)
        try:
            print(e.read().decode()[:200])
        except Exception:
            pass
    except Exception as ex:
        print(path, '-> ERR', ex)

import argparse
from bs4 import BeautifulSoup
import httpx

# ANSI color codes
VIOLET = '\033[95m'
CYAN = '\033[96m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
ORANGE = '\033[33m'
ENDC = '\033[0m'

parser = argparse.ArgumentParser(description='Test the domains for http or https!')
parser.add_argument('-l', '--lists', help='Add your domain list (e.g. "-l domain_list.txt")')
parser.add_argument('--title', help='Display page title', action='store_true')
parser.add_argument('-sc', help='Display Response status code', action='store_true')
parser.add_argument('-cl', help='Display Content-Length', action='store_true')
parser.add_argument('-nc', '--no-color', help='Disable colored output', action='store_true')

args = parser.parse_args()

def check_http(domain):
    try:
        url_https = f'https://{domain}'
        url_http = f'http://{domain}'
        
        with httpx.Client() as client:
            try:
                response = client.get(url_https)
                return url_https, response
            except httpx.RequestError:
                try:
                    response = client.get(url_http)
                    return url_http, response
                except httpx.RequestError:
                    return None, None
    except httpx.ConnectError:
        return None, None

def get_status_color(status_code):
    status_code = int(status_code)
    if 200 <= status_code < 300:
        return GREEN
    elif 300 <= status_code < 400:
        return YELLOW
    elif 400 <= status_code < 500:
        return RED
    elif 500 <= status_code <= 600:
        return ORANGE
    else:
        return ENDC

def main():
    with open(args.lists, 'r') as domain_file:
        domains = [line.strip() for line in domain_file.readlines()]
        for domain in domains:
            final_check, res = check_http(domain)
            
            if final_check is None:
                final_check = f"{domain} [Not Alive]"
            else:
                soup = BeautifulSoup(res.content, 'html.parser')
                title_tag = soup.find('title')
                title = title_tag.get_text() if title_tag else 'N/A'
                content_length = str(res.headers.get('Content-Length', 'N/A'))
                status_code = str(res.status_code)
                
                if args.title:
                    final_check += ' ' + f'[{CYAN}{title}{ENDC}]'
                if args.cl:
                    final_check += ' ' + f'[{VIOLET}{content_length}{ENDC}]'
                if args.sc:
                    status_color = get_status_color(status_code)
                    final_check += ' ' + f'[{status_color}{status_code}{ENDC}]'
            
            if args.no_color:
                final_check = final_check.replace(ORANGE, '').replace(RED, '').replace(YELLOW, '').replace(GREEN, '').replace(ENDC, '').replace(VIOLET, '').replace(CYAN, '')
            print(final_check)

if __name__ == '__main__':
    main()

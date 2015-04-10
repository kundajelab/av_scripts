import getpass
import sys

import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

WAIT_TIME = 10
METADATA_URL = \
        'https://www.encodeproject.org/metadata/type=experiment&assay_term_name=DNase-seq&limit=all&status=submitted&status=release%20ready/metadata.tsv'  # nopep8


def get_auth_details():
    email = raw_input('Email: ')
    password = getpass.getpass()
    return email, password


def get_login_cookies():
    # Main script
    email, password = get_auth_details()

    # Login to portal
    driver = webdriver.Firefox()
    #driver = webdriver.PhantomJS()
#    driver.set_window_size(1280, 1024)
    driver.get('http://www.encodeproject.org')
    signin_link = driver.find_element_by_link_text('Sign in')
    signin_link.click()

    portal_window = driver.current_window_handle
    auth_window, = [handle for handle in driver.window_handles
                    if handle != portal_window]

    wait = WebDriverWait(driver, WAIT_TIME)

    driver.switch_to.window(auth_window)
    email_input = wait.until(
        EC.element_to_be_clickable((By.ID, 'authentication_email')))
    email_input.send_keys(email)
    email_input.submit()

    password_input = wait.until(
        EC.element_to_be_clickable((By.ID, 'authentication_password')))
    password_input.send_keys(password)
    password_input.submit()

    # Check that we're successfully logged in
    driver.switch_to.window(portal_window)

    # find_element_by_link_text doesn't work; maybe because text is not visible
    sign_out = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//a[contains(text(), "Sign out")]')))
    assert sign_out.get_attribute('data-trigger') == 'logout'

    # Extract session cookies, then use requests or some other lib to actually
    # do the download
    cookies = driver.get_cookies()
    driver.quit()
    return cookies


def write_cookies(cookies, output_file):
    format_str = \
        '{domain}\tFALSE\t{path}\t{secure}\t{expiry}\t{name}\t{value}\n'

    with open(output_file, 'w') as fp:
        for cookie in cookies:
            if 'expiry' not in cookie:
                cookie['expiry'] = 99999999999
            fp.write(format_str.format(**cookie))


def parse_metadata():
    pass


METADATA_FILE = 'metadata.tsv'
COOKIE_FILE = 'encode_cookies.txt'
SEARCH_TERMS = ['K562', 'HeLa-S3', 'HepG2', 'MEL cell line', 'BJ']
FILE_LIST = 'filelist.txt'

if __name__ == '__main__':
    cookies = get_login_cookies()
    write_cookies(cookies, COOKIE_FILE)
    sys.exit(0);
    session_cookies = {cookie['name']: cookie['value']
                       for cookie in cookies}
    metadata_tsv = requests.get(METADATA_URL, cookies=session_cookies)

    with open(METADATA_FILE, 'w') as fp:
        fp.writelines(metadata_tsv)

    # Parse tsv for interesting samples and generate wget/curl commands
    download_size = 0
    num_files = 0
    metadata = pd.read_table(METADATA_FILE)

    with open(FILE_LIST, 'w') as fp:
        for term in SEARCH_TERMS:
            rows = metadata[(metadata['Biosample term name'] == term) &
                            (metadata['File format'] == 'fastq')]
            for md5, filename in rows[['md5sum', 'File download URL']].values:
                fp.write('%s %s\n' % (filename, md5))
            num_files += rows.shape[0]
            download_size += rows['Size'].sum()

    sys.stderr.write('Cookies:\t%s\n'
                     'Metadata:\t%s\n'
                     'Filelist:\t%s\n\n'
                     'Files:\t%d\n'
                     'Size:\t%.2f GB\n' %
                     (COOKIE_FILE, METADATA_FILE, FILE_LIST,
                      num_files, download_size / 1e9))

from setuptools import setup

APP = ['web_app.py']
DATA_FILES = ['templates', 'static']
OPTIONS = {
    'argv_emulation': True,
    'packages': ['flask', 'pandas', 'numpy', 'akshare', 'vectorbt', 'plotly', 'apscheduler', 'schedule', 'loguru', 'requests'],
    'resources': ['requirements.txt'],
    'plist': {
        'CFBundleName': 'GoldQuantWeb',
        'CFBundleDisplayName': '黄金量化交易系统',
        'CFBundleVersion': '2.0',
        'CFBundleShortVersionString': '2.0',
        'CFBundleIdentifier': 'com.goldquant.web',
        'NSHumanReadableCopyright': '© 2026 GoldQuant. All rights reserved.',
        'LSBackgroundOnly': False,
        'LSUIElement': False,
    },
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
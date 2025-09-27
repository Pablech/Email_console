from setuptools import setup, find_packages

setup(
    name='email_console',
    version='0.1.0',
    description='Pacote para envio de e-mails via console',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Pablech',
    url='https://github.com/Pablech/Email_console',
    packages=find_packages(),
    install_requires=[
        'requests>=2.0.0',
        'email-validator>=2.0.0',
        'python-dotenv>=1.0.0',
    ],
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
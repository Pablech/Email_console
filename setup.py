from setuptools import setup, find_packages

setup(
    name='email_console',
    version='0.1.0',
    description='Pacote para envio de e-mails via console',
    author='Pablech',
    packages=find_packages(),
    install_requires=[
        # Adicione dependências aqui, por exemplo:
        # 'requests>=2.0.0',
    ],
    python_requires='>=3.6',
)
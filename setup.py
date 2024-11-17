from setuptools import setup, find_packages

setup(
    name="codeokey",  # Имя вашего пакета
    version="0.1",            # Версия пакета
    packages=find_packages(), # Автоматически находит все пакеты и модули
    description="Library for programming in Minecraft",  # Описание пакета
    author="Kirito",  # Автор библиотеки
    classifiers=[  # Классификаторы, описывающие ваш пакет
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
    ],
)

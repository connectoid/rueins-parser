import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from transliterate import translit, get_available_language_codes

from .models_donor import Base_donor, Download, Category

# engine_donor = create_engine("mysql+pymysql://admin:s028006000434@localhost/manualsdb_donor?charset=utf8mb4")
engine_donor = create_engine("mysql+pymysql://root:9a9At1l8IS@localhost/innersun_manualb?charset=utf8mb4")
Base_donor.metadata.create_all(engine_donor)
Session_donor = sessionmaker(bind=engine_donor)


def get_manual_titles_from_donor():
    session = Session_donor()
    manuals = session.query(Download).all()
    manuals_titles = [manual.title for manual in manuals]
    return manuals_titles


def create_category(brand_name, category_name, description):
    session = Session_donor()
    category = session.query(Category).filter(Category.name == category_name).first()
    if category is None:
        new_category = Category(
                name=category_name,
                dir=brand_name.lower(),
                alt_name=translit(category_name.replace(' ', '-').lower(), language_code='ru', reversed=True),
                descr=description,
                keywords=f'{brand_name}, {category_name}'
        )
        session.add(new_category)
        session.commit()
        return True
    return False


def create_download(title, brand_name, category_name, xfields, description, filename, filesize):
    session = Session_donor()
    download = session.query(Download).filter(Download.title == title).first()
    if download is None:
        print(f'Интсрукции {title} нет в базе, созадем новую')
        category = session.query(Category).filter(Category.name == category_name).first()
        if category is None:
            print(f'Категории {category_name} не существует, добавляем новую')
            create_category(brand_name, category_name, description)
            cat = session.query(Category).filter(Category.name == category_name).first()
            category_id = cat.id
            new_download = Download(
                title=title,
                alt_name=title.replace(' ', '-').lower(),
                xfields=xfields,
                # brand=brand_name,
                category=str(category_id),
                # description=description,
                filename=filename.replace(' ', '-'),
                size=filesize
            )
        else:
            print(f'Категория {category_name} уже есть в базе, пропускаем')
            cat = session.query(Category).filter(Category.name == category_name).first()
            category_id = cat.id
            new_download = Download(
                title=title,
                alt_name=title.replace(' ', '-').lower(),
                xfields=xfields,
                # brand=brand_name,
                category=str(category_id),
                # description=description,
                filename=filename.replace(' ', '-'),
                size=filesize
            )
        session.add(new_download)
        session.commit()
        return True
    else:
        print(f'Инструкция {title} уже есть в базе пропускаем')
        return False

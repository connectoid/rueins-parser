import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from transliterate import translit, get_available_language_codes

from .models import Base_donor, Download, Category

# engine_donor = create_engine("mysql+pymysql://admin:s028006000434@localhost/manualsdb_donor?charset=utf8mb4")
engine_donor = create_engine("mysql+pymysql://root:9a9At1l8IS@localhost/innersun_manualb?charset=utf8mb4")
Base_donor.metadata.create_all(engine_donor)
Session = sessionmaker(bind=engine_donor)


def get_manual_titles_from_donor():
    session = Session()
    manuals = session.query(Download).all()
    manuals_titles = [manual.title for manual in manuals]
    return manuals_titles


def create_download(title, xfields, category_id, filename, filesize, thumbnale_filename):
    session = Session()
    download = session.query(Download).filter(Download.title == title).first()
    if download is None:
        # print(f'Инструкции {title} нет в базе, созадем новую')
        category_id = category_id
        new_download = Download(
            title=title,
            alt_name=title.replace(' ', '-').lower(),
            xfields=xfields,
            category=str(category_id),
            filename=filename.replace(' ', '-'),
            size=filesize,
            screenshot=thumbnale_filename,
            thumb_screenshot=thumbnale_filename
        )
        session.add(new_download)
        session.commit()
        return True
    else:
        print(f'~~~~~~~~~~> Третья проверка. Инструкция {title} уже есть в базе пропускаем')
        return False

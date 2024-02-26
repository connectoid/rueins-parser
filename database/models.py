from sqlalchemy import Column, Integer, Float, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


Base = declarative_base()
Base_donor = declarative_base()


class Download(Base_donor):
    __tablename__ = 'dle_downloads'
    id = Column(Integer, primary_key=True)
    autor = Column(String(40), nullable=False, default='mbadmin')
    date = Column(DateTime(timezone=True), default=func.now())
    screen_url = Column(String(255), nullable=False, default='')
    desc_url1 = Column(Text, nullable=False, default='')
    desc_url2 = Column(Text, nullable=False, default='')
    version = Column(String(50), nullable=False, default='')
    description = Column(Text, nullable=False, default='0')
    alt_name = Column(String(200), nullable=False, default='')
    xfields = Column(Text, nullable=False, default='')
    screenshot = Column(String(200), nullable=False, default='')
    thumb_screenshot = Column(String(250), nullable=False, default='')
    filename = Column(String(255), nullable=False, default='')
    descr = Column(String(200), nullable=False, default='')
    keywords = Column(Text, nullable=False, default='')
    category = Column(String(200), nullable=False, default='')
    comm_num = Column(Integer, nullable=False, default=0)
    allow_comm = Column(Integer, nullable=False, default=1)
    approve = Column(Integer, nullable=False, default=0)
    rating = Column(Integer, nullable=False, default=0)
    vote_num = Column(Integer, nullable=False, default=0)
    news_read = Column(Integer, nullable=False, default=1)
    allow_rate = Column(Integer, nullable=False, default=1)
    allow_br = Column(Integer, nullable=False, default=1)
    allow_main = Column(Integer, nullable=False, default=1)
    access = Column(String(150), nullable=False, default='')
    version1 = Column(Integer, nullable=False, default=0)
    platform1 = Column(String(250), nullable=False, default='')
    to_ftp = Column(Integer, nullable=False, default=0)
    reason = Column(String(200), nullable=False, default='')
    view_edit = Column(Integer, nullable=False, default=0)
    editdate = Column(String(15), nullable=False, default='')
    editor = Column(String(40), nullable=False, default='')
    description_full = Column(Text, nullable=False, default='')
    allow_block = Column(Integer, nullable=False, default=0)
    news_fixed = Column(Integer, nullable=False, default=0)
    vip = Column(Integer, nullable=False, default=0)
    pdf_view = Column(Integer, nullable=False, default=0)
    size = Column(Integer, nullable=False, default=0)
    title = Column(String(255), nullable=False, default='')
    # alt_name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False, default='')
    category = Column(String(200), nullable=False, default='')

class Category(Base_donor):
    __tablename__ = 'dle_cat_downloads'
    id = Column(Integer, primary_key=True)
    parentid = Column(Integer, nullable=False, default=6)
    name = Column(String(50), nullable=False)
    dir = Column(String(25), nullable=False)
    alt_name = Column(String(25), nullable=False)
    descr = Column(String(25), nullable=False)
    keywords = Column(Text, nullable=False)
    status_down = Column(Integer, nullable=False, default=0)
    order_id = Column(Integer, nullable=False, default=0)




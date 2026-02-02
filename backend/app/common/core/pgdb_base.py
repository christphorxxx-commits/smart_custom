# -*- coding: utf-8 -*-

# db_pg.py
import psycopg2
import numpy as np
import os
from dotenv import load_dotenv
load_dotenv()
import sys

# 设置Python默认编码（可选，用于兼容）
# reload(sys) if 'reload' in dir(sys) else None
# sys.setdefaultencoding('utf-8') if hasattr(sys, 'setdefaultencoding') else None

# =========================
# PostgreSQL config
# =========================



def get_db_conn():
    """get a database connection"""
    try:
        # 显式指定连接编码为UTF8，并处理参数编码问题
        conn = psycopg2.connect(
            host=os.getenv("PG_HOST"),
            database=os.getenv("PG_DB"),
            user=os.getenv("PG_USER"),
            password=os.getenv("PG_PASSWORD"),
            port=os.getenv("PG_PORT"),
            options='-c client_encoding=utf8'  # 强制客户端编码为UTF8
        )
        # 设置连接的编码
        conn.set_client_encoding('UTF8')
        return conn
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        raise  # 抛出异常让调用方处理



def insert_face(name: str, embedding: np.ndarray, img_path: str = None):
    """insert a human face embedding"""
    conn = None
    cur = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        # 确保字符串参数都是UTF8编码
        name_utf8 = name.encode('utf-8').decode('utf-8') if name else None
        img_path_utf8 = img_path.encode('utf-8').decode('utf-8') if img_path else None

        cur.execute(
            """
            INSERT INTO face_embeddings (name, embedding, img_path)
            VALUES (%s, %s, %s)
            """,
            (name_utf8, embedding.tolist(), img_path_utf8)
        )
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"插入人脸数据失败: {str(e)}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def load_all_faces() -> dict:
    """
    load all human face embedding
    return:
        {
            "zhangsan": np.ndarray(512,),
            "lisi": np.ndarray(512,)
        }
    """
    conn = None
    cur = None
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT name, embedding FROM face_embeddings")
        rows = cur.fetchall()

        face_db = {}
        for name, emb in rows:
            # 解码数据库返回的字符串为UTF8
            name_utf8 = name.encode('utf-8').decode('utf-8') if name else None
            face_db[name_utf8] = np.array(emb, dtype=np.float32)

        return face_db
    except Exception as e:
        print(f"加载人脸数据失败: {str(e)}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    try:
        conn = get_db_conn()
        print("PG connected successfully!")
        conn.close()
    except Exception as e:
        print(f"连接测试失败: {e}")
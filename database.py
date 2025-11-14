import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

DB_NAME = "wallet.db"

def init_db():
    """데이터베이스 및 테이블 초기화"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount INTEGER NOT NULL,
            place TEXT,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_expense(date: str, category: str, amount: int, place: str, description: str) -> bool:
    """지출 내역 추가"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO expenses (date, category, amount, place, description)
            VALUES (?, ?, ?, ?, ?)
        """, (date, category, amount, place, description))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error adding expense: {e}")
        return False


def get_all_expenses() -> List[Tuple]:
    """모든 지출 내역 조회"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, category, amount, place, description
        FROM expenses
        ORDER BY date DESC, id DESC
    """)

    expenses = cursor.fetchall()
    conn.close()

    return expenses


def get_expenses_by_date_range(start_date: str, end_date: str) -> List[Tuple]:
    """날짜 범위로 지출 내역 조회"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, category, amount, place, description
        FROM expenses
        WHERE date BETWEEN ? AND ?
        ORDER BY date DESC, id DESC
    """, (start_date, end_date))

    expenses = cursor.fetchall()
    conn.close()

    return expenses


def get_expenses_by_category(category: str) -> List[Tuple]:
    """카테고리별 지출 내역 조회"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, date, category, amount, place, description
        FROM expenses
        WHERE category = ?
        ORDER BY date DESC, id DESC
    """, (category,))

    expenses = cursor.fetchall()
    conn.close()

    return expenses


def update_expense(expense_id: int, date: str, category: str, amount: int, place: str, description: str) -> bool:
    """지출 내역 수정"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE expenses
            SET date = ?, category = ?, amount = ?, place = ?, description = ?
            WHERE id = ?
        """, (date, category, amount, place, description, expense_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating expense: {e}")
        return False


def delete_expense(expense_id: int) -> bool:
    """지출 내역 삭제"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting expense: {e}")
        return False


def get_category_summary() -> List[Tuple]:
    """카테고리별 지출 합계"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM expenses
        GROUP BY category
        ORDER BY total DESC
    """)

    summary = cursor.fetchall()
    conn.close()

    return summary


def get_monthly_summary(year: int, month: int) -> List[Tuple]:
    """월별 지출 요약"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 해당 월의 첫날과 마지막 날 계산
    if month == 12:
        next_month = f"{year+1}-01-01"
    else:
        next_month = f"{year}-{month+1:02d}-01"

    current_month = f"{year}-{month:02d}-01"

    cursor.execute("""
        SELECT category, SUM(amount) as total, COUNT(*) as count
        FROM expenses
        WHERE date >= ? AND date < ?
        GROUP BY category
        ORDER BY total DESC
    """, (current_month, next_month))

    summary = cursor.fetchall()
    conn.close()

    return summary

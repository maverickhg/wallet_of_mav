import sqlite3
import os
from datetime import datetime
from typing import List, Tuple, Optional
import streamlit as st

# Google Sheets 사용 여부 확인
USE_GSHEETS = os.getenv("USE_GSHEETS", "false").lower() == "true" or hasattr(st, "secrets") and "gcp_service_account" in st.secrets

if USE_GSHEETS:
    import gspread
    from google.oauth2.service_account import Credentials

DB_NAME = "wallet.db"


class Database:
    """데이터베이스 추상화 클래스"""

    def init_db(self):
        raise NotImplementedError

    def add_expense(self, date: str, category: str, amount: int, place: str, description: str) -> bool:
        raise NotImplementedError

    def get_all_expenses(self) -> List[Tuple]:
        raise NotImplementedError

    def get_expenses_by_date_range(self, start_date: str, end_date: str) -> List[Tuple]:
        raise NotImplementedError

    def get_expenses_by_category(self, category: str) -> List[Tuple]:
        raise NotImplementedError

    def update_expense(self, expense_id: int, date: str, category: str, amount: int, place: str, description: str) -> bool:
        raise NotImplementedError

    def delete_expense(self, expense_id: int) -> bool:
        raise NotImplementedError

    def get_category_summary(self) -> List[Tuple]:
        raise NotImplementedError

    def get_monthly_summary(self, year: int, month: int) -> List[Tuple]:
        raise NotImplementedError


class SQLiteDatabase(Database):
    """SQLite 데이터베이스"""

    def init_db(self):
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

    def add_expense(self, date: str, category: str, amount: int, place: str, description: str) -> bool:
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

    def get_all_expenses(self) -> List[Tuple]:
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

    def get_expenses_by_date_range(self, start_date: str, end_date: str) -> List[Tuple]:
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

    def get_expenses_by_category(self, category: str) -> List[Tuple]:
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

    def update_expense(self, expense_id: int, date: str, category: str, amount: int, place: str, description: str) -> bool:
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

    def delete_expense(self, expense_id: int) -> bool:
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

    def get_category_summary(self) -> List[Tuple]:
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

    def get_monthly_summary(self, year: int, month: int) -> List[Tuple]:
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


class GoogleSheetsDatabase(Database):
    """Google Sheets 데이터베이스"""

    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

        # Streamlit secrets에서 자격 증명 가져오기
        credentials = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scope
        )

        self.client = gspread.authorize(credentials)
        self.sheet_url = st.secrets.get("sheet_url", "")

        if not self.sheet_url:
            raise ValueError("sheet_url이 Streamlit secrets에 설정되지 않았습니다.")

        self.spreadsheet = self.client.open_by_url(self.sheet_url)
        self.worksheet = self.spreadsheet.sheet1

    def init_db(self):
        """스프레드시트 헤더 초기화"""
        try:
            # 첫 번째 행이 비어있으면 헤더 추가
            if not self.worksheet.row_values(1):
                self.worksheet.append_row(['id', 'date', 'category', 'amount', 'place', 'description', 'created_at'])
        except Exception as e:
            print(f"Error initializing sheet: {e}")

    def _get_next_id(self) -> int:
        """다음 ID 가져오기"""
        all_records = self.worksheet.get_all_records()
        if not all_records:
            return 1
        return max([int(record.get('id', 0)) for record in all_records]) + 1

    def add_expense(self, date: str, category: str, amount: int, place: str, description: str) -> bool:
        """지출 내역 추가"""
        try:
            expense_id = self._get_next_id()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.worksheet.append_row([
                expense_id, date, category, amount, place or "", description or "", created_at
            ])
            return True
        except Exception as e:
            print(f"Error adding expense: {e}")
            return False

    def get_all_expenses(self) -> List[Tuple]:
        """모든 지출 내역 조회"""
        try:
            records = self.worksheet.get_all_records()
            expenses = [
                (int(r['id']), r['date'], r['category'], int(r['amount']), r['place'], r['description'])
                for r in records
            ]
            # 날짜 역순 정렬
            expenses.sort(key=lambda x: (x[1], x[0]), reverse=True)
            return expenses
        except Exception as e:
            print(f"Error getting expenses: {e}")
            return []

    def get_expenses_by_date_range(self, start_date: str, end_date: str) -> List[Tuple]:
        """날짜 범위로 지출 내역 조회"""
        all_expenses = self.get_all_expenses()
        return [e for e in all_expenses if start_date <= e[1] <= end_date]

    def get_expenses_by_category(self, category: str) -> List[Tuple]:
        """카테고리별 지출 내역 조회"""
        all_expenses = self.get_all_expenses()
        return [e for e in all_expenses if e[2] == category]

    def update_expense(self, expense_id: int, date: str, category: str, amount: int, place: str, description: str) -> bool:
        """지출 내역 수정"""
        try:
            records = self.worksheet.get_all_records()
            for idx, record in enumerate(records, start=2):  # 2부터 시작 (헤더 제외)
                if int(record['id']) == expense_id:
                    self.worksheet.update(f'B{idx}:F{idx}', [[date, category, amount, place or "", description or ""]])
                    return True
            return False
        except Exception as e:
            print(f"Error updating expense: {e}")
            return False

    def delete_expense(self, expense_id: int) -> bool:
        """지출 내역 삭제"""
        try:
            records = self.worksheet.get_all_records()
            for idx, record in enumerate(records, start=2):  # 2부터 시작 (헤더 제외)
                if int(record['id']) == expense_id:
                    self.worksheet.delete_rows(idx)
                    return True
            return False
        except Exception as e:
            print(f"Error deleting expense: {e}")
            return False

    def get_category_summary(self) -> List[Tuple]:
        """카테고리별 지출 합계"""
        try:
            expenses = self.get_all_expenses()
            summary = {}
            for e in expenses:
                category = e[2]
                amount = e[3]
                if category in summary:
                    summary[category]['total'] += amount
                    summary[category]['count'] += 1
                else:
                    summary[category] = {'total': amount, 'count': 1}

            result = [(cat, data['total'], data['count']) for cat, data in summary.items()]
            result.sort(key=lambda x: x[1], reverse=True)
            return result
        except Exception as e:
            print(f"Error getting summary: {e}")
            return []

    def get_monthly_summary(self, year: int, month: int) -> List[Tuple]:
        """월별 지출 요약"""
        try:
            # 해당 월의 첫날과 마지막 날 계산
            if month == 12:
                next_month = f"{year+1}-01-01"
            else:
                next_month = f"{year}-{month+1:02d}-01"

            current_month = f"{year}-{month:02d}-01"

            expenses = self.get_expenses_by_date_range(current_month, next_month)
            summary = {}
            for e in expenses:
                category = e[2]
                amount = e[3]
                if category in summary:
                    summary[category]['total'] += amount
                    summary[category]['count'] += 1
                else:
                    summary[category] = {'total': amount, 'count': 1}

            result = [(cat, data['total'], data['count']) for cat, data in summary.items()]
            result.sort(key=lambda x: x[1], reverse=True)
            return result
        except Exception as e:
            print(f"Error getting monthly summary: {e}")
            return []


# 데이터베이스 인스턴스 생성
if USE_GSHEETS:
    _db = GoogleSheetsDatabase()
else:
    _db = SQLiteDatabase()


# 기존 함수들은 데이터베이스 인스턴스로 위임
def init_db():
    return _db.init_db()

def add_expense(date: str, category: str, amount: int, place: str, description: str) -> bool:
    return _db.add_expense(date, category, amount, place, description)

def get_all_expenses() -> List[Tuple]:
    return _db.get_all_expenses()

def get_expenses_by_date_range(start_date: str, end_date: str) -> List[Tuple]:
    return _db.get_expenses_by_date_range(start_date, end_date)

def get_expenses_by_category(category: str) -> List[Tuple]:
    return _db.get_expenses_by_category(category)

def update_expense(expense_id: int, date: str, category: str, amount: int, place: str, description: str) -> bool:
    return _db.update_expense(expense_id, date, category, amount, place, description)

def delete_expense(expense_id: int) -> bool:
    return _db.delete_expense(expense_id)

def get_category_summary() -> List[Tuple]:
    return _db.get_category_summary()

def get_monthly_summary(year: int, month: int) -> List[Tuple]:
    return _db.get_monthly_summary(year, month)

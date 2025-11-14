import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import database as db

# 페이지 설정
st.set_page_config(page_title="가계부", page_icon="💰", layout="wide")

# 데이터베이스 초기화
db.init_db()

# 카테고리 목록
CATEGORIES = ["밥", "커피", "농구", "사람(술 등)", "기타"]

# 사이드바
st.sidebar.title("💰 가계부")
menu = st.sidebar.radio("메뉴", ["지출 추가", "지출 내역", "통계"])

# ========== 지출 추가 ==========
if menu == "지출 추가":
    st.header("💳 지출 추가")

    with st.form("add_expense_form"):
        col1, col2 = st.columns(2)

        with col1:
            expense_date = st.date_input("날짜", value=date.today())
            category = st.selectbox("항목", CATEGORIES)
            amount = st.number_input("금액 (원)", min_value=0, step=100)

        with col2:
            place = st.text_input("지출처")
            description = st.text_area("내용", height=100)

        submitted = st.form_submit_button("추가")

        if submitted:
            if amount > 0:
                success = db.add_expense(
                    date=expense_date.strftime("%Y-%m-%d"),
                    category=category,
                    amount=amount,
                    place=place,
                    description=description
                )
                if success:
                    st.success("✅ 지출이 추가되었습니다!")
                    st.rerun()
                else:
                    st.error("❌ 지출 추가에 실패했습니다.")
            else:
                st.warning("⚠️ 금액을 입력해주세요.")

    # 최근 지출 내역 표시
    st.divider()
    st.subheader("최근 지출 내역 (5개)")

    recent_expenses = db.get_all_expenses()[:5]
    if recent_expenses:
        df = pd.DataFrame(recent_expenses, columns=["ID", "날짜", "항목", "금액", "지출처", "내용"])
        df["금액"] = df["금액"].apply(lambda x: f"{x:,}원")
        st.dataframe(df.drop("ID", axis=1), use_container_width=True, hide_index=True)
    else:
        st.info("아직 지출 내역이 없습니다.")


# ========== 지출 내역 ==========
elif menu == "지출 내역":
    st.header("📊 지출 내역")

    # 필터 옵션
    filter_type = st.radio("조회 방식", ["전체", "날짜 범위", "카테고리별"], horizontal=True)

    if filter_type == "날짜 범위":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("시작 날짜", value=date.today() - timedelta(days=30))
        with col2:
            end_date = st.date_input("종료 날짜", value=date.today())

        expenses = db.get_expenses_by_date_range(
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )

    elif filter_type == "카테고리별":
        selected_category = st.selectbox("카테고리 선택", CATEGORIES)
        expenses = db.get_expenses_by_category(selected_category)

    else:  # 전체
        expenses = db.get_all_expenses()

    # 지출 내역 표시
    if expenses:
        df = pd.DataFrame(expenses, columns=["ID", "날짜", "항목", "금액", "지출처", "내용"])

        # 통계 표시
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 지출", f"{df['금액'].sum():,}원")
        with col2:
            st.metric("지출 건수", f"{len(df)}건")
        with col3:
            st.metric("평균 지출", f"{int(df['금액'].mean()):,}원")

        st.divider()

        # 데이터프레임 표시
        display_df = df.copy()
        display_df["금액"] = display_df["금액"].apply(lambda x: f"{x:,}원")
        st.dataframe(display_df.drop("ID", axis=1), use_container_width=True, hide_index=True)

        # 수정/삭제 기능
        st.divider()
        st.subheader("수정 / 삭제")

        col1, col2 = st.columns([2, 1])
        with col1:
            expense_id = st.selectbox("수정/삭제할 항목 선택", df["ID"].tolist(),
                                      format_func=lambda x: f"ID {x} - {df[df['ID']==x]['날짜'].values[0]} - {df[df['ID']==x]['항목'].values[0]} - {df[df['ID']==x]['금액'].values[0]:,}원")

        with col2:
            action = st.radio("작업 선택", ["수정", "삭제"], horizontal=True)

        if action == "삭제":
            if st.button("🗑️ 삭제", type="primary"):
                if db.delete_expense(expense_id):
                    st.success("✅ 삭제되었습니다!")
                    st.rerun()
                else:
                    st.error("❌ 삭제에 실패했습니다.")

        else:  # 수정
            selected_expense = df[df["ID"] == expense_id].iloc[0]

            with st.form("edit_expense_form"):
                col1, col2 = st.columns(2)

                with col1:
                    edit_date = st.date_input("날짜", value=datetime.strptime(selected_expense["날짜"], "%Y-%m-%d").date())
                    edit_category = st.selectbox("항목", CATEGORIES, index=CATEGORIES.index(selected_expense["항목"]))
                    edit_amount = st.number_input("금액 (원)", value=int(selected_expense["금액"]), min_value=0, step=100)

                with col2:
                    edit_place = st.text_input("지출처", value=selected_expense["지출처"] if selected_expense["지출처"] else "")
                    edit_description = st.text_area("내용", value=selected_expense["내용"] if selected_expense["내용"] else "", height=100)

                if st.form_submit_button("✏️ 수정"):
                    if db.update_expense(expense_id, edit_date.strftime("%Y-%m-%d"), edit_category, edit_amount, edit_place, edit_description):
                        st.success("✅ 수정되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 수정에 실패했습니다.")

    else:
        st.info("지출 내역이 없습니다.")


# ========== 통계 ==========
elif menu == "통계":
    st.header("📈 통계")

    # 월 선택
    col1, col2 = st.columns(2)
    with col1:
        selected_year = st.selectbox("년도", range(2020, 2031), index=date.today().year - 2020)
    with col2:
        selected_month = st.selectbox("월", range(1, 13), index=date.today().month - 1)

    # 전체 통계
    st.subheader("📊 전체 통계")
    all_summary = db.get_category_summary()

    if all_summary:
        summary_df = pd.DataFrame(all_summary, columns=["카테고리", "총 지출", "건수"])

        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(summary_df.set_index("카테고리")["총 지출"])

        with col2:
            for idx, row in summary_df.iterrows():
                st.metric(row["카테고리"], f"{row['총 지출']:,}원", f"{row['건수']}건")

    else:
        st.info("아직 통계 데이터가 없습니다.")

    st.divider()

    # 월별 통계
    st.subheader(f"📅 {selected_year}년 {selected_month}월 통계")
    monthly_summary = db.get_monthly_summary(selected_year, selected_month)

    if monthly_summary:
        monthly_df = pd.DataFrame(monthly_summary, columns=["카테고리", "총 지출", "건수"])

        col1, col2 = st.columns([2, 1])
        with col1:
            st.bar_chart(monthly_df.set_index("카테고리")["총 지출"])

        with col2:
            total_monthly = monthly_df["총 지출"].sum()
            st.metric("이번 달 총 지출", f"{total_monthly:,}원")
            st.divider()
            for idx, row in monthly_df.iterrows():
                percentage = (row["총 지출"] / total_monthly * 100) if total_monthly > 0 else 0
                st.metric(row["카테고리"], f"{row['총 지출']:,}원", f"{percentage:.1f}%")

    else:
        st.info(f"{selected_year}년 {selected_month}월 지출 내역이 없습니다.")

"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.
"""

# Giả lập biến session lưu trữ sinh viên đang đăng nhập hệ thống
CURRENT_LOGGED_IN_USER = "SV123"


def get_student_transcript(target_student_id: str) -> str:
    """
    Tra cứu bảng điểm sinh viên, GPA, danh sách các môn đã đỗ/nợ.
    LƯU Ý BẢO MẬT: Một sinh viên chỉ được phép tra cứu thông tin của chính mình.

    Args:
        target_student_id (str): Mã sinh viên cần tra cứu (Ví dụ: 'SV123').

    Returns:
        str: Thông tin điểm số hoặc chuỗi báo lỗi từ chối quyền truy cập/không tìm thấy.
    """
    target_id = target_student_id.upper().strip()

    # Cơ chế kiểm tra quyền truy cập (Authorization)
    if target_id != CURRENT_LOGGED_IN_USER:
        return f"LỖI TỪ CHỐI TRUY CẬP: Hệ thống ghi nhận bạn là {CURRENT_LOGGED_IN_USER}. Bạn không có quyền xem bảng điểm của {target_id}."

    db = {
        "SV123": "GPA: 3.2, Đã đỗ: Hệ quản trị cơ sở dữ liệu, Nhập môn Python, Cấu trúc dữ liệu. Nợ: Không.",
        "SV456": "GPA: 2.8, Đã đỗ: Kỹ năng mềm. Nợ: Giải tích.",
    }

    return db.get(
        target_id, f"LỖI: Không tìm thấy dữ liệu cho mã sinh viên '{target_id}'."
    )


def search_course_catalog(keyword: str) -> str:
    """
    Tra cứu chương trình học, số tín chỉ, yêu cầu môn tiên quyết.

    Args:
        keyword (str): Mã môn hoặc tên môn (Ví dụ: 'IS201', 'Java', 'Machine Learning').

    Returns:
        str: Thông tin chi tiết của môn học hoặc chuỗi báo lỗi nếu không tìm thấy.
    """
    keyword_lower = keyword.lower().strip()

    if (
        "is201" in keyword_lower
        or "cơ sở dữ liệu" in keyword_lower
        or "sql" in keyword_lower
    ):
        return "Môn: Hệ quản trị cơ sở dữ liệu (IS201) - 3 tín chỉ. Tiên quyết: Không. Nội dung: SQL Server, MySQL, ETL pipelines."
    elif (
        "ds301" in keyword_lower
        or "machine learning" in keyword_lower
        or "học máy" in keyword_lower
    ):
        return "Môn: Học máy (DS301) - 4 tín chỉ. Tiên quyết: Xác suất thống kê, Nhập môn Python. Nội dung: Hồi quy, Phân loại, đánh giá model (AUC/ROC)."
    elif "it401" in keyword_lower or "java" in keyword_lower:
        return "Môn: Lập trình Java Ứng dụng (IT401) - 3 tín chỉ. Tiên quyết: Lập trình hướng đối tượng. Nội dung: Java Core, thiết kế Web App, quản lý kho."
    else:
        return f"LỖI: Không tìm thấy môn học nào khớp với từ khóa '{keyword}' trong hệ thống đào tạo."


def check_course_schedule(course_code: str) -> str:
    """
    Kiểm tra lịch học, phòng học, giảng viên và số slot còn trống của lớp học phần.

    Args:
        course_code (str): Mã môn học (Ví dụ: 'IS201', 'DS301').

    Returns:
        str: Thông tin lịch học chi tiết hoặc chuỗi báo lỗi.
    """
    code_upper = course_code.upper().strip()

    if code_upper == "IS201":
        return "Lớp IS201-01: Sáng T3 (08:00 - 11:30), Phòng E402. Giảng viên: Trần Văn A. Số slot còn trống: 5/40."
    elif code_upper == "DS301":
        return "Lớp DS301-02: Chiều T5 (13:30 - 17:00), Phòng Lab. Giảng viên: Nguyễn Thị B. Số slot còn trống: 0/30 (Đã đầy)."
    elif code_upper == "IT401":
        return "Lớp IT401-01: Sáng T2 (08:00 - 11:30), Phòng E403. Giảng viên: Lê Văn C. Số slot còn trống: 12/40."
    else:
        return f"LỖI: Không có lịch học nào được xếp cho mã môn '{code_upper}' trong học kỳ này."


# Danh sách các tool được đăng ký để Agent sử dụng
AVAILABLE_TOOLS = {
    "get_student_transcript": get_student_transcript,
    "search_course_catalog": search_course_catalog,
    "check_course_schedule": check_course_schedule,
}

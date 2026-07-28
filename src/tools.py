"""
🛠️ TOOL REGISTRY & SCHEMAS (Dành cho Role 2: Tool & Spec Engineer)
Nơi khai báo tất cả các "món đồ nghề" mà ReAct Agent có thể gọi.

Mốc 2: Định nghĩa tool contract chuẩn với Docstring đầy đủ.
Mốc 3: Đảm bảo mọi hàm bắt lỗi an toàn — không crash, luôn trả về chuỗi.
"""

# Giả lập biến session lưu trữ sinh viên đang đăng nhập hệ thống
CURRENT_LOGGED_IN_USER = "SV123"


# =============================================================================
# TOOL 1: get_student_transcript
# =============================================================================
def get_student_transcript(target_student_id: str) -> str:
    """
    Tra cứu bảng điểm sinh viên, GPA, danh sách các môn đã đỗ/nợ.

    Mục đích (Purpose):
        Dùng khi sinh viên muốn xem kết quả học tập của chính mình.
        LƯU Ý BẢO MẬT: Một sinh viên chỉ được phép tra cứu thông tin của chính mình.
        KHÔNG dùng để tra cứu thông tin của sinh viên khác.

    Input Schema:
        target_student_id (str): Mã sinh viên cần tra cứu. Ví dụ: 'SV123', 'sv123'.

    Output Schema (Thành công):
        str: Chuỗi thông tin điểm số bao gồm GPA, danh sách môn đã đỗ và môn nợ.
             Ví dụ: "GPA: 3.2, Đã đỗ: Nhập môn Python. Nợ: Không."

    Error Semantics (Lỗi):
        str: Chuỗi bắt đầu bằng "LỖI" trong các trường hợp:
             - Không có quyền xem bảng điểm của sinh viên khác.
             - Mã sinh viên không tồn tại trong hệ thống.
             - Input rỗng hoặc không hợp lệ.
             → Không crash chương trình.

    Side Effect: Read-only — chỉ tra cứu, không thay đổi dữ liệu.

    Ví dụ hợp lệ:
        Input:  get_student_transcript("SV123")
        Output: "GPA: 3.2, Đã đỗ: Hệ quản trị cơ sở dữ liệu, Nhập môn Python, Cấu trúc dữ liệu. Nợ: Không."

    Safety: Bọc toàn bộ bằng try/except, validate input rỗng, không raise Exception.
    """
    try:
        # Validate input
        if not target_student_id or not isinstance(target_student_id, str):
            return "LỖI: Tham số 'target_student_id' không hợp lệ. Vui lòng cung cấp mã sinh viên hợp lệ (Ví dụ: 'SV123')."

        target_id = target_student_id.upper().strip()

        if not target_id:
            return "LỖI: Mã sinh viên không được để trống."

        # Cơ chế kiểm tra quyền truy cập (Authorization - Guardrail bảo mật)
        if target_id != CURRENT_LOGGED_IN_USER:
            return (
                f"LỖI TỪ CHỐI TRUY CẬP: Hệ thống ghi nhận bạn là {CURRENT_LOGGED_IN_USER}. "
                f"Bạn không có quyền xem bảng điểm của {target_id}. "
                f"Bạn chỉ có thể tra cứu bảng điểm của chính mình."
            )

        db = {
            "SV123": "GPA: 3.2, Đã đỗ: Hệ quản trị cơ sở dữ liệu, Nhập môn Python, Cấu trúc dữ liệu. Nợ: Không.",
            "SV456": "GPA: 2.8, Đã đỗ: Kỹ năng mềm. Nợ: Giải tích.",
        }

        return db.get(
            target_id,
            f"LỖI: Không tìm thấy dữ liệu cho mã sinh viên '{target_id}'. Vui lòng kiểm tra lại mã sinh viên.",
        )

    except Exception as e:
        return f"LỖI: Đã xảy ra lỗi không mong muốn khi tra cứu bảng điểm: {str(e)}."


# =============================================================================
# TOOL 2: search_course_catalog
# =============================================================================
def search_course_catalog(keyword: str) -> str:
    """
    Tra cứu chương trình học, số tín chỉ, yêu cầu môn tiên quyết.

    Mục đích (Purpose):
        Dùng khi người dùng muốn tìm hiểu về một môn học cụ thể: mô tả, tín chỉ, tiên quyết.
        KHÔNG dùng để tra cứu lịch học — dùng check_course_schedule cho mục đích đó.

    Input Schema:
        keyword (str): Mã môn hoặc tên môn (Ví dụ: 'IS201', 'Java', 'Machine Learning', 'Học máy').

    Output Schema (Thành công):
        str: Thông tin chi tiết môn học bao gồm tên, số tín chỉ, tiên quyết và nội dung.
             Ví dụ: "Môn: Học máy (DS301) - 4 tín chỉ. Tiên quyết: Xác suất thống kê."

    Error Semantics (Lỗi):
        str: Chuỗi bắt đầu bằng "LỖI:" khi không tìm thấy môn học hoặc input không hợp lệ.
             → Không crash chương trình.

    Side Effect: Read-only — chỉ tra cứu, không thay đổi dữ liệu.

    Ví dụ hợp lệ:
        Input:  search_course_catalog("DS301")
        Output: "Môn: Học máy (DS301) - 4 tín chỉ. Tiên quyết: Xác suất thống kê, Nhập môn Python."

    Safety: Bọc toàn bộ bằng try/except, validate input rỗng, không raise Exception.
    """
    try:
        # Validate input
        if not keyword or not isinstance(keyword, str):
            return "LỖI: Tham số 'keyword' không hợp lệ. Vui lòng cung cấp mã hoặc tên môn học (Ví dụ: 'IS201', 'Java')."

        keyword_lower = keyword.lower().strip()

        if not keyword_lower:
            return "LỖI: Từ khóa tìm kiếm không được để trống."

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
            return (
                f"LỖI: Không tìm thấy môn học nào khớp với từ khóa '{keyword}' trong hệ thống đào tạo. "
                f"Các môn có sẵn: IS201 (Cơ sở dữ liệu), DS301 (Học máy), IT401 (Java)."
            )

    except Exception as e:
        return f"LỖI: Đã xảy ra lỗi không mong muốn khi tìm kiếm môn học '{keyword}': {str(e)}."


# =============================================================================
# TOOL 3: check_course_schedule
# =============================================================================
def check_course_schedule(course_code: str) -> str:
    """
    Kiểm tra lịch học, phòng học, giảng viên và số slot còn trống của lớp học phần.

    Mục đích (Purpose):
        Dùng khi người dùng muốn biết lịch học cụ thể, phòng và số slot trống.
        KHÔNG dùng để tìm mô tả môn học — dùng search_course_catalog cho mục đích đó.

    Input Schema:
        course_code (str): Mã môn học. Ví dụ: 'IS201', 'DS301', 'IT401'.

    Output Schema (Thành công):
        str: Thông tin lịch học bao gồm tên lớp, thời gian, phòng học,
             tên giảng viên và số slot còn trống.
             Ví dụ: "Lớp IS201-01: Sáng T3 (08:00 - 11:30), Phòng E402. Số slot còn trống: 5/40."

    Error Semantics (Lỗi):
        str: Chuỗi bắt đầu bằng "LỖI:" khi mã môn không tồn tại hoặc input không hợp lệ.
             → Không crash chương trình.

    Side Effect: Read-only — chỉ tra cứu, không thay đổi dữ liệu.

    Ví dụ hợp lệ:
        Input:  check_course_schedule("IS201")
        Output: "Lớp IS201-01: Sáng T3 (08:00 - 11:30), Phòng E402. Giảng viên: Trần Văn A. Số slot còn trống: 5/40."

    Safety: Bọc toàn bộ bằng try/except, validate input rỗng, không raise Exception.
    """
    try:
        # Validate input
        if not course_code or not isinstance(course_code, str):
            return "LỖI: Tham số 'course_code' không hợp lệ. Vui lòng cung cấp mã môn học (Ví dụ: 'IS201', 'DS301')."

        code_upper = course_code.upper().strip()

        if not code_upper:
            return "LỖI: Mã môn học không được để trống."

        schedule_db = {
            "IS201": "Lớp IS201-01: Sáng T3 (08:00 - 11:30), Phòng E402. Giảng viên: Trần Văn A. Số slot còn trống: 5/40.",
            "DS301": "Lớp DS301-02: Chiều T5 (13:30 - 17:00), Phòng Lab. Giảng viên: Nguyễn Thị B. Số slot còn trống: 0/30 (Đã đầy).",
            "IT401": "Lớp IT401-01: Sáng T2 (08:00 - 11:30), Phòng E403. Giảng viên: Lê Văn C. Số slot còn trống: 12/40.",
        }

        if code_upper in schedule_db:
            return schedule_db[code_upper]

        return (
            f"LỖI: Không có lịch học nào được xếp cho mã môn '{code_upper}' trong học kỳ này. "
            f"Các mã môn có lịch: IS201, DS301, IT401."
        )

    except Exception as e:
        return f"LỖI: Đã xảy ra lỗi không mong muốn khi kiểm tra lịch học cho '{course_code}': {str(e)}."


AVAILABLE_TOOLS = {
    "get_student_transcript": get_student_transcript,
    "search_course_catalog": search_course_catalog,
    "check_course_schedule": check_course_schedule,
}

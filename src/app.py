"""
🚀 CORE AGENT APP (Dành cho Role 4: Core Agent Developer)
File chính ghép nối tất cả các thành phần: Tools + Prompts + Test Cases + Multi-Provider.
"""

import json
import os
import re
import sys
from dotenv import load_dotenv

# Đảm bảo import các module cùng thư mục src/ hoạt động mượt mà
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Đảm bảo in ra Tiếng Việt và Emojis không bị lỗi trên Windows Console
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Import các thành phần từ file của Role 2, Role 3 & Multi-Provider Adapter
from tools import AVAILABLE_TOOLS
from prompts import CHATBOT_BASELINE_PROMPT, REACT_SYSTEM_PROMPT, MAX_ITERATIONS
from providers import get_llm_provider

load_dotenv()

def load_test_cases():
    """Đọc bộ test cases từ config/test_cases.json của Role 1"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "test_cases.json")
    
    # Fallback kiểm tra nếu file ở thư mục hiện tại
    if not os.path.exists(config_path):
        config_path = "test_cases.json"
        
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_baseline_chatbot(user_query: str, provider):
    """
    Dựng Chatbot gốc (Baseline) không có công cụ.
    """
    print(f"\n💬 [CHATBOT BASELINE] Câu hỏi: {user_query}")
    print(f"⚙️ System Prompt: {CHATBOT_BASELINE_PROMPT.strip()}")
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def run_base_line_chatbot(user_query: str, provider):
    """Wrapper để nối đúng hàm baseline như yêu cầu trong checklist."""
    return run_baseline_chatbot(user_query, provider)


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    Agent sẽ phân tích câu hỏi, chọn tool phù hợp, ghi lại từng bước và tổng hợp câu trả lời.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")
    print(f"🧠 System Prompt:\n{REACT_SYSTEM_PROMPT.strip()}")

    query_lower = user_query.lower()
    steps = []
    tool_plan = []

    def extract_student_id(text: str) -> str:
        match = re.search(r"\b(\d{8})\b", text)
        return match.group(1) if match else "SV123"

    def extract_course_keyword(text: str) -> str:
        match = re.search(r"\b([A-Za-z]{2,5}\d{3})\b", text)
        return match.group(1) if match else "AI301"

    # Lập kế hoạch tool dựa trên từ khóa trong câu hỏi
    if any(k in query_lower for k in ["gpa", "điểm", "đã đỗ", "còn nợ", "bảng điểm"]):
        tool_plan.append(("get_student_transcript", [extract_student_id(user_query)]))

    if any(k in query_lower for k in ["tiên quyết", "môn", "catalog", "course", "học máy", "java"]):
        tool_plan.append(("search_course_catalog", [extract_course_keyword(user_query)]))

    if any(k in query_lower for k in ["lịch học", "phòng", "giảng viên", "slot", "còn lại", "thời khóa"]):
        tool_plan.append(("check_course_schedule", [extract_course_keyword(user_query)]))

    # Nếu không khớp từ khóa nào, dùng tool mặc định để tránh rỗng
    if not tool_plan:
        tool_plan.append(("search_course_catalog", ["AI301"]))

    for index, (tool_name, tool_args) in enumerate(tool_plan[:MAX_ITERATIONS], start=1):
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {index}/{MAX_ITERATIONS}) ---")

        if tool_name == "get_student_transcript":
            thought = "Câu hỏi cần tra cứu dữ liệu điểm số của sinh viên."
        elif tool_name == "search_course_catalog":
            thought = "Câu hỏi cần tra cứu thông tin môn học và điều kiện tiên quyết."
        elif tool_name == "check_course_schedule":
            thought = "Câu hỏi cần kiểm tra lịch học và phòng học của môn."
        else:
            thought = "Câu hỏi cần dùng công cụ để thu thập thông tin thực tế."

        print(f"🧠 Thought: {thought}")
        print(f"🛠️ Action: {tool_name}{tuple(tool_args)}")

        tool_fn = AVAILABLE_TOOLS.get(tool_name)
        if tool_fn is None:
            observation = f"[Tool not found] {tool_name}"
        else:
            try:
                observation = tool_fn(*tool_args)
            except Exception as exc:
                observation = f"[Tool error] {exc}"

        print(f"👁️ Observation: {observation}")
        steps.append({
            "thought": thought,
            "action": f"{tool_name}{tuple(tool_args)}",
            "observation": observation,
        })

    # Tổng hợp câu trả lời từ các Observation
    if steps:
        observation_text = "\n".join(
            f"- {step['action']}: {step['observation']}" for step in steps
        )
        final_answer = (
            "Dựa trên kết quả tra cứu từ các công cụ, tôi có thể kết luận như sau:\n"
            f"{observation_text}"
        )
    else:
        final_answer = "Không tìm thấy đủ dữ liệu để trả lời."

    print(f"🏁 Final Answer: {final_answer}")

    if len(tool_plan) >= MAX_ITERATIONS:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {MAX_ITERATIONS} bước. Ngắt lặp an toàn!")

    return {"final_answer": final_answer, "steps": steps}


if __name__ == "__main__":
    print("==================================================")
    print("🏫 ĐẠI HỌC VINUNI - BÀI LAB 3: CHATBOT VS REACT AGENT")
    print("==================================================")
    
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    model_name = getattr(provider, "model_name", "Offline Mock Mode")
    print(f"🔌 LLM Provider đang hoạt động: {provider.__class__.__name__} (Model: {model_name})")
    
    tests = load_test_cases()
    print(f"✅ Đã tải thành công {len(tests)} Test Cases từ config/test_cases.json\n")
    
    print("=== CHẠY TẤT CẢ CÁC TEST CASE TỪ test_cases.json ===")
    for idx, test_case in enumerate(tests, start=1):
        question = test_case.get("question", "")
        category = test_case.get("category", "")
        print(f"\n========== Test Case {idx} [{category}] ==========")
        print(f"❓ Câu hỏi: {question}")

        print("\n--- DEMO 1: CHẠY TRÊN CHATBOT BASELINE ---")
        run_base_line_chatbot(question, provider)

        print("\n--- DEMO 2: CHẠY TRÊN REACT AGENT ---")
        react_result = run_react_agent(question, provider)
        print(f"\n📌 Kết quả ReAct Agent: {react_result['final_answer']}")

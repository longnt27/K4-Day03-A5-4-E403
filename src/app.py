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
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print("* **Phản hồi**:")
    print(response)
    return response


def run_base_line_chatbot(user_query: str, provider):
    """Wrapper để nối đúng hàm baseline như yêu cầu trong checklist."""
    return run_baseline_chatbot(user_query, provider)


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent (Thought -> Action -> Observation) có Guardrails.
    Agent sẽ phân tích câu hỏi, chọn tool phù hợp, ghi lại từng bước và tổng hợp câu trả lời.
    """
    steps = []
    max_iterations = MAX_ITERATIONS
    final_answer = ""

    def format_action(tool_name: str, tool_args: list[str]) -> str:
        return f"{tool_name}[{', '.join(tool_args)}]"

    def build_react_prompt() -> str:
        prompt_parts = [
            f"Câu hỏi gốc của người dùng: {user_query}",
            "Lịch sử ReAct cho đến hiện tại:",
        ]
        if steps:
            for idx, step in enumerate(steps, start=1):
                prompt_parts.extend([
                    f"Thought {idx}: {step['thought']}",
                    f"Action {idx}: {step['action']}",
                    f"Observation {idx}: {step['observation']}",
                ])
        else:
            prompt_parts.append("(Chưa có bước nào.)")

        prompt_parts.extend([
            "",
            "Hãy quyết định bước tiếp theo dựa trên toàn bộ lịch sử ở trên.",
            "Nếu cần thêm dữ liệu, chỉ trả về đúng một bước:",
            "Thought: <suy luận ngắn gọn>",
            "Action: tên_công_cụ[tham_số]",
            "Nếu đã đủ dữ liệu hoặc gặp lỗi không thể tiếp tục an toàn, trả về:",
            "Thought: Tôi đã có đủ thông tin để trả lời.",
            "Final Answer: <câu trả lời tự nhiên>",
            "Không lặp lại Action đã gọi trước đó nếu Observation của Action đó đã có trong lịch sử.",
        ])
        return "\n".join(prompt_parts)

    def parse_action(response_text: str):
        action_line = None
        for line in response_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("Action:"):
                action_line = stripped[len("Action:"):].strip()
                break
        if not action_line:
            return None, None

    def extract_course_keyword(text: str) -> str:
        match = re.search(r"\b([A-Za-z]{2,5}\d{3})\b", text)
        return match.group(1) if match else "AI301"

    # Lập kế hoạch tool dựa trên từ khóa trong câu hỏi
    if any(k in query_lower for k in ["gpa", "điểm", "đã đỗ", "còn nợ", "bảng điểm"]):
        tool_plan.append(("get_student_transcript", [extract_student_id(user_query)]))

    if any(k in query_lower for k in ["tiên quyết", "môn", "catalog", "course", "học máy", "java"]):
        tool_plan.append(("search_course_catalog", [extract_course_keyword(user_query)]))

    for step_index in range(1, max_iterations + 1):
        react_prompt = build_react_prompt()
        response = provider.generate(react_prompt, system_prompt=REACT_SYSTEM_PROMPT).strip()

        if "Final Answer:" in response:
            thought_line = next((line for line in response.splitlines() if line.strip().startswith("Thought:")), "")
            if thought_line:
                thought = thought_line.split(":", 1)[1].strip()
                print(f"* **Thought {step_index}**: {thought}")
            final_answer = response.split("Final Answer:", 1)[1].strip()
            break

        thought_line = next((line for line in response.splitlines() if line.strip().startswith("Thought:")), "")
        thought = thought_line.split(":", 1)[1].strip() if thought_line else "Không có suy luận rõ ràng"

        tool_name, tool_args = parse_action(response)
        if not tool_name:
            final_answer = response
            break

        action = format_action(tool_name, tool_args)
        if any(step["action"] == action for step in steps):
            final_answer = (
                "Tôi đã tra cứu thông tin này nhưng chưa thể tiến thêm bằng một công cụ mới. "
                "Bạn vui lòng kiểm tra lại yêu cầu hoặc cung cấp thêm thông tin cụ thể hơn."
            )
            break

        if tool_name not in AVAILABLE_TOOLS:
            final_answer = (
                "Hiện hệ thống chỉ hỗ trợ tra cứu bảng điểm, thông tin môn học và lịch học. "
                "Tôi không thể thực hiện công cụ hoặc thao tác mà hệ thống không cung cấp."
            )
            break
        else:
            thought = "Câu hỏi cần dùng công cụ để thu thập thông tin thực tế."

        print(f"* **Thought {step_index}**: {thought}")
        print(f"* **Action {step_index}**: `{action}`")
        print(f"* **Observation {step_index}**: `{observation}`")
        steps.append({
            "thought": thought,
            "action": action,
            "observation": observation,
        })

    # Tổng hợp câu trả lời từ các Observation bằng LLM thực tế
    if steps:
        trace_text = "\n\n".join(
            f"Thought: {step['thought']}\nAction: {step['action']}\nObservation: {step['observation']}"
            for step in steps
        )
        synthesis_prompt = (
            f"Câu hỏi của người dùng: {user_query}\n\n"
            "Hãy sử dụng chuỗi Thought -> Action -> Observation sau để trả lời câu hỏi một cách tự nhiên bằng tiếng Việt.\n"
            "Đừng liệt kê các bước công cụ. Hãy trả lời như một trợ lý hữu ích, ngắn gọn và rõ ràng.\n\n"
            f"Trace:\n{trace_text}"
        )
        try:
            final_answer = provider.generate(synthesis_prompt, system_prompt=REACT_SYSTEM_PROMPT).strip()
        except Exception as exc:
            final_answer = f"Tôi chưa nhận được câu trả lời từ mô hình: {exc}"
    else:
        final_answer = "Hiện tại tôi chưa thu thập đủ dữ liệu để trả lời một cách chắc chắn."

    print(f"* **Final Answer**: *\"{final_answer}\"*")

    if step_index > max_iterations:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {max_iterations} bước. Ngắt lặp an toàn!")

    return {"final_answer": final_answer, "steps": steps}


if __name__ == "__main__":
    # Khởi tạo Multi-Provider LLM Adapter (Đọc từ biến môi trường LLM_PROVIDER)
    provider = get_llm_provider()
    
    tests = load_test_cases()
    
    for idx, test_case in enumerate(tests, start=1):
        question = test_case.get("question", "")
        print(f"\n**Câu hỏi {idx}**: {question}")
        print("\n### 🤖 Chatbot Baseline:")
        run_base_line_chatbot(question, provider)

        print("### 🧠 ReAct Agent:")
        run_react_agent(question, provider)

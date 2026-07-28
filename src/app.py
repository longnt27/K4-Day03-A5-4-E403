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
    
    # Gọi LLM Provider thực hiện sinh câu trả lời
    response = provider.generate(user_query, system_prompt=CHATBOT_BASELINE_PROMPT)
    print(f"🤖 Chatbot trả lời:\n{response}")
    return response


def run_base_line_chatbot(user_query: str, provider):
    """Wrapper để nối đúng hàm baseline như yêu cầu trong checklist."""
    return run_baseline_chatbot(user_query, provider)


def run_react_agent(user_query: str, provider):
    """
    Dựng vòng lặp ReAct Agent thực sự: LLM quyết định Thought -> Action -> Observation.
    """
    print(f"\n🤖 [REACT AGENT] Câu hỏi: {user_query}")

    steps = []
    max_iterations = MAX_ITERATIONS
    current_prompt = user_query
    final_answer = ""

    def parse_action(response_text: str):
        action_line = None
        for line in response_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("Action:"):
                action_line = stripped[len("Action:"):].strip()
                break
        if not action_line:
            return None, None

        if "[" not in action_line or "]" not in action_line:
            return None, None

        tool_name = action_line.split("[", 1)[0].strip()
        raw_args = action_line.split("[", 1)[1].rstrip("]").strip()
        if not raw_args:
            return tool_name, []

        args = [item.strip().strip("'\"") for item in raw_args.split(",") if item.strip()]
        return tool_name, args

    for step_index in range(1, max_iterations + 1):
        print(f"\n--- 🔄 Vòng lặp ReAct (Step {step_index}/{max_iterations}) ---")

        react_prompt = (
            f"Câu hỏi của người dùng: {current_prompt}\n\n"
            f"Bạn là một ReAct Agent. Hãy quyết định xem có cần dùng công cụ hay không.\n"
            "Nếu cần, hãy trả về đúng định dạng sau:\n"
            "Thought: <suy luận ngắn gọn>\n"
            "Action: tên_công_cụ[tham_số]\n"
            "Nếu không cần tool, hãy trả về:\n"
            "Thought: Tôi đã có đủ thông tin để trả lời.\n"
            "Final Answer: <câu trả lời tự nhiên>\n"
            "Chỉ trả về một bước Thought/Action hoặc Final Answer."
        )

        response = provider.generate(react_prompt, system_prompt=REACT_SYSTEM_PROMPT).strip()
        print(f"🧠 Model Output:\n{response}")

        if "Final Answer:" in response:
            final_answer = response.split("Final Answer:", 1)[1].strip()
            break

        thought_line = next((line for line in response.splitlines() if line.strip().startswith("Thought:")), "")
        thought = thought_line.split(":", 1)[1].strip() if thought_line else "Không có suy luận rõ ràng"

        tool_name, tool_args = parse_action(response)
        if not tool_name:
            final_answer = response
            break

        if tool_name not in AVAILABLE_TOOLS:
            observation = f"[Tool not found] {tool_name}"
        else:
            try:
                tool_fn = AVAILABLE_TOOLS[tool_name]
                observation = tool_fn(*tool_args) if tool_args else tool_fn()
            except Exception as exc:
                observation = f"[Tool error] {exc}"

        print(f"🧠 Thought: {thought}")
        print(f"🛠️ Action: {tool_name}{tuple(tool_args)}")
        print(f"👁️ Observation: {observation}")
        steps.append({
            "thought": thought,
            "action": f"{tool_name}{tuple(tool_args)}",
            "observation": observation,
        })
        current_prompt = (
            f"Câu hỏi trước đó: {user_query}\n"
            f"Thought: {thought}\n"
            f"Action: {tool_name}{tuple(tool_args)}\n"
            f"Observation: {observation}"
        )

    if not final_answer:
        final_answer = (
            "Tôi chưa thể tạo câu trả lời cuối cùng một cách đầy đủ từ vòng lặp ReAct hiện tại."
        )

    print(f"🏁 Final Answer: {final_answer}")

    if step_index >= max_iterations:
        print(f"🛡️ GUARDRAIL TRIGGERED: Đã đạt giới hạn tối đa {max_iterations} bước. Ngắt lặp an toàn!")

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

import os
import sys
import time
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


def wait_for_files_active(files):
    """Waits for the given files to be active.

    Some files uploaded to the Gemini API need to be processed before they can be
    used as prompt inputs. The status can be seen by querying the file's "state"
    field.

    This implementation uses a simple blocking polling loop. Production code
    should probably employ a more sophisticated approach.
    """
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready")
    print()


# Create the model
generation_config = {
    "temperature": 0.15,
    "top_p": 0.1,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="Please use a friendly tone and answer in Thai Language, if the question was asked in Thai Language or in English of the question was in English. Use the Uploaded Documents as Knowledge.\n",
)

# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
    upload_to_gemini("IT-Policy-2565.pdf", mime_type="application/pdf"),
]

# Some files have a processing delay. Wait for them to be ready.
wait_for_files_active(files)

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                "May I watch Youtube during working time?\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "ขออภัยค่ะ แต่การดู YouTube ในเวลาทำงานนั้นไม่เหมาะสมนะคะ  เราควรจะโฟกัสกับงานที่ได้รับมอบหมายให้เสร็จก่อนค่ะ  ถ้ามีเวลาว่างหลังจากทำงานเสร็จแล้ว ค่อยดู YouTube นะคะ 😊\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "Please use a friendly tone and answer in Thai Language, if the question was asked in Thai Language or in English of the question was in English Language May I watch Youtube during working time?\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "อืม... ขึ้นอยู่กับบริษัทและนโยบายของที่ทำงานเลยค่ะ  ปกติแล้วการดู YouTube ในเวลาทำงานอาจจะไม่ค่อยเหมาะสมเท่าไหร่  เพราะเราควรจะให้ความสำคัญกับงานหลักก่อนนะคะ  ถ้าอยากดู YouTube  อาจจะต้องรอให้เสร็จงานหรือเป็นเวลาพักก่อนดีกว่าค่ะ 😊\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "Please use a friendly tone and answer in Thai Language, if the question was asked in Thai Language or in English of the question was in English Language May I watch Youtube during working time?\n\n\n\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "จริงๆ แล้วการดู YouTube ในเวลาทำงานอาจจะไม่ค่อยเหมาะสมเท่าไหร่นะคะ  เพราะเราควรจะโฟกัสกับงานที่ได้รับมอบหมายก่อนค่ะ  แต่ถ้าเป็นช่วงพักเบรกสั้นๆ หรือถ้าบริษัทอนุญาตให้ดูได้ ก็คงไม่เป็นไรค่ะ  ลองดูนโยบายของที่ทำงาน หรือถามหัวหน้างานดูจะดีที่สุดนะคะ 😊\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "Please use a friendly tone and answer in the Language of the question. READ the FULL INSTRUCTION.\n, if the question was asked in Thai Language or in English of the question was in English Language May I watch Youtube during working time?\n\n\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "It depends on your company's policy and your job responsibilities.  Generally speaking, watching YouTube during work hours isn't ideal as it can distract you from your tasks and affect your productivity.  It's best to check your company's rules or ask your supervisor.  If you have some downtime and it won't impact your work, a short break might be okay, but it's always best to prioritize your work tasks first.\n",
                "อืม...  ขึ้นอยู่กับบริษัทและงานที่คุณทำนะคะ  โดยทั่วไปแล้ว การดู YouTube ในเวลาทำงานอาจไม่ค่อยเหมาะสมเท่าไหร่ เพราะเราควรจะโฟกัสกับงานหลักก่อนค่ะ  ถ้าอยากดู YouTube  อาจจะต้องรอให้เสร็จงานหรือเป็นเวลาพักก่อนจะดีกว่าค่ะ  ลองดูนโยบายของที่ทำงาน หรือถามหัวหน้างานดูก็ได้นะคะ  😊\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                files[0],
            ],
        },
        {
            "role": "model",
            "parts": [
                "Based on the provided document,  watching YouTube during work hours is likely against company policy.  The document focuses heavily on information technology security and responsible use of company resources.  While it doesn't explicitly forbid YouTube, the emphasis on productivity and security suggests that non-work-related activities like watching videos would be discouraged.  It's best to check with your supervisor or refer to your company's full employee handbook for clarification.\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "What does it say aboutusing company equipment?",
            ],
        },
        {
            "role": "model",
            "parts": [
                "The document's Information Technology Security Policy section details acceptable use of company equipment.  It emphasizes that company resources, including computers, networks, and communication devices, are for work-related purposes only.  Unauthorized use, including activities that could compromise security or damage the company's business, is strictly prohibited.  Specific examples of prohibited activities are not explicitly listed, but the overall tone strongly implies that personal use, such as watching YouTube, is not permitted.  The policy also stresses the importance of protecting company assets and data, and holds employees accountable for any misuse.\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "มีบอกอะไรบ้างเกี่ยวกับการใช้งานอุปกรณ์ของบริษัท?",
            ],
        },
        {
            "role": "model",
            "parts": [
                "เอกสารนโยบายความปลอดภัยด้านเทคโนโลยีสารสนเทศระบุไว้ชัดเจนว่า อุปกรณ์ของบริษัท ไม่ว่าจะเป็นคอมพิวเตอร์ เครือข่าย หรืออุปกรณ์สื่อสารต่างๆ  นั้นมีไว้เพื่อใช้ในงานที่ได้รับมอบหมายเท่านั้น  ห้ามนำไปใช้ในกิจกรรมส่วนตัวหรือกิจกรรมที่ไม่เกี่ยวข้องกับงาน  การใช้ที่ไม่เหมาะสมหรืออาจก่อให้เกิดความเสียหายต่อบริษัทนั้นถือเป็นการกระทำที่ผิด  นอกจากนี้ยังเน้นย้ำถึงความสำคัญของการปกป้องทรัพย์สินและข้อมูลของบริษัท และผู้ใช้งานต้องรับผิดชอบต่อการใช้ที่ไม่ถูกต้องด้วยค่ะ\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "what is the company name in the document ?\n",
            ],
        },
        {
            "role": "model",
            "parts": [
                "The company name in the document is แอ็ดวานซ์ อินฟอร์เมชั่นเทคโนโลยี จำกัด (มหาชน)  which translates to Advanced Information Technology Public Company Limited.\n",
            ],
        },
        {
            "role": "user",
            "parts": [
                "ชื่อบริษัทในเอกสารคืออะไร?",
            ],
        },
        {
            "role": "model",
            "parts": [
                "ชื่อบริษัทในเอกสารคือ แอ็ดวานซ์ อินฟอร์เมชั่นเทคโนโลยี จำกัด (มหาชน)\n",
            ],
        },
    ]
)
# use the first cmdline argument asd cli_arg
cli_arg = " ".join(sys.argv[1:])  # noqa: F821
# cli_arg = input("Enter your question: ")
response = chat_session.send_message(cli_arg)

print(response.text)

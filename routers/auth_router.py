import requests
from fastapi import FastAPI, APIRouter
from controller.auth_controller import get_generate_qrcode, get_callback, get_active_by_state, get_token_viewer, get_province
from models.auth_model import AuthBase, ViewerBase

router = APIRouter(tags=["authentication"])


@router.get("/")
async def read_root():
    return {"message": "Hello, World"}


@router.post("/gen_qrcode/")
async def generate_qrcode(request_token: AuthBase, state: str = None):
    return get_generate_qrcode(request_token, state)


@router.get("/callback/")
async def callback(code: str = None, state: str = None):
    return get_callback(code, state)


@router.post("/active/")
async def read_active_by_state(request_token: AuthBase, state: str = None):
    return get_active_by_state(request_token, state)


@router.post("/viewer/")
async def read_token_viewer(request_viewer: ViewerBase):
    return get_token_viewer(request_viewer)


@router.post("/province/")
async def read_province(request_token: AuthBase):
    return get_province(request_token)


@router.get("/policy/")
async def read_policy():
    return {"title": "เงื่อนไขบริการ (Policy)",
            "content": "การยืนยันตัวตนเพื่อเข้าใช้งานระบบของเว็บไซต์ของสำนักงานสาธารณสุขจังหวัดเชียงใหม่ ภายใต้ชื่อโดนเมน <br>"
                       "*.chiangmaihealth.go.th และชื่อโดเมน *.cmhis.org <br>"
                       "โดยการยืนยันตัวตนนี้เป็นเพียงอีกวิธีหนึ่งในการพิสูจน์ตัวบุคคลเท่านั้น โดยยังมีวิธีในการพิสูจน์ตัวบุคคลอื่นๆ อีกที่สามารถทำได้ เช่น การเข้าใช้งานด้วย username และ password และสิทธิการเข้าใช้งาน <br>"
                       "การยืนยันตัวตนนี้จะเป็นการยืนยันตัวตนกับแอพพลิเคชั่น ThaiD ของกรมการปกครอง <br>"
                       "โดยผู้ใช้งานจะต้องเข้าใจและยอมรับข้อกำหนดและเงื่อนไขการใช้งาน ของสำนักงานสาธารณสุขจังหวัดเชียงใหม่ <br>"
            }


@router.get("/termsofuser/")
async def read_term_of_user():
    return {"title": "ข้อกำหนดผู้ใช้งาน (Term of User)",
            "content": "การยืนยันตัวตนเพื่อเข้าใช้งานระบบของเว็บไซต์ของสำนักงานสาธารณสุขจังหวัดเชียงใหม่ ภายใต้ชื่อโดนเมน <br>"
                       "*.chiangmaihealth.go.th และชื่อโดเมน *.cmhis.org โดยมีวัตถุประสงค์เพื่อเป็นการยืนยันตัวตนเพื่อเข้าใช้งานระบบสารสนเทศภายใต้ชื่อโดเมนดังกล่าว <br>"
                       " โดยผู้ใช้งานจะต้องเข้าใจและยอมรับข้อกำหนดและเงื่อนไขการใช้งานดังต่อไปนี้ โดยเว็บไซต์ของสำนักงานสาธารณสุขจังหวัดเชียงใหม่ <br>"
                       " จะมีการเปลี่ยนแปลงข้อกำหนดและเงื่อนไขการใช้งานได้โดยไม่ต้องแจ้งให้ทราบล่วงหน้า ดังนั้นผู้ใช้งานควรตรวจสอบข้อกำหนดและเงื่อนไขการใช้งานเป็นประจำ <br>"
                       " หากผู้ใช้งานไม่ยอมรับข้อกำหนดและเงื่อนไขการใช้งาน ผู้ใช้งานควรหยุดใช้งานระบบทันที และหากผู้ใช้งานยอมรับข้อกำหนดและเงื่อนไขการใช้งาน <br>"
                       " ผู้ใช้งานจะต้องปฏิบัติตามข้อกำหนดและเงื่อนไขการใช้งานต่อไปนี้ <br>"
                       " 1. ผู้ใช้งานจะต้องเป็นเจ้าหน้าที่ของสำนักงานสาธารณสุขจังหวัดเชียงใหม่ หรือเจ้าหน้าที่ของหน่วยงานที่เกี่ยวข้อง ที่ได้มีการลงทะเบียนเข้าใช้งานระบบไว้แล้ว <br>"
                       " 2. ผู้ใช้งานจะต้องเป็นผู้ที่ได้รับอนุญาตให้เข้าใช้งานระบบ โดยผู้ใช้งานจะต้องเป็นผู้ที่ได้รับอนุญาตจากผู้ดูแลระบบหรือผู้ที่ได้รับมอบหมายให้ใช้งานระบบ <br>"
                       " 3. ผู้ใช้งานจะต้องมีการยืนยันตัวตนกับแอพพลิเคชั่น ThaiD ของกรมการปกครอง <br>"
                       " 4. การยืนยันตัวตนจะเป็นการยืนยันกับระบบ ThaiD และเมื่อผู้ใช้งานยืนยันตัวตนเรียบร้อยแล้ว ระบบจะทำการส่งข้อมูลการยืนยันตัวตนกลับมายังระบบของสำนักงานสาธารณสุขจังหวัดเชียงใหม่ ประกอบด้วย ชื่อ-สกุล และเลขประจำตัวประชาชนของผู้ยืนยัน <br>"
                       " 5. ระบบของสำนักงานฯ จะทำการตรวจสอบข้อมูลการยืนยันตัวตนกับระบบ ThaiD ว่าตรงกับข้อมูลที่สำนักงานสาธารณสุขจังหวัดเชียงใหม่ ได้ลงทะเบียนเพื่อใช้งานระบบของสำนักงานฯ ไว้หรือไม่ <br>"
                       " 6. ระบบของสำนักงานฯ จะนำข้อมูลที่ได้คืน (Call back) มาจากระบบ ThaiD มาเพื่อเปรียบเทียบความถูกต้องเท่านั้น จะไม่เก็บข้อมูลที่ได้รับคืนมานั้นไว้ในระบบ  <br>"}

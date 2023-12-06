from fastapi import APIRouter, Request
from controller.auth_controller import get_generate_qrcode, get_callback, get_active_by_state, get_token_viewer, \
    get_province, get_hosname, get_script_provider, get_province_code, get_client, get_active_by_client_id, post_version
from models.auth_model import AuthBase, ViewerBase, RegBase
import controller.auth_controller as auth_controller


router = APIRouter(tags=["authentication"])


@router.post("/register/")
async def check_register(req: RegBase):
    return auth_controller.check_register(req)


@router.get("/client/")
async def read_client(request: Request):
    return auth_controller.get_client(request)


@router.post("/gen_qrcode/")
async def generate_qrcode(request_token: AuthBase, state: str = None):
    return get_generate_qrcode(request_token, state)


@router.get("/callback/")
async def callback(code: str = None, state: str = None):
    return get_callback(code, state)


@router.post("/active/")
async def check_active_by_state(request_token: AuthBase, state: str = None):
    return get_active_by_state(request_token, state)


@router.post("/active_by_id/")
async def check_active_by_client_id(request_token: AuthBase, client_id: str = None):
    return get_active_by_client_id(request_token, client_id)


@router.post("/viewer/")
async def get_token_for_viewer(request_viewer: ViewerBase):
    return get_token_viewer(request_viewer)


router2 = APIRouter(tags=["lookup table"])


@router2.post("/province/")
async def read_province_list(request_token: AuthBase):
    return get_province(request_token)


@router2.get("/hoscode/")
async def read_hosname_by_hoscode(hoscode: str):
    return get_hosname(hoscode)


@router2.get("/hoscode_all/")
async def read_hosname_all():
    return auth_controller.get_hosname_all()


@router2.post("/script_provider/")
async def read_script_provider(request_token: AuthBase):
    return get_script_provider(request_token)


@router2.get("/province_code/")
async def read_province_code():
    return get_province_code()


@router2.post("/version/")
async def read_version(request_token: AuthBase):
    return post_version(request_token)


router3 = APIRouter(tags=["policy"])


@router3.get("/policy/")
async def read_policy():
    return {"title": "เงื่อนไขบริการ (Policy)",
            "content": "การยืนยันตัวตนเพื่อเข้าใช้งานระบบของเว็บไซต์ของสำนักงานสาธารณสุขจังหวัดเชียงใหม่ ภายใต้ชื่อโดนเมน <br>"
                       "*.chiangmaihealth.go.th และชื่อโดเมน *.cmhis.org <br>"
                       "โดยการยืนยันตัวตนนี้เป็นเพียงอีกวิธีหนึ่งในการพิสูจน์ตัวบุคคลเท่านั้น โดยยังมีวิธีในการพิสูจน์ตัวบุคคลอื่นๆ อีกที่สามารถทำได้ เช่น การเข้าใช้งานด้วย username และ password และสิทธิการเข้าใช้งาน <br>"
                       "การยืนยันตัวตนนี้จะเป็นการยืนยันตัวตนกับแอพพลิเคชั่น ThaiD ของกรมการปกครอง <br>"
                       "โดยผู้ใช้งานจะต้องเข้าใจและยอมรับข้อกำหนดและเงื่อนไขการใช้งาน ของสำนักงานสาธารณสุขจังหวัดเชียงใหม่ <br>"
            }


@router3.get("/termsofuser/")
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

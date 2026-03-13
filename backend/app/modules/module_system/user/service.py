from backend.app.common.core.exceptions import CustomException
from backend.app.common.utils.hash_bcrpy_util import PwdUtil
from backend.app.modules.module_system.auth.schema import AuthSchema
from backend.app.modules.module_system.user.crud import UserCRUD
from backend.app.modules.module_system.user.schema import UserRegisterSchema, UserOutSchema


class UserService:

    # @classmethod
    # async def get_current_user_info_service(cls) -> dict:
    #     user = UserModel(
    #         username="test",
    #         email="test@example",
    #         gender="男",
    #         is_superuser=False,
    #     )

    @classmethod
    async def register_user_service(cls, auth: AuthSchema, data: UserRegisterSchema) -> dict:
        """
        用户注册

        参数:
        - auth (AuthSchema): 认证信息模型
        - data (UserRegisterSchema): 用户注册数据

        返回:
        - Dict: 注册后的用户详情字典
        """
        # 检查用户名是否存在
        #TODO 提取数据库中，若是存在，则用户已经注册
        if not data.mobile and not data.email:
            raise CustomException(msg="手机号和邮箱不能同时为空")


        user_ok = None

        if data.mobile:
            user_ok = await UserCRUD(auth).get_by_mobile_crud(mobile=data.mobile)
        elif data.email:
            user_ok = await UserCRUD(auth).get_by_email_crud(email=data.email)

        if user_ok:
            raise CustomException(msg='账号已存在')

        #data.password是 传入的明文密码，随后hash加密再赋值给data，设置data
        data.password = PwdUtil.set_password_hash(data.password)
        #name是选填项，username是必填项，注册时直接复制
        data.name = data.username
        #model_dump是pydanticv2将pydantic模型转换为Python字典的方法
        #exclude_unset=True标识只包含用户实际提交的字段

        #exclude是主动剔除指定字段
        create_dict = data.model_dump(exclude_unset=True,exclude={"role_ids","dept_ids"})

        #设置默认用户类型为普通用户
        # create_dict.setdefault("user_type","0")

        #设置创建人ID
        if auth.user and auth.user.id:
            create_dict["created_id"] = auth.user.id

        result = await UserCRUD(auth).create(data=create_dict)

        # if data.role_ids:
        #     await UserCRUD(auth).set_user_roles_crud(user_ids=[result.id], role_ids=data.role_ids)
        return UserOutSchema.model_validate(result).model_dump()



from backend.app.modules.module_system.user.model import UserModel


class UserService:

    @classmethod
    async def get_current_user_info_service(cls) -> dict:

        user = UserModel(
            username="test",
            email="test@example",
            gender="男",
            is_superuser=False,
        )

